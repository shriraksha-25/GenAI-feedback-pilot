"""
ai/tests/test_product_assistant.py
=====================================
Tests for ai/services/product_assistant.py - the public interface the
backend calls for the Product Intelligence Assistant.

Run from the repo root:
    pytest ai/tests/ -v
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.services import product_assistant  # noqa: E402
from ai.services.product_assistant import ask_assistant  # noqa: E402
from ai.agents.llm import LLMNotConfiguredError  # noqa: E402
from ai.agents.schemas import AssistantResponse  # noqa: E402


def test_ask_assistant_grounded_answer(monkeypatch):
    fake_response = AssistantResponse(
        answer="Two customers reported the same crash when uploading documents.",
        grounded=True,
        referenced_feedback_ids=["42", "43"],
        confidence=0.9,
    )
    monkeypatch.setattr(product_assistant, "run_assistant_crew", lambda question, context: fake_response)

    result = ask_assistant("What feedback supports this?", {"supporting_evidence": []})

    assert result["status"] == "completed"
    assert result["grounded"] is True
    assert result["referenced_feedback_ids"] == ["42", "43"]
    assert result["confidence"] == 0.9


def test_ask_assistant_ungrounded_answer(monkeypatch):
    fake_response = AssistantResponse(
        answer="This information is not available in the provided project context.",
        grounded=False,
        referenced_feedback_ids=[],
        confidence=0.95,
    )
    monkeypatch.setattr(product_assistant, "run_assistant_crew", lambda question, context: fake_response)

    result = ask_assistant("What is our market share?", {})

    assert result["status"] == "completed"  # the ANALYSIS succeeded even though the answer says "unavailable"
    assert result["grounded"] is False


def test_ask_assistant_rejects_empty_question_without_calling_llm(monkeypatch):
    called = {"count": 0}

    def fake_run(question, context):
        called["count"] += 1
        raise AssertionError("should not be called for empty input")

    monkeypatch.setattr(product_assistant, "run_assistant_crew", fake_run)

    result = ask_assistant("")

    assert result["status"] == "failed"
    assert called["count"] == 0


def test_ask_assistant_not_configured(monkeypatch):
    def fake_run(question, context):
        raise LLMNotConfiguredError("no provider configured")

    monkeypatch.setattr(product_assistant, "run_assistant_crew", fake_run)

    result = ask_assistant("Why is this feature important?")
    assert result["status"] == "not_configured"
    assert result["answer"] is None


def test_ask_assistant_failure_never_raises(monkeypatch):
    def fake_run(question, context):
        raise RuntimeError("rate limit exceeded")

    monkeypatch.setattr(product_assistant, "run_assistant_crew", fake_run)

    result = ask_assistant("Why is this feature important?")
    assert result["status"] == "failed"
    assert "rate limit exceeded" in result["error"]


def test_ask_assistant_output_is_json_serializable(monkeypatch):
    import json

    fake_response = AssistantResponse(answer="Yes.", grounded=True, referenced_feedback_ids=["1"], confidence=0.8)
    monkeypatch.setattr(product_assistant, "run_assistant_crew", lambda question, context: fake_response)

    result = ask_assistant("some question")
    json.dumps(result)  # raises if not serializable


def test_ask_assistant_default_context_is_empty_dict_not_none(monkeypatch):
    """context is Optional - calling without one must not crash run_assistant_crew with None."""
    captured = {}

    def fake_run(question, context):
        captured["context"] = context
        return AssistantResponse(answer="ok", grounded=True, confidence=0.5)

    monkeypatch.setattr(product_assistant, "run_assistant_crew", fake_run)

    ask_assistant("some question")  # no context passed
    assert captured["context"] == {}
