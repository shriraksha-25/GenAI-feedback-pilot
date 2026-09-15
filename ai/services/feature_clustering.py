"""
ai/services/feature_clustering.py
====================================
Groups semantically similar feature requests (extracted per-record by
the Feature Request Agent in ai.agents.crew) into broader feature
opportunities — e.g. "Add UPI payments", "Support Google Pay", and
"Give us more payment options" all grouping into one payment-related
opportunity.

WHY THIS IS A SEPARATE FUNCTION, NOT A FOURTH AGENT
-------------------------------------------------------
The Feature Request Agent (ai/agents/crew.py) only ever sees ONE piece
of feedback at a time — it has no visibility into other records to
group against. Clustering is inherently a BATCH operation across many
already-extracted feature requests, so it belongs here as a plain
utility function the backend (or a batch job) calls after collecting
several `analyze_feedback()` results, not as another CrewAI agent.

HOW SIMILARITY IS COMPUTED
------------------------------
Grouping requests like "Add UPI payments" and "Support Google Pay"
requires genuine semantic understanding — they share almost no
vocabulary, so keyword/TF-IDF overlap alone cannot group them
correctly (verified while building this: TF-IDF left every one of
those three example requests in its own singleton cluster). Real
embeddings are needed.

Rather than adding a new heavy local dependency (`sentence-transformers`
pulls in PyTorch — a multi-GB install that's overkill for a college
project already using CrewAI + a GenAI API), this module reuses
whichever GenAI provider is ALREADY configured for the three agents
(ai.agents.llm) and calls its embeddings endpoint directly:
  - OPENAI_API_KEY configured  -> OpenAI `text-embedding-3-small`
  - GEMINI_API_KEY configured  -> Gemini `gemini-embedding-001`
No new provider, no new API key, no new heavy dependency.

FALLBACK WHEN NO PROVIDER IS CONFIGURED
-------------------------------------------
If neither key is set (e.g. running Milestone 1-only, no AI configured
at all), this module falls back to local TF-IDF + cosine similarity
(scikit-learn, already a listed dependency, no network needed). This
keeps `cluster_feature_requests()` fully usable and testable offline,
at the cost of only catching lexically-similar requests (e.g. "Add
dark mode" / "Dark mode please") rather than fully cross-vocabulary
paraphrases — clearly logged when it happens, never silently degraded.

WHAT THIS DOES NOT DO
------------------------
It does not call an LLM to invent a pretty group name by default —
the group label defaults to the most representative member's own
text. If a GenAI provider is configured, `label_with_llm=True` will
ask it for a short, human-friendly group name as a labeling nicety
layered on top of the real clustering — never required for the
clustering itself to work or be tested.
"""

from __future__ import annotations

import logging
from typing import Optional, TypedDict

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ai.config.config import OPENAI_API_KEY, GEMINI_API_KEY

logger = logging.getLogger("ai.services.feature_clustering")

# Cosine DISTANCE (1 - similarity) below which two feature requests are
# considered part of the same cluster.
#   - With real embeddings, semantically related short phrases
#     typically land well under this even with zero shared words.
#   - With the TF-IDF fallback, this is tuned for short phrases so
#     requests need meaningfully overlapping wording to group.
DEFAULT_DISTANCE_THRESHOLD = 0.35


class FeatureRequestItem(TypedDict, total=False):
    feedback_id: Optional[str]
    feature_request: str


class ClusteredFeatureItem(TypedDict, total=False):
    feedback_id: Optional[str]
    feature_request: str
    feature_opportunity_group: str
    cluster_id: int


