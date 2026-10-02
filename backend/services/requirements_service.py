from uuid import uuid4

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


# =========================================================
# PRD
# =========================================================

def _build_prd_content(feature: dict) -> PRDContent:
    """
    Temporary structured PRD builder.

    This keeps the backend flow working until the Milestone 3
    AI PRD-generation service is provided by the AI module.
    """

    title = feature.get("title", "Feature")
    description = feature.get("description")
    pain_point = feature.get("pain_point")

    return PRDContent(
        overview=description or f"Product requirement for {title}.",
        problem_statement=pain_point,
        target_users=[],
        goals=[
            f"Deliver the requested capability: {title}"
        ],
        non_goals=[],
        functional_requirements=[
            f"Implement support for {title}."
        ],
        non_functional_requirements=[],
        success_metrics=[],
        risks=[],
        dependencies=[],
    )


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

    evidence = feature.get("evidence", [])

    evidence_feedback_ids = list(
        dict.fromkeys(
            item.get("feedback_id")
            for item in evidence
            if item.get("feedback_id")
        )
    )

    current_prd = await get_current_prd_for_feature(feature_id)

    if current_prd:
        prd_id = current_prd["prd_id"]
    else:
        prd_id = str(uuid4())

    content = _build_prd_content(feature)

    prd_record = PRDVersionRecord(
        prd_id=prd_id,
        workspace_id=workspace_id,
        feature_id=feature_id,
        title=f"PRD - {feature.get('title', 'Feature')}",
        content=content,
        evidence_feedback_ids=evidence_feedback_ids,
        review_status="ai_draft",
        generated_by_ai=False,
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


async def get_feature_current_prd(
    feature_id: str,
):
    prd = await get_current_prd_for_feature(feature_id)

    if prd is None:
        raise ValueError("PRD not found for this feature.")

    prd.pop("_id", None)

    return prd


async def get_prd_version_history(
    prd_id: str,
):
    history = await get_prd_history(prd_id)

    if not history:
        raise ValueError("PRD history not found.")

    for item in history:
        item.pop("_id", None)

    return history


# =========================================================
# USER STORIES + ACCEPTANCE CRITERIA
# =========================================================

def _build_acceptance_criteria(
    feature_title: str,
    requirement: str,
) -> list[AcceptanceCriterion]:
    """
    Temporary acceptance-criteria builder.

    Later this can be replaced by the AI module.
    """

    return [
        AcceptanceCriterion(
            criterion_id=str(uuid4()),
            title="Successful feature usage",
            given=f"The user is ready to use {feature_title}",
            when=requirement,
            then=f"The {feature_title} capability should complete successfully.",
            is_approved=False,
        ),
        AcceptanceCriterion(
            criterion_id=str(uuid4()),
            title="Failure handling",
            given=f"The user attempts to use {feature_title}",
            when="The requested action cannot be completed",
            then="The system should return a clear and useful response.",
            is_approved=False,
        ),
    ]


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

    current_prd = await get_current_prd_for_feature(feature_id)

    if current_prd is None:
        raise ValueError(
            "Generate a PRD before generating user stories."
        )

    if prd_id and current_prd.get("prd_id") != prd_id:
        raise ValueError(
            "Provided PRD does not match the current PRD for this feature."
        )

    content = current_prd.get("content", {})

    functional_requirements = (
        content.get("functional_requirements", [])
        if isinstance(content, dict)
        else []
    )

    if not functional_requirements:
        functional_requirements = [
            f"Implement support for {feature.get('title', 'Feature')}."
        ]

    evidence_feedback_ids = current_prd.get(
        "evidence_feedback_ids",
        [],
    )

    generated_stories = []

    for index, requirement in enumerate(
        functional_requirements,
        start=1,
    ):
        feature_title = feature.get("title", "Feature")

        story_record = UserStoryVersionRecord(
            user_story_id=str(uuid4()),
            workspace_id=workspace_id,
            feature_id=feature_id,
            prd_id=current_prd.get("prd_id"),
            prd_version=current_prd.get("version"),
            title=f"User Story {index} - {feature_title}",
            persona="Product user",
            need=requirement,
            value=(
                f"Use {feature_title} with a clear and reliable experience."
            ),
            acceptance_criteria=_build_acceptance_criteria(
                feature_title=feature_title,
                requirement=requirement,
            ),
            evidence_feedback_ids=evidence_feedback_ids,
            review_status="ai_draft",
            generated_by_ai=False,
            created_by=requested_by,
        )

        saved_story = await save_user_story_version(
            story_record
        )

        saved_story.pop("_id", None)

        generated_stories.append(saved_story)

    return generated_stories


async def get_user_story_by_id(
    user_story_id: str,
):
    story = await get_current_user_story(
        user_story_id
    )

    if story is None:
        raise ValueError("User story not found.")

    story.pop("_id", None)

    return story


async def get_user_story_version_history(
    user_story_id: str,
):
    history = await get_user_story_history(
        user_story_id
    )

    if not history:
        raise ValueError(
            "User story history not found."
        )

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
        raise ValueError(
            "Invalid user story review status."
        )

    updated_story = await update_user_story_review_status(
        user_story_id=user_story_id,
        status=status,
        reviewed_by=reviewed_by,
    )

    if updated_story is None:
        raise ValueError("User story not found.")

    updated_story.pop("_id", None)

    return updated_story