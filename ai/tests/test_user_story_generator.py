"""
ai/tests/test_user_story_generator.py
========================================
Tests for ai/services/user_story_generator.py - the public interface
the backend calls for both user stories and acceptance criteria.

Run from the repo root:
    pytest ai/tests/ -v
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ai.services import user_story_generator  # noqa: E402
from ai.services.user_story_generator import generate_user_stories, generate_acceptance_criteria  # noqa: E402
from ai.agents.llm import LLMNotConfiguredError  # noqa: E402
from ai.agents.schemas import UserStoriesResult, UserStoryResult, AcceptanceCriteriaResult, AcceptanceCriterionResult  # noqa: E402


# ---------------------------------------------------------------------
# generate_user_stories
# ---------------------------------------------------------------------
def test_generate_user_stories_success(monkeypatch):
    fake_result = UserStoriesResult(
        user_stories=[
            UserStoryResult(
                user_story="As a user, I want to save reports, so that I don't regenerate them.",
                user_type="user",
                goal="save reports",
                benefit="don't regenerate them",
            )
        ]
    )
    monkeypatch.setattr(user_story_generator, "run_user_story_crew", lambda context: fake_result)

    result = generate_user_stories({}, feature_id="feat-1")

    assert result["status"] == "ai_draft"
    assert len(result["user_stories"]) == 1
    assert result["user_stories"][0]["user_type"] == "user"


def test_generate_user_stories_not_configured(monkeypatch):
    def fake_run(context):
        raise LLMNotConfiguredError("no provider configured")

    monkeypatch.setattr(user_story_generator, "run_user_story_crew", fake_run)

    result = generate_user_stories({})
    assert result["status"] == "not_configured"
    assert result["user_stories"] is None


def test_generate_user_stories_never_raises_on_failure(monkeypatch):
    monkeypatch.setattr(user_story_generator, "run_user_story_crew", lambda context: (_ for _ in ()).throw(RuntimeError("boom")))

    result = generate_user_stories({})
    assert result["status"] == "failed"
    assert "boom" in result["error"]


# ---------------------------------------------------------------------
# generate_acceptance_criteria
# ---------------------------------------------------------------------
def test_generate_acceptance_criteria_success(monkeypatch):
    fake_result = AcceptanceCriteriaResult(
        acceptance_criteria=[
            AcceptanceCriterionResult(id="AC-1", criterion="Clicking Save stores the configuration.", priority="Must"),
        ]
    )
    monkeypatch.setattr(user_story_generator, "run_acceptance_criteria_crew", lambda story, context: fake_result)

    result = generate_acceptance_criteria("As a user, I want to save reports, so that I don't regenerate them.")

    assert result["status"] == "ai_draft"
    assert result["acceptance_criteria"][0]["id"] == "AC-1"
    assert result["acceptance_criteria"][0]["priority"] == "Must"


def test_generate_acceptance_criteria_rejects_empty_story_without_calling_llm(monkeypatch):
    called = {"count": 0}

    def fake_run(story, context):
        called["count"] += 1
        raise AssertionError("should not be called for empty input")

    monkeypatch.setattr(user_story_generator, "run_acceptance_criteria_crew", fake_run)

    result = generate_acceptance_criteria("")

    assert result["status"] == "failed"
    assert called["count"] == 0
    assert "required" in result["error"]


def test_generate_acceptance_criteria_not_configured(monkeypatch):
    def fake_run(story, context):
        raise LLMNotConfiguredError("no provider configured")

    monkeypatch.setattr(user_story_generator, "run_acceptance_criteria_crew", fake_run)

    result = generate_acceptance_criteria("As a user, I want X, so that Y.")
    assert result["status"] == "not_configured"


def test_full_output_is_json_serializable(monkeypatch):
    import json

    fake_stories = UserStoriesResult(user_stories=[UserStoryResult(user_story="...", user_type="user", goal="...", benefit="...")])
    monkeypatch.setattr(user_story_generator, "run_user_story_crew", lambda context: fake_stories)
    result = generate_user_stories({}, feature_id="feat-1")
    json.dumps(result)  # raises if not serializable