def cluster_feature_requests(
    items: list[FeatureRequestItem],
    distance_threshold: float = DEFAULT_DISTANCE_THRESHOLD,
    label_with_llm: bool = False,
) -> list[ClusteredFeatureItem]:
    """
    Group semantically similar feature requests together.

    Parameters
    ----------
    items:
        A list of dicts, each with at least a "feature_request" string
        (e.g. filtered from a batch of `analyze_feedback()` results
        where `feature_request` is not None). An optional
        "feedback_id" is carried through unchanged so the caller can
        map clusters back to source records.
    distance_threshold:
        Cosine-distance cutoff for merging two requests into the same
        cluster. Lower = stricter (fewer, tighter clusters).
    label_with_llm:
        If True AND a GenAI provider is configured, ask the LLM for a
        short, human-friendly name for each cluster (e.g. "Expanded
        Payment Options") instead of using the representative member's
        raw text. Falls back to the representative text silently if no
        provider is configured or the call fails.

    Returns
    -------
    The same items, each augmented with:
        - "feature_opportunity_group": the assigned group label
        - "cluster_id": an integer cluster index (stable within this
          call only — not a persistent ID across separate calls)

    Notes
    -----
    - 0 items -> returns [].
    - 1 item -> returns it as its own single-member cluster.
    - Items with empty/whitespace-only "feature_request" text are
      skipped (excluded from the returned list) rather than crashing
      the whole batch over one bad record.
    """
    usable = [it for it in items if it.get("feature_request") and it["feature_request"].strip()]
    if not usable:
        return []

    if len(usable) == 1:
        only = dict(usable[0])
        only["feature_opportunity_group"] = only["feature_request"]
        only["cluster_id"] = 0
        return [only]  # type: ignore[list-item]

    texts = [it["feature_request"].strip() for it in usable]
    vectors, method = _vectorize(texts)
    logger.info("Clustering %d feature requests using %s", len(texts), method)

    similarity = cosine_similarity(vectors)
    distance = np.clip(1 - similarity, 0, None)
    np.fill_diagonal(distance, 0.0)  # required for a valid precomputed distance matrix

    clustering = AgglomerativeClustering(
        n_clusters=None,
        metric="precomputed",
        linkage="average",
        distance_threshold=distance_threshold,
    )
    labels = clustering.fit_predict(distance)

    results: list[ClusteredFeatureItem] = []
    for cluster_id in sorted(set(labels)):
        member_indices = [i for i, lbl in enumerate(labels) if lbl == cluster_id]
        representative_text = _pick_representative(member_indices, similarity, texts)
        group_label = representative_text

        if label_with_llm:
            member_texts = [texts[i] for i in member_indices]
            llm_label = _try_llm_label(member_texts)
            if llm_label:
                group_label = llm_label

        for i in member_indices:
            item = dict(usable[i])
            item["feature_opportunity_group"] = group_label
            item["cluster_id"] = int(cluster_id)
            results.append(item)  # type: ignore[arg-type]

    return results


# ---------------------------------------------------------------------
# Vectorization: real embeddings when a provider is configured, TF-IDF
# fallback otherwise. Isolated here so this is the ONLY place that
# would need to change to add another embedding provider.
# ---------------------------------------------------------------------
def _vectorize(texts: list[str]) -> tuple[np.ndarray, str]:
    if OPENAI_API_KEY:
        vectors = _embed_with_openai(texts)
        if vectors is not None:
            return vectors, "openai-embeddings"
    if GEMINI_API_KEY:
        vectors = _embed_with_gemini(texts)
        if vectors is not None:
            return vectors, "gemini-embeddings"

    logger.info(
        "No GenAI provider configured (or embedding call failed) - falling back to "
        "local TF-IDF similarity. This groups lexically similar requests well, but "
        "may miss cross-vocabulary paraphrases (e.g. 'UPI payments' vs 'Google Pay')."
    )
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    return vectorizer.fit_transform(texts), "tfidf"


def _embed_with_openai(texts: list[str]) -> Optional[np.ndarray]:
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(model="text-embedding-3-small", input=texts)
        return np.array([d.embedding for d in response.data])
    except Exception:  # noqa: BLE001 - embeddings are best-effort; TF-IDF fallback always available
        logger.warning("OpenAI embedding call failed; falling back to TF-IDF.", exc_info=True)
        return None


def _embed_with_gemini(texts: list[str]) -> Optional[np.ndarray]:
    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.embed_content(model="gemini-embedding-001", contents=texts)
        return np.array([e.values for e in response.embeddings])
    except Exception:  # noqa: BLE001 - embeddings are best-effort; TF-IDF fallback always available
        logger.warning("Gemini embedding call failed; falling back to TF-IDF.", exc_info=True)
        return None


def _pick_representative(member_indices: list[int], similarity: np.ndarray, texts: list[str]) -> str:
    """
    Within a cluster, pick the member with the highest average
    similarity to the other members (the most "central"/typical
    phrasing) as the default group label, falling back to the
    shortest text on ties for a cleaner-looking label.
    """
    if len(member_indices) == 1:
        return texts[member_indices[0]]

    best_idx = member_indices[0]
    best_score = -1.0
    for i in member_indices:
        others = [j for j in member_indices if j != i]
        avg_sim = float(np.mean([similarity[i, j] for j in others]))
        if avg_sim > best_score or (avg_sim == best_score and len(texts[i]) < len(texts[best_idx])):
            best_score = avg_sim
            best_idx = i
    return texts[best_idx]


def _try_llm_label(member_texts: list[str]) -> Optional[str]:
    """
    Best-effort LLM-generated cluster name. Returns None (never
    raises) if no provider is configured or the call fails for any
    reason — the caller always has the representative-text fallback.
    """
    try:
        from ai.agents.llm import get_llm, LLMNotConfiguredError

        try:
            llm = get_llm()
        except LLMNotConfiguredError:
            return None

        prompt = (
            "These are similar customer feature requests:\n"
            + "\n".join(f"- {t}" for t in member_texts)
            + "\n\nRespond with ONLY a short (2-4 word) name for this feature opportunity, "
            "no punctuation, no explanation."
        )
        response = llm.call(messages=[{"role": "user", "content": prompt}])
        label = str(response).strip().strip('"')
        return label or None
    except Exception:  # noqa: BLE001 - labeling is a nicety; any failure just falls back
        logger.info("LLM cluster labeling failed; falling back to representative text", exc_info=True)
        return None
