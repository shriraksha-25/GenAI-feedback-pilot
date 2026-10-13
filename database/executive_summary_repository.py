"""Versioned executive-summary persistence for Milestone 4."""

from datetime import datetime, timezone
from typing import Any

from pymongo import DESCENDING, ReturnDocument

from database.connection import get_database
from database.milestone4_models import (
    ExecutiveSummaryVersionRecord,
    RoadmapStatus,
)


async def _validate_summary_relationships(
    summary: ExecutiveSummaryVersionRecord,
) -> None:
    """Validate roadmap, feature and feedback relationships."""

    database = get_database()

    roadmap = await database.roadmaps.find_one(
        {
            "workspace_id": summary.workspace_id,
            "roadmap_id": summary.roadmap_id,
            "version": summary.roadmap_version,
        },
        {"_id": 1},
    )

    if roadmap is None:
        raise ValueError(
            "The referenced roadmap version does not exist "
            "in this workspace."
        )

    if summary.source_feature_ids:
        feature_cursor = database.features.find(
            {
                "workspace_id": summary.workspace_id,
                "feature_id": {
                    "$in": summary.source_feature_ids
                },
            },
            {"feature_id": 1},
        )

        existing_feature_ids = {
            document["feature_id"]
            async for document in feature_cursor
        }

        missing_feature_ids = (
            set(summary.source_feature_ids)
            - existing_feature_ids
        )

        if missing_feature_ids:
            missing_text = ", ".join(
                sorted(missing_feature_ids)
            )
            raise ValueError(
                "Summary features do not exist in this "
                f"workspace: {missing_text}"
            )

    if summary.source_feedback_ids:
        feedback_cursor = database.feedback.find(
            {
                "workspace_id": summary.workspace_id,
                "feedback_id": {
                    "$in": summary.source_feedback_ids
                },
            },
            {"feedback_id": 1},
        )

        existing_feedback_ids = {
            document["feedback_id"]
            async for document in feedback_cursor
        }

        missing_feedback_ids = (
            set(summary.source_feedback_ids)
            - existing_feedback_ids
        )

        if missing_feedback_ids:
            missing_text = ", ".join(
                sorted(missing_feedback_ids)
            )
            raise ValueError(
                "Summary feedback does not exist in this "
                f"workspace: {missing_text}"
            )


async def save_executive_summary_version(
    summary: ExecutiveSummaryVersionRecord
    | dict[str, Any],
) -> dict[str, Any]:
    """Save a new executive-summary version."""

    database = get_database()

    summary_model = (
        summary
        if isinstance(
            summary,
            ExecutiveSummaryVersionRecord,
        )
        else ExecutiveSummaryVersionRecord.model_validate(
            summary
        )
    )

    await _validate_summary_relationships(summary_model)

    latest = await database.executive_summaries.find_one(
        {
            "workspace_id": summary_model.workspace_id,
            "summary_id": summary_model.summary_id,
        },
        sort=[("version", DESCENDING)],
    )

    next_version = 1

    if latest is not None:
        next_version = latest.get("version", 0) + 1

    document = summary_model.model_dump(mode="python")
    document["version"] = next_version
    document["is_current"] = True
    document["created_at"] = datetime.now(timezone.utc)

    await database.executive_summaries.update_many(
        {
            "workspace_id": summary_model.workspace_id,
            "summary_id": summary_model.summary_id,
            "is_current": True,
        },
        {
            "$set": {
                "is_current": False,
            }
        },
    )

    await database.executive_summaries.insert_one(document)

    return document


async def get_current_executive_summary(
    workspace_id: str,
    summary_id: str,
) -> dict[str, Any] | None:
    """Retrieve the current executive-summary version."""

    database = get_database()

    return await database.executive_summaries.find_one(
        {
            "workspace_id": workspace_id,
            "summary_id": summary_id,
            "is_current": True,
        }
    )


async def get_executive_summary_version(
    workspace_id: str,
    summary_id: str,
    version: int,
) -> dict[str, Any] | None:
    """Retrieve a specific executive-summary version."""

    database = get_database()

    return await database.executive_summaries.find_one(
        {
            "workspace_id": workspace_id,
            "summary_id": summary_id,
            "version": version,
        }
    )


async def get_executive_summary_history(
    workspace_id: str,
    summary_id: str,
) -> list[dict[str, Any]]:
    """Retrieve all versions of an executive summary."""

    database = get_database()

    cursor = (
        database.executive_summaries
        .find(
            {
                "workspace_id": workspace_id,
                "summary_id": summary_id,
            }
        )
        .sort("version", DESCENDING)
    )

    return [document async for document in cursor]


async def list_roadmap_summaries(
    workspace_id: str,
    roadmap_id: str,
    current_only: bool = True,
) -> list[dict[str, Any]]:
    """List executive summaries for a roadmap."""

    database = get_database()

    query: dict[str, Any] = {
        "workspace_id": workspace_id,
        "roadmap_id": roadmap_id,
    }

    if current_only:
        query["is_current"] = True

    cursor = (
        database.executive_summaries
        .find(query)
        .sort("created_at", DESCENDING)
    )

    return [document async for document in cursor]


async def update_executive_summary_status(
    workspace_id: str,
    summary_id: str,
    status: RoadmapStatus,
    reviewed_by: str,
) -> dict[str, Any] | None:
    """Update review status on the current summary."""

    database = get_database()
    now = datetime.now(timezone.utc)

    update_fields: dict[str, Any] = {
        "review_status": status,
    }

    if status == "approved":
        update_fields["approved_by"] = reviewed_by
        update_fields["approved_at"] = now
    else:
        update_fields["approved_by"] = None
        update_fields["approved_at"] = None

    return (
        await database.executive_summaries
        .find_one_and_update(
            {
                "workspace_id": workspace_id,
                "summary_id": summary_id,
                "is_current": True,
            },
            {
                "$set": update_fields,
            },
            return_document=ReturnDocument.AFTER,
        )
    )