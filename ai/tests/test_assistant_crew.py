"""
ai/tests/test_assistant_crew.py
==================================
Tests for ai/agents/assistant_crew.py. Same fake-crew pattern as
ai/tests/test_crew.py and ai/tests/test_product_crew.py. No API key,
no network access required.

Run from the repo root:
    pytest ai/tests/ -v
"""

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.agents.assistant_crew import run_assistant_crew  # noqa: E402
from ai.agents.schemas import AssistantResponse  # noqa: E402


class _FakeTaskOutput:
    def __init__(self, pydantic_obj):
        self.pydantic = pydantic_obj


class _FakeCrewOutput:
    def __init__(self, result):
        self.tasks_output = [_FakeTaskOutput(result)]


class _FakeCrew:
    def __init__(self, result):
        self._result = result

    def kickoff(self, inputs=None):
        return _FakeCrewOutput(self._result)


class _FailingCrew:
    def kickoff(self, inputs=None):
        raise RuntimeError("simulated LLM/provider failure")


def test_grounded_answer_returned_correctly():
    fake_response = AssistantResponse(
        answer="Two customers reported the same crash when uploading documents.",
        grounded=True,
        referenced_feedback_ids=["42", "43"],
        confidence=0.9,
    )
    result = run_assistant_crew(
        "What customer feedback supports this feature?",
        {"supporting_evidence": [{"feedback_id": "42", "text": "..."}]},
        crew_factory=lambda q, c: _FakeCrew(fake_response),
    )
    assert result.grounded is True
    assert result.referenced_feedback_ids == ["42", "43"]


def test_ungrounded_answer_when_context_insufficient():
    """
    The whole point of the `grounded` flag: when the context genuinely
    doesn't support an answer, the agent should say so rather than
    guess - this test checks our extraction/combination logic handles
    that result correctly, not that a real LLM behaves this way (that
    needs the live smoke test).
    """
    fake_response = AssistantResponse(
        answer="This information is not available in the provided project context.",
        grounded=False,
        referenced_feedback_ids=[],
        confidence=0.95,
    )
    result = run_assistant_crew("What is our market share?", {}, crew_factory=lambda q, c: _FakeCrew(fake_response))
    assert result.grounded is False
    assert result.referenced_feedback_ids == []


def test_propagates_llm_failures():
    with pytest.raises(RuntimeError, match="simulated LLM/provider failure"):
        run_assistant_crew("some question", {}, crew_factory=lambda q, c: _FailingCrew())


def test_raises_on_malformed_output():
    with pytest.raises(ValueError, match="structured result"):
        run_assistant_crew("some question", {}, crew_factory=lambda q, c: _FakeCrew(None))
