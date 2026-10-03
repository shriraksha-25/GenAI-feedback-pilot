"""
ai/tests/test_prd_generator.py
=================================
Tests for ai/services/prd_generator.py - the public interface the
backend calls. Same monkeypatch-the-crew-runner pattern as
ai/tests/test_feedback_analyzer_ai.py. No API key/network required.

Run from the repo root:
    pytest ai/tests/ -v
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.services import prd_generator  # noqa: E402
from ai.services.prd_generator import generate_prd  # noqa: E402
from ai.agents.llm import LLMNotConfiguredError  # noqa: E402
from ai.agents.schemas import PRDResult  # noqa: E402


def test_generate_prd_success(monkeypatch):
    fake_prd = PRDResult(
        title="Save Frequently Used Reports",
        problem_statement="Regenerating the same report every time is tedious.",
        customer_pain_points=["Regenerating the same report every time is tedious."],
        feature_requirements=["Allow users to save a report configuration for reuse."],
        supporting_evidence=["42"],
    )
    monkeypatch.setattr(prd_generator, "run_prd_crew", lambda context: fake_prd)

    result = generate_prd({"feature_name": "Save reports"}, feature_id="feat-1")

    assert result["feature_id"] == "feat-1"
    assert result["status"] == "ai_draft"
    assert result["prd"]["title"] == "Save Frequently Used Reports"
    assert result["prd"]["supporting_evidence"] == ["42"]
    assert "error" not in result


def test_generate_prd_not_configured(monkeypatch):
    def fake_run(context):
        raise LLMNotConfiguredError("no provider configured")

    monkeypatch.setattr(prd_generator, "run_prd_crew", fake_run)

    result = generate_prd({}, feature_id="feat-1")

    assert result["status"] == "not_configured"
    assert result["prd"] is None
    assert "no provider configured" in result["error"]


def test_generate_prd_failure_never_raises(monkeypatch):
    def fake_run(context):
        raise RuntimeError("rate limit exceeded")

    monkeypatch.setattr(prd_generator, "run_prd_crew", fake_run)

    result = generate_prd({})

    assert result["status"] == "failed"
    assert result["prd"] is None
    assert "rate limit exceeded" in result["error"]


def test_generate_prd_output_is_json_serializable(monkeypatch):
    import json

    fake_prd = PRDResult(title="Test Feature")
    monkeypatch.setattr(prd_generator, "run_prd_crew", lambda context: fake_prd)

    result = generate_prd({}, feature_id="feat-1")
    json.dumps(result)  # raises if not serializable


def test_generate_prd_feature_id_echoed_even_on_failure(monkeypatch):
    def fake_run(context):
        raise RuntimeError("boom")

    monkeypatch.setattr(prd_generator, "run_prd_crew", fake_run)

    result = generate_prd({}, feature_id="feat-99")
    assert result["feature_id"] == "feat-99"
