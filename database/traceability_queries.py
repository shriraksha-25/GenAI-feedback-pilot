"""Traceability queries for the complete Milestone 3 workflow."""

from typing import Any

from pymongo import DESCENDING

from database.connection import get_database
from database.milestone3_models import WorkflowEventRecord


async def record_workflow_event(
    event: WorkflowEventRecord | dict[str, Any],
) -> dict[str, Any]:
    """Store an audit event for a workflow status change."""

    database = get_database()

    event_model = (
        event
        if isinstance(event, WorkflowEventRecord)
        else WorkflowEventRecord.model_validate(event)
    )

    document = event_model.model_dump(mode="python")
    await database.workflow_events.insert_one(document)

    return document


async def get_feature_workflow_history(
    feature_id: str,
) -> list[dict[str, Any]]:
    """Retrieve the complete workflow audit history of a feature."""

    database = get_database()

    cursor = (
        database.workflow_events
        .find({"feature_id": feature_id})
        .sort("created_at", DESCENDING)
    )

    return [document async for document in cursor]


async def get_feature_traceability(
    feature_id: str,
) -> dict[str, Any] | None:
    """
    Retrieve the complete relationship:

    feedback -> feature -> priority -> PRD -> user stories
    """

    database = get_database()

    feature = await database.features.find_one(
        {"feature_id": feature_id}
    )

    if feature is None:
        return None

    evidence_cursor = (
        database.feature_evidence
        .find({"feature_id": feature_id})
        .sort("created_at", DESCENDING)
    )

    evidence = [
        document async for document in evidence_cursor
    ]

    feedback_ids = set(
        feature.get("source_feedback_ids", [])
    )

    for evidence_record in evidence:
        feedback_id = evidence_record.get("feedback_id")

        if feedback_id:
            feedback_ids.add(feedback_id)

    feedback_records: list[dict[str, Any]] = []

    if feedback_ids:
        feedback_cursor = database.feedback.find(
            {
                "feedback_id": {
                    "$in": list(feedback_ids),
                }
            }
        )

        feedback_records = [
            document async for document in feedback_cursor
        ]

    latest_priority = await database.priority_scores.find_one(
        {"feature_id": feature_id},
        sort=[("calculated_at", DESCENDING)],
    )

    current_prd = await database.prds.find_one(
        {
            "feature_id": feature_id,
            "is_current": True,
        },
        sort=[("created_at", DESCENDING)],
    )

    story_cursor = (
        database.user_stories
        .find(
            {
                "feature_id": feature_id,
                "is_current": True,
            }
        )
        .sort("created_at", DESCENDING)
    )

    current_user_stories = [
        document async for document in story_cursor
    ]

    workflow_history = await get_feature_workflow_history(
        feature_id
    )

    return {
        "feature": feature,
        "evidence": evidence,
        "feedback": feedback_records,
        "priority": latest_priority,
        "prd": current_prd,
        "user_stories": current_user_stories,
        "workflow_history": workflow_history,
    }


async def get_requirements_for_feedback(
    feedback_id: str,
) -> list[dict[str, Any]]:
    """Find features and requirements created from feedback."""

    database = get_database()

    feature_cursor = database.features.find(
        {"source_feedback_ids": feedback_id}
    )

    features = [
        document async for document in feature_cursor
    ]

    results: list[dict[str, Any]] = []

    for feature in features:
        feature_id = feature["feature_id"]

        current_prd = await database.prds.find_one(
            {
                "feature_id": feature_id,
                "is_current": True,
            }
        )

        story_cursor = database.user_stories.find(
            {
                "feature_id": feature_id,
                "is_current": True,
            }
        )

        stories = [
            document async for document in story_cursor
        ]

        results.append(
            {
                "feature": feature,
                "prd": current_prd,
                "user_stories": stories,
            }
        )

    return results


async def get_workspace_workflow_counts(
    workspace_id: str,
) -> dict[str, int]:
    """Return workflow-stage counts for the requirements workspace."""

    database = get_database()

    statuses = [
        "identified",
        "prioritized",
        "prd_generated",
        "stories_generated",
        "approved",
        "archived",
    ]

    counts: dict[str, int] = {}

    for status in statuses:
        counts[status] = await database.features.count_documents(
            {
                "workspace_id": workspace_id,
                "status": status,
            }
        )

    counts["total"] = await database.features.count_documents(
        {"workspace_id": workspace_id}
    )

    return counts