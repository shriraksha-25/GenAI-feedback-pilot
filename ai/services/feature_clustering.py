"""
ai/services/feature_clustering.py
====================================
Groups semantically similar feature requests into broader feature
opportunities using configured GenAI embeddings when available, with
a local TF-IDF fallback when no provider is configured.
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

# Default cosine-distance threshold.
DEFAULT_DISTANCE_THRESHOLD = 0.35

# TF-IDF fallback needs a slightly more permissive threshold for
# short, lexically similar requests such as "Add dark mode to the app"
# and "Dark mode please".
TFIDF_MIN_DISTANCE_THRESHOLD = 0.50


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
    Group similar feature requests together.

    Empty requests are excluded. The original feedback fields are
    preserved, with feature_opportunity_group and cluster_id added.
    """
    usable = [
        item
        for item in items
        if item.get("feature_request")
        and item["feature_request"].strip()
    ]

    if not usable:
        return []

    if len(usable) == 1:
        only = dict(usable[0])
        only["feature_opportunity_group"] = only["feature_request"]
        only["cluster_id"] = 0
        return [only]  # type: ignore[list-item]

    texts = [item["feature_request"].strip() for item in usable]
    vectors, method = _vectorize(texts)

    logger.info(
        "Clustering %d feature requests using %s",
        len(texts),
        method,
    )

    similarity = cosine_similarity(vectors)
    distance = np.clip(1 - similarity, 0, None)
    np.fill_diagonal(distance, 0.0)

    # Adjust only the TF-IDF fallback. Keep the configured threshold
    # unchanged when using real GenAI embeddings.
    effective_threshold = distance_threshold
    if method == "tfidf":
        effective_threshold = max(
            distance_threshold,
            TFIDF_MIN_DISTANCE_THRESHOLD,
        )

    clustering = AgglomerativeClustering(
        n_clusters=None,
        metric="precomputed",
        linkage="average",
        distance_threshold=effective_threshold,
    )

    labels = clustering.fit_predict(distance)

    results: list[ClusteredFeatureItem] = []

    for cluster_id in sorted(set(labels)):
        member_indices = [
            i for i, label in enumerate(labels)
            if label == cluster_id
        ]

        representative_text = _pick_representative(
            member_indices,
            similarity,
            texts,
        )
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


def _vectorize(texts: list[str]) -> tuple[np.ndarray, str]:
    """Use configured GenAI embeddings, falling back to local TF-IDF."""

    if OPENAI_API_KEY:
        vectors = _embed_with_openai(texts)
        if vectors is not None:
            return vectors, "openai-embeddings"

    if GEMINI_API_KEY:
        vectors = _embed_with_gemini(texts)
        if vectors is not None:
            return vectors, "gemini-embeddings"

    logger.info(
        "No usable GenAI embedding provider configured; "
        "falling back to local TF-IDF similarity."
    )

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
    )
    return vectorizer.fit_transform(texts), "tfidf"


def _embed_with_openai(texts: list[str]) -> Optional[np.ndarray]:
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
        )
        return np.array([item.embedding for item in response.data])

    except Exception:  # noqa: BLE001
        logger.warning(
            "OpenAI embedding call failed; trying fallback.",
            exc_info=True,
        )
        return None


def _embed_with_gemini(texts: list[str]) -> Optional[np.ndarray]:
    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts,
        )
        return np.array(
            [embedding.values for embedding in response.embeddings]
        )

    except Exception:  # noqa: BLE001
        logger.warning(
            "Gemini embedding call failed; trying fallback.",
            exc_info=True,
        )
        return None


def _pick_representative(
    member_indices: list[int],
    similarity: np.ndarray,
    texts: list[str],
) -> str:
    """Choose the most representative text within a cluster."""

    if len(member_indices) == 1:
        return texts[member_indices[0]]

    best_idx = member_indices[0]
    best_score = -1.0

    for i in member_indices:
        others = [j for j in member_indices if j != i]
        avg_similarity = float(
            np.mean([similarity[i, j] for j in others])
        )

        if (
            avg_similarity > best_score
            or (
                avg_similarity == best_score
                and len(texts[i]) < len(texts[best_idx])
            )
        ):
            best_score = avg_similarity
            best_idx = i

    return texts[best_idx]


def _try_llm_label(
    member_texts: list[str],
) -> Optional[str]:
    """Generate a short cluster label when an LLM is available."""

    try:
        from ai.agents.llm import get_llm, LLMNotConfiguredError

        try:
            llm = get_llm()
        except LLMNotConfiguredError:
            return None

        prompt = (
            "These are similar customer feature requests:\n"
            + "\n".join(f"- {text}" for text in member_texts)
            + "\n\nRespond with ONLY a short (2-4 word) name "
            "for this feature opportunity, no punctuation, "
            "no explanation."
        )

        response = llm.call(
            messages=[{"role": "user", "content": prompt}]
        )
        label = str(response).strip().strip('"')

        return label or None

    except Exception:  # noqa: BLE001
        logger.info(
            "LLM cluster labeling failed; using representative text.",
            exc_info=True,
        )
        return None
