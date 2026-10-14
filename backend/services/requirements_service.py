
import asyncio
import logging
from uuid import uuid4

from ai.services.prd_generator import generate_prd
from ai.services.user_story_generator import (
    generate_user_stories,
    generate_acceptance_criteria,
)
from database.feature_repository import get_feature_with_evidence
from database.milestone3_models import (
    AcceptanceCriterion,
    PRDContent,
    PRDVersionRecord,
    UserStoryVersionRecord,
)
from database.requirements_repository import (
    get_current_prd_for_feature,
    get_current_user_story,
    get_prd_history,
    get_user_story_history,
    save_prd_version,
    save_user_story_version,
    update_prd_review_status,
    update_user_story_review_status,
)

logger = logging.getLogger(__name__)


class AIGenerationError(RuntimeError):
    """Raised when an AI generator cannot produce a valid result."""


def _as_dict(value):
    """Return a dictionary or an empty dictionary."""
    return value if isinstance(value, dict) else {}


def _add_unique(items: list, value):
    """Add a non-empty string only when it is not already present."""
    if isinstance(value, str):
        value = value.strip()
        if value and value not in items:
            items.append(value)


def _get_feature_context(feature: dict) -> dict:
    """Build AI context from a feature and its linked evidence."""

    feature_id = str(
        feature.get("feature_id")
        or feature.get("id")
        or ""
    )

    feature_name = (
        feature.get("title")
        or feature.get("name")
        or "Feature"
    )

    themes = []
    pain_points = []
    feature_requests = []
    supporting_evidence = []

    # Include information already stored on the feature itself.
    _add_unique(themes, feature.get("theme"))
    _add_unique(pain_points, feature.get("pain_point"))
    _add_unique(feature_requests, feature.get("description"))
    _add_unique(
        feature_requests,
        feature.get("feature_category"),
    )

    evidence = feature.get("evidence") or []

    for item in evidence:
        item = _as_dict(item)

        analysis = _as_dict(
            item.get("ai_analysis")
            or item.get("analysis")
        )

        # FeatureEvidenceRecord stores its available text in `excerpt`.
        evidence_text = (
            item.get("excerpt")
            or item.get("text")
            or item.get("description")
            or item.get("content")
            or item.get("feedback_text")
            or ""
        )

        theme = (
            item.get("theme")
            or analysis.get("theme")
        )

        pain_point = (
            item.get("pain_point")
            or analysis.get("pain_point")
        )

        feature_request = (
            item.get("feature_request")
            or analysis.get("feature_opportunity")
        )

        _add_unique(themes, theme)
        _add_unique(pain_points, pain_point)
        _add_unique(feature_requests, feature_request)

        feedback_id = item.get("feedback_id")

        if feedback_id:
            supporting_evidence.append({
                "feedback_id": str(feedback_id),
                "text": str(evidence_text).strip(),
            })

    opportunity_group = (
        feature.get("feature_opportunity_group")
        or feature.get("feature_category")
    )

    return {
        "feature_id": feature_id,
        "feature_name": feature_name,
        "themes": themes,
        "pain_points": pain_points,
        "feature_requests": feature_requests,
        "feature_opportunity_group": opportunity_group,
        "supporting_evidence": supporting_evidence,
    }


def _require_ai_result(result: dict, output_key: str):
    """Reject failed or unconfigured AI output instead of saving fake results."""

    result = _as_dict(result)

    if result.get("status") != "ai_draft":
        status = result.get("status", "unknown")
        detail = result.get(
            "error",
            "No error details provided.",
        )
        raise AIGenerationError(
            f"AI generation {status}: {detail}"
        )

    output = result.get(output_key)

    if not output:
        raise AIGenerationError(
            f"AI generation returned no {output_key}."
        )

    return output


# =========================================================
# PRD GENERATION
# =========================================================

