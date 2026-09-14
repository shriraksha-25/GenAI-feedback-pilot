"""
ai/tests/test_feature_clustering.py
======================================
Tests for ai/services/feature_clustering.py.

Two groups of tests here:
1. The TF-IDF fallback path — runs for real, fully offline, no mocking
   needed (no API key required to exercise this code path at all).
2. The real-embeddings path — the exact "Add UPI payments / Support
   Google Pay / Give us more payment options" example from the
   Milestone 2 spec, which TF-IDF genuinely cannot group (verified
   while building this module: those three share almost no
   vocabulary). This is tested by monkeypatching the embedding call
   itself to return controlled vectors, so the clustering ALGORITHM is
   exercised for real while the network call is not — no API key, no
   real embedding API call, no network access needed to run this test.

Run from the repo root:
    pytest ai/tests/ -v
"""

import sys
from pathlib import Path

import numpy as np

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.services import feature_clustering  # noqa: E402
from ai.services.feature_clustering import cluster_feature_requests  # noqa: E402


# ---------------------------------------------------------------------
# Basic behavior (no vectorization needed)
# ---------------------------------------------------------------------
def test_empty_list_returns_empty():
    assert cluster_feature_requests([]) == []


def test_items_with_blank_feature_request_are_skipped():
    items = [
        {"feedback_id": "1", "feature_request": "Add dark mode"},
        {"feedback_id": "2", "feature_request": ""},
        {"feedback_id": "3", "feature_request": "   "},
    ]
    result = cluster_feature_requests(items)
    ids = {r["feedback_id"] for r in result}
    assert ids == {"1"}


def test_single_item_is_its_own_cluster():
    items = [{"feedback_id": "1", "feature_request": "Add dark mode"}]
    result = cluster_feature_requests(items)
    assert len(result) == 1
    assert result[0]["feature_opportunity_group"] == "Add dark mode"
    assert result[0]["cluster_id"] == 0


# ---------------------------------------------------------------------
# TF-IDF fallback path (runs for real — no API key, no network)
# ---------------------------------------------------------------------
def test_tfidf_fallback_groups_lexically_similar_requests(monkeypatch):
    monkeypatch.setattr(feature_clustering, "OPENAI_API_KEY", None)
    monkeypatch.setattr(feature_clustering, "GEMINI_API_KEY", None)

    items = [
        {"feedback_id": "1", "feature_request": "Add dark mode to the app"},
        {"feedback_id": "2", "feature_request": "Dark mode please"},
        {"feedback_id": "3", "feature_request": "Export reports to PDF"},
    ]
    result = cluster_feature_requests(items)

    by_id = {r["feedback_id"]: r for r in result}
    assert by_id["1"]["cluster_id"] == by_id["2"]["cluster_id"]  # dark mode requests grouped
    assert by_id["3"]["cluster_id"] != by_id["1"]["cluster_id"]  # unrelated request separate


def test_tfidf_fallback_used_when_no_provider_configured(monkeypatch):
    monkeypatch.setattr(feature_clustering, "OPENAI_API_KEY", None)
    monkeypatch.setattr(feature_clustering, "GEMINI_API_KEY", None)

    texts = ["Add dark mode", "Export to PDF"]
    _, method = feature_clustering._vectorize(texts)
    assert method == "tfidf"


# ---------------------------------------------------------------------
# Real-embeddings path — exact example from the Milestone 2 spec,
# with the embedding call itself mocked out.
# ---------------------------------------------------------------------
def test_embedding_path_groups_cross_vocabulary_payment_requests(monkeypatch):
    """
    "Add UPI payments", "Support Google Pay", and "Give us more payment
    options" share almost no words - this is exactly the case TF-IDF
    cannot solve and real semantic embeddings are needed for. We mock
    the embedding call to return vectors that reflect what a real
    embedding model would produce (the three payment-related requests
    close together, the unrelated one far away), then verify the
    clustering algorithm correctly groups them.
    """
    monkeypatch.setattr(feature_clustering, "OPENAI_API_KEY", "sk-fake-test-key")
    monkeypatch.setattr(feature_clustering, "GEMINI_API_KEY", None)

    texts = [
        "Add UPI payments",
        "Support Google Pay",
        "Give us more payment options",
        "Export reports to PDF",
    ]

    # Hand-crafted vectors: first three nearly identical (simulating
    # what a real embedding model would produce for semantically
    # related payment requests), the fourth orthogonal/unrelated.
    fake_vectors = np.array(
        [
            [1.0, 0.05, 0.0],
            [0.98, 0.08, 0.0],
            [0.95, 0.10, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )

    def fake_embed_with_openai(texts_arg):
        assert texts_arg == texts
        return fake_vectors

    monkeypatch.setattr(feature_clustering, "_embed_with_openai", fake_embed_with_openai)

    items = [{"feedback_id": str(i), "feature_request": t} for i, t in enumerate(texts)]
    result = cluster_feature_requests(items)

    by_id = {r["feedback_id"]: r for r in result}
    payment_clusters = {by_id["0"]["cluster_id"], by_id["1"]["cluster_id"], by_id["2"]["cluster_id"]}
    assert len(payment_clusters) == 1, "all three payment-related requests should land in one cluster"
    assert by_id["3"]["cluster_id"] not in payment_clusters


def test_vectorize_prefers_openai_over_gemini_when_both_configured(monkeypatch):
    monkeypatch.setattr(feature_clustering, "OPENAI_API_KEY", "sk-fake")
    monkeypatch.setattr(feature_clustering, "GEMINI_API_KEY", "fake-gemini-key")
    monkeypatch.setattr(feature_clustering, "_embed_with_openai", lambda texts: np.array([[1.0], [2.0]]))
    monkeypatch.setattr(
        feature_clustering,
        "_embed_with_gemini",
        lambda texts: (_ for _ in ()).throw(AssertionError("gemini should not be called when openai is configured")),
    )

    _, method = feature_clustering._vectorize(["a", "b"])
    assert method == "openai-embeddings"


def test_vectorize_falls_back_to_tfidf_when_embedding_call_fails(monkeypatch):
    monkeypatch.setattr(feature_clustering, "OPENAI_API_KEY", "sk-fake")
    monkeypatch.setattr(feature_clustering, "GEMINI_API_KEY", None)
    monkeypatch.setattr(feature_clustering, "_embed_with_openai", lambda texts: None)  # simulates a failed call

    _, method = feature_clustering._vectorize(["Add dark mode", "Export to PDF"])
    assert method == "tfidf"
