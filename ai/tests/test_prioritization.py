"""
ai/tests/test_prioritization.py
==================================
Tests for ai/services/prioritization.py.

`calculate_rice_score` is pure arithmetic - tested for real, no
mocking needed at all. `explain_priority` wraps it with an LLM
explanation call, tested with a monkeypatched
run_priority_explanation_crew (no API key/network needed), the same
pattern as ai/tests/test_feedback_analyzer_ai.py uses for
run_feedback_crew.

Run from the repo root:
    pytest ai/tests/ -v
"""

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.services import prioritization  # noqa: E402
from ai.services.prioritization import calculate_rice_score, explain_priority  # noqa: E402
from ai.agents.llm import LLMNotConfiguredError  # noqa: E402
from ai.agents.schemas import PriorityExplanationResult  # noqa: E402


# ---------------------------------------------------------------------
# calculate_rice_score — pure arithmetic, real tests, no mocking
# ---------------------------------------------------------------------
def test_rice_score_is_deterministic():
    score1 = calculate_rice_score(reach=1000, impact=2, confidence=0.8, effort=3)
    score2 = calculate_rice_score(reach=1000, impact=2, confidence=0.8, effort=3)
    assert score1 == score2 == 533.33


def test_rice_score_formula_is_exactly_reach_impact_confidence_over_effort():
    # 100 * 3 * 1.0 / 2 = 150.0, chosen so there's no rounding to hide a wrong formula
    assert calculate_rice_score(reach=100, impact=3, confidence=1.0, effort=2) == 150.0


def test_rice_score_higher_effort_lowers_score():
    low_effort = calculate_rice_score(reach=100, impact=2, confidence=1.0, effort=1)
    high_effort = calculate_rice_score(reach=100, impact=2, confidence=1.0, effort=10)
    assert low_effort > high_effort


def test_rice_score_rejects_zero_effort():
    with pytest.raises(ValueError, match="effort"):
        calculate_rice_score(reach=100, impact=1, confidence=1, effort=0)


def test_rice_score_rejects_negative_effort():
    with pytest.raises(ValueError, match="effort"):
        calculate_rice_score(reach=100, impact=1, confidence=1, effort=-5)


def test_rice_score_rejects_negative_reach():
    with pytest.raises(ValueError, match="non-negative"):
        calculate_rice_score(reach=-10, impact=1, confidence=1, effort=1)


# ---------------------------------------------------------------------
# explain_priority — score always present, explanation best-effort
# ---------------------------------------------------------------------
def test_explain_priority_returns_score_even_when_llm_not_configured(monkeypatch):
    def fake_run(context):
        raise LLMNotConfiguredError("no provider configured")

    monkeypatch.setattr(prioritization, "run_priority_explanation_crew", fake_run)

    result = explain_priority({}, reach=1000, impact=2, confidence=0.8, effort=3, feature_id="f1")

    assert result["priority_score"] == 533.33  # the score is NEVER blocked by missing AI config
    assert result["ai_status"] == "not_configured"
    assert result["impact_reasoning"] is None
    assert "no provider configured" in result["ai_error"]


def test_explain_priority_returns_score_even_when_llm_fails(monkeypatch):
    def fake_run(context):
        raise RuntimeError("rate limit exceeded")

    monkeypatch.setattr(prioritization, "run_priority_explanation_crew", fake_run)

    result = explain_priority({}, reach=1000, impact=2, confidence=0.8, effort=3)

    assert result["priority_score"] == 533.33
    assert result["ai_status"] == "failed"
    assert "rate limit exceeded" in result["ai_error"]


def test_explain_priority_populates_explanation_fields_on_success(monkeypatch):
    fake_explanation = PriorityExplanationResult(
        impact_reasoning="High impact because multiple customers independently requested this.",
        supporting_pain_points=["Regenerating the same report every time is tedious."],
        assumptions=[],
        evidence_summary="Two feedback records cite the same friction.",
    )
    monkeypatch.setattr(prioritization, "run_priority_explanation_crew", lambda context: fake_explanation)

    result = explain_priority(
        {"pain_points": ["Regenerating the same report every time is tedious."]},
        reach=1000,
        impact=2,
        confidence=0.8,
        effort=3,
        feature_id="f1",
    )

    assert result["ai_status"] == "completed"
    assert result["priority_score"] == 533.33
    assert "High impact" in result["impact_reasoning"]
    assert result["supporting_pain_points"] == ["Regenerating the same report every time is tedious."]
    assert "error" not in result or result.get("ai_error") is None


def test_explain_priority_passes_computed_score_into_explanation_context(monkeypatch):
    """The explanation agent must be given the ALREADY-COMPUTED score, never asked to invent its own."""
    captured_context = {}

    def fake_run(context):
        captured_context.update(context)
        return PriorityExplanationResult(impact_reasoning="ok")

    monkeypatch.setattr(prioritization, "run_priority_explanation_crew", fake_run)

    explain_priority({}, reach=100, impact=3, confidence=1.0, effort=2)

    assert captured_context["priority"]["score"] == 150.0
    assert captured_context["priority"]["reach"] == 100
