"""
ai/services/user_story_generator.py
======================================
PUBLIC INTERFACE for user story and acceptance criteria generation.
Same pattern as ai.services.prd_generator / ai.services.feedback_analyzer:
plain dicts in and out, no CrewAI/Pydantic details leaked to the caller.

    from ai.services.user_story_generator import generate_user_stories, generate_acceptance_criteria

    stories = generate_user_stories(context={...}, feature_id="feat-001")
    # stories["user_stories"] -> list of {"user_story": ..., "user_type": ..., "goal": ..., "benefit": ...}

    ac = generate_acceptance_criteria(
        user_story_text=stories["user_stories"][0]["user_story"],
        context={...},
    )
    # ac["acceptance_criteria"] -> list of {"id": "AC-1", "criterion": ..., "priority": "Must"}

Acceptance criteria are generated PER user story (one call per story),
not all stories at once - this keeps each criterion set tightly scoped
to the one story it belongs to, mirroring how a real PM/QA workflow
reviews one story's criteria at a time.
"""

from __future__ import annotations

import logging
from typing import Optional

from ai.agents.product_crew import run_user_story_crew, run_acceptance_criteria_crew
from ai.agents.llm import LLMNotConfiguredError

logger = logging.getLogger("ai.services.user_story_generator")


def generate_user_stories(context: dict, feature_id: Optional[str] = None) -> dict:
    """
    Generate 1-5 user stories from Milestone 2 feedback-analysis
    context (see ai.agents.context.FeatureContext).

    Returns
    -------
    dict, always with these keys:
        {
            "feature_id": <str or None>,
            "status": "ai_draft" | "failed" | "not_configured",
            "user_stories": <list[dict] or None>,  # each: {user_story, user_type, goal, benefit}
            "error": <str>,  # only if status != "ai_draft"
        }

    Never raises. See ai.services.prd_generator.generate_prd for the
    identical error-handling contract and the "ai_draft" status note.
    """
    try:
        result = run_user_story_crew(context)
    except LLMNotConfiguredError as exc:
        logger.info("User story generation skipped for feature %s: %s", feature_id, exc)
        return {"feature_id": feature_id, "status": "not_configured", "user_stories": None, "error": str(exc)}
    except Exception as exc:  # noqa: BLE001
        logger.error("User story generation failed for feature %s: %s", feature_id, exc, exc_info=True)
        return {"feature_id": feature_id, "status": "failed", "user_stories": None, "error": f"{type(exc).__name__}: {exc}"}

    logger.info("Generated %d user stories for feature %s", len(result.user_stories), feature_id)
    return {
        "feature_id": feature_id,
        "status": "ai_draft",
        "user_stories": [s.model_dump() for s in result.user_stories],
    }


def generate_acceptance_criteria(
    user_story_text: str,
    context: Optional[dict] = None,
    feature_id: Optional[str] = None,
) -> dict:
    """
    Generate acceptance criteria for ONE user story.

    Parameters
    ----------
    user_story_text:
        The full "As a X, I want Y, so that Z" sentence to write
        criteria for (e.g. one entry from generate_user_stories()'s
        output). Required.
    context:
        Optional FeatureContext-shaped dict for additional grounding
        (e.g. supporting_evidence) - not required, since the user
        story text itself is usually enough to write testable criteria.
    feature_id:
        Optional caller-supplied ID, echoed back unchanged.

    Returns
    -------
    dict, always with these keys:
        {
            "feature_id": <str or None>,
            "status": "ai_draft" | "failed" | "not_configured",
            "acceptance_criteria": <list[dict] or None>,  # each: {id, criterion, priority}
            "error": <str>,  # only if status != "ai_draft"
        }

    Never raises. `id` values ("AC-1", "AC-2", ...) are LOCAL labels
    for this call only, NOT database IDs - see AcceptanceCriterionResult
    in ai/agents/schemas.py.
    """
    if not user_story_text or not user_story_text.strip():
        return {
            "feature_id": feature_id,
            "status": "failed",
            "acceptance_criteria": None,
            "error": "user_story_text is required and cannot be empty.",
        }

    try:
        result = run_acceptance_criteria_crew(user_story_text, context or {})
    except LLMNotConfiguredError as exc:
        logger.info("Acceptance criteria generation skipped for feature %s: %s", feature_id, exc)
        return {"feature_id": feature_id, "status": "not_configured", "acceptance_criteria": None, "error": str(exc)}
    except Exception as exc:  # noqa: BLE001
        logger.error("Acceptance criteria generation failed for feature %s: %s", feature_id, exc, exc_info=True)
        return {"feature_id": feature_id, "status": "failed", "acceptance_criteria": None, "error": f"{type(exc).__name__}: {exc}"}

    logger.info("Generated %d acceptance criteria for feature %s", len(result.acceptance_criteria), feature_id)
    return {
        "feature_id": feature_id,
        "status": "ai_draft",
        "acceptance_criteria": [ac.model_dump() for ac in result.acceptance_criteria],
    }
