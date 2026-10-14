"""Versioned roadmap persistence for Milestone 4."""

from datetime import datetime, timezone
from typing import Any

from pymongo import DESCENDING, ReturnDocument

from database.connection import get_database
from database.milestone4_models import (
    RoadmapStatus,
    RoadmapVersionRecord,
)


def _collect_feature_ids(
    roadmap: RoadmapVersionRecord,
) -> set[str]:
    """Collect every feature referenced by the roadmap."""

    feature_ids = set(roadmap.source_feature_ids)

    for milestone in roadmap.milestones:
        for item in milestone.feature_items:
            feature_ids.add(item.feature_id)

    return feature_ids


def _validate_dependency_graph(
    roadmap: RoadmapVersionRecord,
    feature_ids: set[str],
) -> None:
    """Validate dependency references and detect dependency cycles."""

    graph: dict[str, list[str]] = {
        feature_id: [] for feature_id in feature_ids
    }

    for dependency in roadmap.dependencies:
        if dependency.feature_id == dependency.depends_on_feature_id:
            raise ValueError(
                "A feature cannot depend on itself."
            )

        if dependency.feature_id not in feature_ids:
            raise ValueError(
                f"Unknown dependent feature: "
                f"{dependency.feature_id}"
            )

        if dependency.depends_on_feature_id not in feature_ids:
            raise ValueError(
                f"Unknown dependency feature: "
                f"{dependency.depends_on_feature_id}"
            )

        graph[dependency.feature_id].append(
            dependency.depends_on_feature_id
        )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(feature_id: str) -> None:
        if feature_id in visiting:
            raise ValueError(
                "Circular roadmap dependency detected."
            )

        if feature_id in visited:
            return

        visiting.add(feature_id)

        for dependency_id in graph.get(feature_id, []):
            visit(dependency_id)

        visiting.remove(feature_id)
        visited.add(feature_id)

    for feature_id in feature_ids:
        visit(feature_id)


async def _validate_roadmap_integrity(
    roadmap: RoadmapVersionRecord,
) -> set[str]:
    """Validate milestones, features and workspace ownership."""

    database = get_database()

    milestone_ids = [
        milestone.milestone_id
        for milestone in roadmap.milestones
    ]

    if len(milestone_ids) != len(set(milestone_ids)):
        raise ValueError(
            "Duplicate milestone IDs are not allowed."
        )

    scheduled_feature_ids: list[str] = []

    for milestone in roadmap.milestones:
        if (
            milestone.start_date is not None
            and milestone.end_date is not None
            and milestone.end_date < milestone.start_date
        ):
            raise ValueError(
                f"Milestone {milestone.milestone_id} "
                "ends before it starts."
            )

        for item in milestone.feature_items:
            scheduled_feature_ids.append(item.feature_id)

            if (
                item.planned_start is not None
                and item.planned_end is not None
                and item.planned_end < item.planned_start
            ):
                raise ValueError(
                    f"Feature {item.feature_id} "
                    "ends before it starts."
                )

    if len(scheduled_feature_ids) != len(
        set(scheduled_feature_ids)
    ):
        raise ValueError(
            "A feature cannot be scheduled more than once "
            "in the same roadmap version."
        )

    feature_ids = _collect_feature_ids(roadmap)
    _validate_dependency_graph(roadmap, feature_ids)

    if feature_ids:
        cursor = database.features.find(
            {
                "workspace_id": roadmap.workspace_id,
                "feature_id": {"$in": list(feature_ids)},
            },
            {"feature_id": 1},
        )

        existing_ids = {
            document["feature_id"]
            async for document in cursor
        }

        missing_ids = feature_ids - existing_ids

        if missing_ids:
            missing_text = ", ".join(sorted(missing_ids))
            raise ValueError(
                "Features do not exist in this workspace: "
                f"{missing_text}"
            )

    return feature_ids


async def save_roadmap_version(
    roadmap: RoadmapVersionRecord | dict[str, Any],
) -> dict[str, Any]:
    """Create a new immutable roadmap version."""

    database = get_database()

    roadmap_model = (
        roadmap
        if isinstance(roadmap, RoadmapVersionRecord)
        else RoadmapVersionRecord.model_validate(roadmap)
    )

    feature_ids = await _validate_roadmap_integrity(
        roadmap_model
    )

    latest = await database.roadmaps.find_one(
        {
            "workspace_id": roadmap_model.workspace_id,
            "roadmap_id": roadmap_model.roadmap_id,
        },
        sort=[("version", DESCENDING)],
    )

    next_version = 1

    if latest is not None:
        next_version = latest.get("version", 0) + 1

    document = roadmap_model.model_dump(mode="python")
    document["version"] = next_version

    is_baseline = (
        roadmap_model.roadmap_type == "baseline"
    )

    document["is_current"] = is_baseline
    document["source_feature_ids"] = sorted(feature_ids)
    document["created_at"] = datetime.now(timezone.utc)

    # Only an official baseline revision replaces the
    # current baseline. What-if versions remain scenarios.
    if is_baseline:
        await database.roadmaps.update_many(
            {
                "workspace_id": roadmap_model.workspace_id,
                "roadmap_id": roadmap_model.roadmap_id,
                "is_current": True,
            },
            {
                "$set": {
                    "is_current": False,
                }
            },
        )

    await database.roadmaps.insert_one(document)

    return document

async def get_current_roadmap(
    workspace_id: str,
    roadmap_id: str,
) -> dict[str, Any] | None:
    """Retrieve the current roadmap version in a workspace."""

    database = get_database()

    return await database.roadmaps.find_one(
        {
            "workspace_id": workspace_id,
            "roadmap_id": roadmap_id,
            "is_current": True,
        }
    )


async def get_roadmap_version(
    workspace_id: str,
    roadmap_id: str,
    version: int,
) -> dict[str, Any] | None:
    """Retrieve one specific roadmap version."""

    database = get_database()

    return await database.roadmaps.find_one(
        {
            "workspace_id": workspace_id,
            "roadmap_id": roadmap_id,
            "version": version,
        }
    )


async def get_roadmap_history(
    workspace_id: str,
    roadmap_id: str,
) -> list[dict[str, Any]]:
    """Retrieve every version of a roadmap."""

    database = get_database()

    cursor = (
        database.roadmaps
        .find(
            {
                "workspace_id": workspace_id,
                "roadmap_id": roadmap_id,
            }
        )
        .sort("version", DESCENDING)
    )

    return [document async for document in cursor]


async def list_workspace_roadmaps(
    workspace_id: str,
    status: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List current roadmaps belonging to one workspace."""

    database = get_database()

    query: dict[str, Any] = {
        "workspace_id": workspace_id,
        "is_current": True,
    }

    if status is not None:
        query["review_status"] = status

    safe_limit = max(1, min(limit, 100))

    cursor = (
        database.roadmaps
        .find(query)
        .sort("created_at", DESCENDING)
        .limit(safe_limit)
    )

    return [document async for document in cursor]


async def update_roadmap_review_status(
    workspace_id: str,
    roadmap_id: str,
    status: RoadmapStatus,
    reviewed_by: str,
) -> dict[str, Any] | None:
    """Update review information on the current roadmap."""

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

    return await database.roadmaps.find_one_and_update(
        {
            "workspace_id": workspace_id,
            "roadmap_id": roadmap_id,
            "is_current": True,
        },
        {
            "$set": update_fields,
        },
        return_document=ReturnDocument.AFTER,
    )