async def generate_prd_for_feature(
    feature_id: str,
    workspace_id: str,
    requested_by: str | None = None,
):
    feature = await get_feature_with_evidence(feature_id)

    if feature is None:
        raise ValueError("Feature not found.")

    if feature.get("workspace_id") != workspace_id:
        raise ValueError(
            "Feature does not belong to the requested workspace."
        )

    context = _get_feature_context(feature)

    logger.info(
        "Generating PRD for feature %s with %d evidence records",
        feature_id,
        len(context["supporting_evidence"]),
    )

    result = await asyncio.to_thread(
        generate_prd,
        context,
        feature_id,
    )

    ai_prd = _as_dict(
        _require_ai_result(result, "prd")
    )

    evidence_ids = list(dict.fromkeys(
        item["feedback_id"]
        for item in context["supporting_evidence"]
    ))

    current_prd = await get_current_prd_for_feature(
        feature_id
    )

    prd_id = (
        current_prd["prd_id"]
        if current_prd
        else str(uuid4())
    )

    objective = ai_prd.get("objective")
    feature_summary = ai_prd.get("feature_summary")

    content = PRDContent(
        overview=feature_summary or objective,
        problem_statement=ai_prd.get("problem_statement"),
        target_users=ai_prd.get("target_users") or [],
        goals=[objective] if objective else [],
        non_goals=ai_prd.get("out_of_scope") or [],
        functional_requirements=(
            ai_prd.get("feature_requirements") or []
        ),
        non_functional_requirements=[],
        success_metrics=ai_prd.get("success_metrics") or [],
        risks=ai_prd.get("risks") or [],
        dependencies=ai_prd.get("dependencies") or [],
    )

    prd_record = PRDVersionRecord(
        prd_id=prd_id,
        workspace_id=workspace_id,
        feature_id=feature_id,
        title=(
            ai_prd.get("title")
            or f"PRD - {context['feature_name']}"
        ),
        content=content,
        evidence_feedback_ids=evidence_ids,
        review_status="ai_draft",
        generated_by_ai=True,
        created_by=requested_by,
    )

    saved_prd = await save_prd_version(prd_record)
    saved_prd.pop("_id", None)

    return saved_prd


async def review_prd(
    prd_id: str,
    status: str,
    reviewed_by: str,
):
    allowed_statuses = {
        "ai_draft",
        "under_review",
        "approved",
        "rejected",
    }

    if status not in allowed_statuses:
        raise ValueError("Invalid PRD review status.")

    updated_prd = await update_prd_review_status(
        prd_id=prd_id,
        status=status,
        reviewed_by=reviewed_by,
    )

    if updated_prd is None:
        raise ValueError("PRD not found.")

    updated_prd.pop("_id", None)
    return updated_prd


async def get_feature_current_prd(feature_id: str):
    prd = await get_current_prd_for_feature(feature_id)

    if prd is None:
        raise ValueError(
            "PRD not found for this feature."
        )

    prd.pop("_id", None)
    return prd


async def get_prd_version_history(prd_id: str):
    history = await get_prd_history(prd_id)

    if not history:
        raise ValueError("PRD history not found.")

    for item in history:
        item.pop("_id", None)

    return history


# =========================================================
# USER STORIES + ACCEPTANCE CRITERIA
# =========================================================

