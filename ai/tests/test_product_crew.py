"""
ai/tests/test_product_crew.py
================================
Tests for ai/agents/product_crew.py's orchestration logic: given a
crew that returns some structured result, do run_prd_crew() /
run_user_story_crew() / run_acceptance_criteria_crew() /
run_priority_explanation_crew() extract it correctly? Given a crew
that fails, does the error propagate?

Same fake-crew approach as ai/tests/test_crew.py (Milestone 2) - see
that file's docstring for why fake crews are used instead of mocking
crewai's internals. No API key, no network access required.

Run from the repo root:
    pytest ai/tests/ -v
"""

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.agents.product_crew import (  # noqa: E402
    run_prd_crew,
    run_user_story_crew,
    run_acceptance_criteria_crew,
    run_priority_explanation_crew,
)
from ai.agents.schemas import (  # noqa: E402
    PRDResult,
    UserStoriesResult,
    UserStoryResult,
    AcceptanceCriteriaResult,
    AcceptanceCriterionResult,
    PriorityExplanationResult,
)


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


# ---------------------------------------------------------------------
# PRD generation
# ---------------------------------------------------------------------
def test_run_prd_crew_returns_structured_result():
    fake_prd = PRDResult(
        title="Save Frequently Used Reports",
        problem_statement="Regenerating the same report every time is tedious.",
        customer_pain_points=["Regenerating the same report every time is tedious."],
        supporting_evidence=["42"],
    )
    result = run_prd_crew({"feature_name": "test"}, crew_factory=lambda ctx: _FakeCrew(fake_prd))
    assert result.title == "Save Frequently Used Reports"
    assert result.supporting_evidence == ["42"]


def test_run_prd_crew_allows_mostly_empty_prd_when_context_is_sparse():
    """A PRD with only a title and everything else empty is a VALID result, not an error - this is what 'use null/empty instead of hallucinating' looks like in practice."""
    sparse_prd = PRDResult(title="Unnamed Feature")
    result = run_prd_crew({}, crew_factory=lambda ctx: _FakeCrew(sparse_prd))
    assert result.title == "Unnamed Feature"
    assert result.customer_pain_points == []
    assert result.risks == []


def test_run_prd_crew_propagates_failures():
    with pytest.raises(RuntimeError, match="simulated LLM/provider failure"):
        run_prd_crew({}, crew_factory=lambda ctx: _FailingCrew())


def test_run_prd_crew_raises_on_malformed_output():
    with pytest.raises(ValueError, match="structured result"):
        run_prd_crew({}, crew_factory=lambda ctx: _FakeCrew(None))


# ---------------------------------------------------------------------
# User story generation
# ---------------------------------------------------------------------
def test_run_user_story_crew_returns_list():
    fake_stories = UserStoriesResult(
        user_stories=[
            UserStoryResult(
                user_story="As a user, I want to save frequently used reports, so that I don't regenerate them.",
                user_type="user",
                goal="save frequently used reports",
                benefit="don't regenerate them every time",
            )
        ]
    )
    result = run_user_story_crew({}, crew_factory=lambda ctx: _FakeCrew(fake_stories))
    assert len(result.user_stories) == 1
    assert result.user_stories[0].user_type == "user"


def test_run_user_story_crew_allows_empty_list_when_no_evidence():
    empty_stories = UserStoriesResult(user_stories=[])
    result = run_user_story_crew({}, crew_factory=lambda ctx: _FakeCrew(empty_stories))
    assert result.user_stories == []


def test_run_user_story_crew_propagates_failures():
    with pytest.raises(RuntimeError, match="simulated LLM/provider failure"):
        run_user_story_crew({}, crew_factory=lambda ctx: _FailingCrew())


# ---------------------------------------------------------------------
# Acceptance criteria generation
# ---------------------------------------------------------------------
def test_run_acceptance_criteria_crew_returns_list_with_local_ids():
    fake_ac = AcceptanceCriteriaResult(
        acceptance_criteria=[
            AcceptanceCriterionResult(id="AC-1", criterion="Clicking Save stores the current report configuration.", priority="Must"),
            AcceptanceCriterionResult(id="AC-2", criterion="Saved reports appear in a 'My Reports' list.", priority="Should"),
        ]
    )
    result = run_acceptance_criteria_crew(
        "As a user, I want to save reports, so that I don't regenerate them.",
        {},
        crew_factory=lambda story, ctx: _FakeCrew(fake_ac),
    )
    assert len(result.acceptance_criteria) == 2
    assert result.acceptance_criteria[0].id == "AC-1"
    assert result.acceptance_criteria[0].priority == "Must"


def test_run_acceptance_criteria_crew_propagates_failures():
    with pytest.raises(RuntimeError, match="simulated LLM/provider failure"):
        run_acceptance_criteria_crew("some story", {}, crew_factory=lambda s, c: _FailingCrew())


# ---------------------------------------------------------------------
# Priority explanation
# ---------------------------------------------------------------------
def test_run_priority_explanation_crew_returns_structured_result():
    fake_explanation = PriorityExplanationResult(
        impact_reasoning="High impact because multiple customers independently requested this.",
        supporting_pain_points=["Regenerating the same report every time is tedious."],
        evidence_summary="Two feedback records cite the same friction.",
    )
    result = run_priority_explanation_crew({}, crew_factory=lambda ctx: _FakeCrew(fake_explanation))
    assert "High impact" in result.impact_reasoning
    assert len(result.supporting_pain_points) == 1


def test_run_priority_explanation_crew_propagates_failures():
    with pytest.raises(RuntimeError, match="simulated LLM/provider failure"):
        run_priority_explanation_crew({}, crew_factory=lambda ctx: _FailingCrew())
