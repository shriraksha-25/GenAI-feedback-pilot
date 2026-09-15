"""
ai/tests/test_feedback_analyzer_ai.py
========================================
Tests for the Milestone 2 addition to analyze_feedback(): running the
CrewAI agents on already-cleaned text and folding the result in.

Kept SEPARATE from ai/tests/test_feedback_analyzer.py (the Milestone 1
test file) deliberately: those tests cover text cleaning/validation
only and must keep passing unmodified as proof Milestone 1 behavior is
unbroken. These tests cover the new AI-augmentation concern using a
different fixture style (patching run_feedback_crew), so mixing them
into one file would blur which milestone's contract each test is
protecting.

No network access or API key is used or required by these tests.

Run from the repo root:
    pytest ai/tests/ -v
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.services import feedback_analyzer  # noqa: E402
from ai.services.feedback_analyzer import analyze_feedback  # noqa: E402
from ai.agents.llm import LLMNotConfiguredError  # noqa: E402
from ai.agents.schemas import AgentAnalysisResult  # noqa: E402


def test_rejected_text_never_reaches_ai_analysis(monkeypatch):
    """Milestone 1 behavior: empty/too-short text is rejected before AI runs at all."""
    called = {"count": 0}

    def fake_run(*args, **kwargs):
        called["count"] += 1
        raise AssertionError("AI analysis should not run for rejected text")

    monkeypatch.setattr(feedback_analyzer, "run_feedback_crew", fake_run)

    result = analyze_feedback(text="")
    assert result["status"] == "rejected"
    assert called["count"] == 0
    assert "ai_status" not in result  # M1 contract: no AI keys at all when text is rejected


def test_successful_analysis_populates_all_fields(monkeypatch):
    fake_result = AgentAnalysisResult(
        theme="App Stability",
        theme_confidence=0.9,
        pain_point="Customers cannot upload documents because the app crashes.",
        pain_point_confidence=0.92,
        feature_request=None,
        feature_category=None,
        feature_request_confidence=0.6,
    )
    monkeypatch.setattr(feedback_analyzer, "run_feedback_crew", lambda text: fake_result)

    result = analyze_feedback(text="The app keeps crashing whenever I try to upload a document.", feedback_id="7")

    assert result["status"] == "processed"
    assert result["ai_status"] == "completed"
    assert result["theme"] == "App Stability"
    assert result["pain_point"] == "Customers cannot upload documents because the app crashes."
    assert result["feature_opportunity"] is None
    assert result["confidence"]["theme"] == 0.9
    assert result["confidence"]["pain_point"] == 0.92
    assert result["sentiment"] is None  # explicitly not this milestone's scope
    assert result["category"] is None  # explicitly not this milestone's scope
    assert "ai_error" not in result


def test_feature_request_flows_through_to_feature_opportunity(monkeypatch):
    fake_result = AgentAnalysisResult(
        theme="Reporting",
        theme_confidence=0.85,
        pain_point="Regenerating the same report every time is tedious.",
        pain_point_confidence=0.8,
        feature_request="Save frequently used reports",
        feature_category="Reporting",
        feature_request_confidence=0.88,
    )
    monkeypatch.setattr(feedback_analyzer, "run_feedback_crew", lambda text: fake_result)

    result = analyze_feedback(text="I wish I could save my frequently used reports.")

    assert result["feature_opportunity"] == "Save frequently used reports"
    assert result["feature_category"] == "Reporting"
    assert result["confidence"]["feature_opportunity"] == 0.88


def test_llm_not_configured_degrades_gracefully_without_fake_data(monkeypatch):
    def fake_run(text):
        raise LLMNotConfiguredError("no provider configured")

    monkeypatch.setattr(feedback_analyzer, "run_feedback_crew", fake_run)

    result = analyze_feedback(text="Payment failed during checkout")

    assert result["status"] == "processed"  # the TEXT was fine
    assert result["ai_status"] == "not_configured"
    assert result["theme"] is None
    assert result["pain_point"] is None
    assert result["feature_opportunity"] is None
    assert result["confidence"] == {"theme": None, "pain_point": None, "feature_opportunity": None}
    assert "no provider configured" in result["ai_error"]


def test_llm_failure_reported_not_raised(monkeypatch):
    def fake_run(text):
        raise RuntimeError("rate limit exceeded")

    monkeypatch.setattr(feedback_analyzer, "run_feedback_crew", fake_run)

    result = analyze_feedback(text="Payment failed during checkout")

    assert result["status"] == "processed"
    assert result["ai_status"] == "failed"
    assert "rate limit exceeded" in result["ai_error"]
    assert result["theme"] is None  # no fabricated result on failure


def test_output_is_json_serializable_after_ai_augmentation(monkeypatch):
    import json

    fake_result = AgentAnalysisResult(
        theme="App Stability",
        theme_confidence=0.9,
        pain_point="Something broke.",
        pain_point_confidence=0.7,
        feature_request=None,
        feature_category=None,
        feature_request_confidence=0.5,
    )
    monkeypatch.setattr(feedback_analyzer, "run_feedback_crew", lambda text: fake_result)

    result = analyze_feedback(text="Something in the app broke today.", feedback_id="99")
    json.dumps(result)  # raises if not serializable