async def generate_user_stories_for_feature(
    feature_id: str,
    workspace_id: str,
    prd_id: str | None = None,
    requested_by: str | None = None,
):
    feature = await get_feature_with_evidence(feature_id)

    if feature is None:
        raise ValueError("Feature not found.")

    if feature.get("workspace_id") != workspace_id:
        raise ValueError(
            "Feature does not belong to the requested workspace."
        )

    current_prd = await get_current_prd_for_feature(
        feature_id
    )

    if current_prd is None:
        raise ValueError(
            "Generate a PRD before generating user stories."
        )

    if (
        prd_id
        and current_prd.get("prd_id") != prd_id
    ):
        raise ValueError(
            "Provided PRD does not match the current PRD "
            "for this feature."
        )

    context = _get_feature_context(feature)

    context["prd"] = {
        "title": current_prd.get("title"),
        "content": current_prd.get("content", {}),
    }

    result = await asyncio.to_thread(
        generate_user_stories,
        context,
        feature_id,
    )

    ai_stories = _require_ai_result(
        result,
        "user_stories",
    )

    if not isinstance(ai_stories, list):
        raise AIGenerationError(
            "AI returned user stories in an unexpected format."
        )

    if not ai_stories:
        raise AIGenerationError(
            "AI returned an empty user-story list."
        )

    evidence_ids = list(dict.fromkeys(
        item["feedback_id"]
        for item in context["supporting_evidence"]
    ))

    # Prepare every story and its acceptance criteria before saving.
    prepared_stories = []

    for ai_story in ai_stories:
        ai_story = _as_dict(ai_story)

        story_text = ai_story.get("user_story")
        persona = ai_story.get("user_type")
        need = ai_story.get("goal")
        value = ai_story.get("benefit")

        if not all((story_text, persona, need, value)):
            raise AIGenerationError(
                "AI returned a user story with missing "
                "required fields."
            )

        ac_result = await asyncio.to_thread(
            generate_acceptance_criteria,
            user_story_text=story_text,
            context=context,
            feature_id=feature_id,
        )

        ai_criteria = _require_ai_result(
            ac_result,
            "acceptance_criteria",
        )

        if not isinstance(ai_criteria, list):
            raise AIGenerationError(
                "AI returned acceptance criteria in an "
                "unexpected format."
            )

        criteria = []

        for criterion_data in ai_criteria:
            criterion_data = _as_dict(criterion_data)
            criterion_text = criterion_data.get("criterion")

            if not criterion_text:
                continue

            criteria.append(
                AcceptanceCriterion(
                    criterion_id=str(uuid4()),
                    title=criterion_data.get("id"),
                    given=(
                        "The user has access to "
                        f"{context['feature_name']}."
                    ),
                    when=(
                        "The user performs the action: "
                        f"{need}"
                    ),
                    then=criterion_text,
                    is_approved=False,
                )
            )

        prepared_stories.append({
            "title": need,
            "persona": persona,
            "need": need,
            "value": value,
            "acceptance_criteria": criteria,
        })

    saved_stories = []

    for story in prepared_stories:
        story_record = UserStoryVersionRecord(
            user_story_id=str(uuid4()),
            workspace_id=workspace_id,
            feature_id=feature_id,
            prd_id=current_prd.get("prd_id"),
            prd_version=current_prd.get("version"),
            title=story["title"],
            persona=story["persona"],
            need=story["need"],
            value=story["value"],
            acceptance_criteria=story[
                "acceptance_criteria"
            ],
            evidence_feedback_ids=evidence_ids,
            review_status="ai_draft",
            generated_by_ai=True,
            created_by=requested_by,
        )

        saved_story = await save_user_story_version(
            story_record
        )
        saved_story.pop("_id", None)
        saved_stories.append(saved_story)

    return saved_stories


async def get_user_story_by_id(user_story_id: str):
    story = await get_current_user_story(user_story_id)

    if story is None:
        raise ValueError("User story not found.")

    story.pop("_id", None)
    return story


async def get_user_story_version_history(
    user_story_id: str,
):
    history = await get_user_story_history(user_story_id)

    if not history:
        raise ValueError("User story history not found.")

    for item in history:
        item.pop("_id", None)

    return history


async def review_user_story(
    user_story_id: str,
    status: str,
    reviewed_by: str,
):
    allowed_statuses = {
        "ai_draft",
        "under_review",
        "approved",
        "rejected",
    }

    if status not in allowed_statuses:
        raise ValueError("Invalid user story review status.")

    updated_story = await update_user_story_review_status(
        user_story_id=user_story_id,
        status=status,
        reviewed_by=reviewed_by,
    )

    if updated_story is None:
        raise ValueError("User story not found.")

    updated_story.pop("_id", None)
    return updated_story
