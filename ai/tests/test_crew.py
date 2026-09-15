"""
ai/tests/test_crew.py
========================
Tests for ai/agents/crew.py's orchestration logic: given a crew that
produces some result, does run_feedback_crew() extract and combine it
correctly? Given a crew that fails, does the error propagate cleanly?

WHY FAKE CREWS INSTEAD OF MOCKING crewai INTERNALS
------------------------------------------------------
crewai routes LLM calls through provider-specific internal classes
(e.g. crewai.llms.providers.openai.completion.OpenAICompletion) that
differ by provider and have changed across crewai versions. Patching
those directly is brittle and version-coupled. Instead, these tests
use `run_feedback_crew(text, crew_factory=...)` — a factory function
that returns a lightweight fake object with just a `.kickoff()`
method, matching the ONE public method run_feedback_crew() actually
calls on whatever a "crew" is. This tests 100% of our own
extraction/combination logic without needing crewai to make a single
real network call, and without needing to know its internals at all.

These tests require NO API key and make NO network calls.

Run from the repo root:
    pytest ai/tests/ -v
"""

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.agents.crew import run_feedback_crew  # noqa: E402
from ai.agents.llm import LLMNotConfiguredError  # noqa: E402
from ai.agents.schemas import ThemeResult, PainPointResult, FeatureRequestResult  # noqa: E402


class _FakeTaskOutput:
    def __init__(self, pydantic_obj):
        self.pydantic = pydantic_obj


class _FakeCrewOutput:
    def __init__(self, tasks_output):
        self.tasks_output = tasks_output


class _FakeCrew:
    """Stands in for a real crewai.Crew — only .kickoff() is called by run_feedback_crew()."""

    def __init__(self, tasks_output):
        self._tasks_output = tasks_output

    def kickoff(self, inputs=None):
        return _FakeCrewOutput(self._tasks_output)


class _FailingCrew:
    def kickoff(self, inputs=None):
        raise RuntimeError("simulated LLM/provider failure")


def _make_successful_factory(theme, pain_point, feature):
    def factory(feedback_text):
        return _FakeCrew(
            [
                _FakeTaskOutput(theme),
                _FakeTaskOutput(pain_point),
                _FakeTaskOutput(feature),
            ]
        )

    return factory


def test_run_feedback_crew_combines_three_agent_outputs():
    factory = _make_successful_factory(
        ThemeResult(theme="App Stability", confidence=0.9),
        PainPointResult(pain_point="Customers cannot upload documents.", confidence=0.92),
        FeatureRequestResult(has_feature_request=False, confidence=0.6),
    )

    result = run_feedback_crew("The app keeps crashing.", crew_factory=factory)

    assert result.theme == "App Stability"
    assert result.theme_confidence == 0.9
    assert result.pain_point == "Customers cannot upload documents."
    assert result.pain_point_confidence == 0.92
    assert result.feature_request is None  # has_feature_request was False
    assert result.feature_request_confidence == 0.6


def test_run_feedback_crew_with_real_feature_request():
    factory = _make_successful_factory(
        ThemeResult(theme="Reporting", confidence=0.85),
        PainPointResult(pain_point="Regenerating the same report every time is tedious.", confidence=0.8),
        FeatureRequestResult(
            has_feature_request=True,
            feature_request="Save frequently used reports",
            feature_category="Reporting",
            confidence=0.88,
        ),
    )

    result = run_feedback_crew("I wish I could save my frequently used reports.", crew_factory=factory)

    assert result.feature_request == "Save frequently used reports"
    assert result.feature_category == "Reporting"
    assert result.feature_request_confidence == 0.88


def test_run_feedback_crew_propagates_llm_failures():
    """
    A real LLM/provider error (rate limit, network failure, etc.) must
    propagate to the caller (feedback_analyzer.py), not be swallowed
    or turned into a fabricated result here.
    """

    def failing_factory(feedback_text):
        return _FailingCrew()

    with pytest.raises(RuntimeError, match="simulated LLM/provider failure"):
        run_feedback_crew("Some feedback text.", crew_factory=failing_factory)


def test_run_feedback_crew_raises_on_malformed_structured_output():
    """
    If crewai's structured-output parsing fails for any agent (e.g. the
    model ignored the schema), .pydantic comes back None. This must be
    treated as a failure, never silently combined into a partial result.
    """

    def factory(feedback_text):
        return _FakeCrew(
            [
                _FakeTaskOutput(ThemeResult(theme="App Stability", confidence=0.9)),
                _FakeTaskOutput(None),  # pain point agent failed to produce valid structured output
                _FakeTaskOutput(FeatureRequestResult(has_feature_request=False, confidence=0.5)),
            ]
        )

    with pytest.raises(ValueError, match="structured result"):
        run_feedback_crew("Some feedback text.", crew_factory=factory)


def test_default_crew_factory_raises_llm_not_configured_without_api_key(monkeypatch):
    """
    With no crew_factory override and no API key configured, building
    the real crew must raise LLMNotConfiguredError (from ai.agents.llm)
    rather than silently using some default/dummy LLM.
    """
    monkeypatch.setattr("ai.agents.llm.OPENAI_API_KEY", None)
    monkeypatch.setattr("ai.agents.llm.GEMINI_API_KEY", None)

    with pytest.raises(LLMNotConfiguredError):
        run_feedback_crew("Some feedback text.")
