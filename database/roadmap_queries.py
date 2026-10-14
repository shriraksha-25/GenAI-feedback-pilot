"""Evidence-linked roadmap and dashboard queries."""

from collections import defaultdict
from typing import Any

from pymongo import DESCENDING

from database.connection import get_database


def _extract_roadmap_feature_ids(
    roadmap: dict[str, Any],
) -> set[str]:
    """Collect feature IDs scheduled in a roadmap."""

    feature_ids: set[str] = set(
        roadmap.get("source_feature_ids", [])
    )

    for milestone in roadmap.get("milestones", []):
        for item in milestone.get("feature_items", []):
            feature_id = item.get("feature_id")

            if feature_id:
                feature_ids.add(feature_id)

    return feature_ids


async def get_evidence_linked_roadmap(
    workspace_id: str,
    roadmap_id: str,
    version: int | None = None,
) -> dict[str, Any] | None:
    """
    Retrieve a roadmap with its features, priorities,
    evidence and original customer feedback.
    """

    database = get_database()

    roadmap_query: dict[str, Any] = {
        "workspace_id": workspace_id,
        "roadmap_id": roadmap_id,
    }

    if version is None:
        roadmap_query["is_current"] = True
    else:
        roadmap_query["version"] = version

    roadmap = await database.roadmaps.find_one(
        roadmap_query
    )

    if roadmap is None:
        return None

    feature_ids = _extract_roadmap_feature_ids(roadmap)

    features_by_id: dict[str, dict[str, Any]] = {}
    priorities_by_feature: dict[str, dict[str, Any]] = {}
    evidence_by_feature: dict[
        str,
        list[dict[str, Any]],
    ] = defaultdict(list)

    if feature_ids:
        feature_cursor = database.features.find(
            {
                "workspace_id": workspace_id,
                "feature_id": {"$in": list(feature_ids)},
            }
        )

        async for feature in feature_cursor:
            features_by_id[feature["feature_id"]] = feature

        priority_cursor = (
            database.priority_scores
            .find(
                {
                    "workspace_id": workspace_id,
                    "feature_id": {
                        "$in": list(feature_ids)
                    },
                }
            )
            .sort("calculated_at", DESCENDING)
        )

        async for priority in priority_cursor:
            feature_id = priority["feature_id"]

            if feature_id not in priorities_by_feature:
                priorities_by_feature[feature_id] = priority

        evidence_cursor = database.feature_evidence.find(
            {
                "workspace_id": workspace_id,
                "feature_id": {"$in": list(feature_ids)},
            }
        )

        async for evidence in evidence_cursor:
            evidence_by_feature[
                evidence["feature_id"]
            ].append(evidence)

    feedback_ids: set[str] = set(
        roadmap.get("source_feedback_ids", [])
    )

    for milestone in roadmap.get("milestones", []):
        for item in milestone.get("feature_items", []):
            feedback_ids.update(
                item.get("source_feedback_ids", [])
            )

    for evidence_records in evidence_by_feature.values():
        for evidence in evidence_records:
            feedback_id = evidence.get("feedback_id")

            if feedback_id:
                feedback_ids.add(feedback_id)

    feedback_by_id: dict[str, dict[str, Any]] = {}

    if feedback_ids:
        feedback_cursor = database.feedback.find(
            {
                "workspace_id": workspace_id,
                "feedback_id": {
                    "$in": list(feedback_ids)
                },
            }
        )

        async for feedback in feedback_cursor:
            feedback_by_id[
                feedback["feedback_id"]
            ] = feedback

    enriched_milestones: list[dict[str, Any]] = []

    for milestone in roadmap.get("milestones", []):
        enriched_milestone = dict(milestone)
        enriched_items: list[dict[str, Any]] = []

        for item in milestone.get("feature_items", []):
            enriched_item = dict(item)
            feature_id = item["feature_id"]

            evidence_records = evidence_by_feature.get(
                feature_id,
                [],
            )

            item_feedback_ids = set(
                item.get("source_feedback_ids", [])
            )

            for evidence in evidence_records:
                feedback_id = evidence.get("feedback_id")

                if feedback_id:
                    item_feedback_ids.add(feedback_id)

            enriched_item["feature"] = (
                features_by_id.get(feature_id)
            )
            enriched_item["latest_priority"] = (
                priorities_by_feature.get(feature_id)
            )
            enriched_item["evidence"] = evidence_records
            enriched_item["supporting_feedback"] = [
                feedback_by_id[feedback_id]
                for feedback_id in item_feedback_ids
                if feedback_id in feedback_by_id
            ]

            enriched_items.append(enriched_item)

        enriched_milestone["feature_items"] = (
            enriched_items
        )
        enriched_milestones.append(enriched_milestone)

    roadmap["milestones"] = enriched_milestones

    return roadmap


async def get_roadmap_dashboard_metrics(
    workspace_id: str,
    roadmap_id: str,
) -> dict[str, Any] | None:
    """Calculate roadmap dashboard and chart metrics."""

    roadmap = await get_evidence_linked_roadmap(
        workspace_id,
        roadmap_id,
    )

    if roadmap is None:
        return None

    total_features = 0
    total_effort = 0.0
    total_impact = 0.0
    total_progress = 0.0

    risk_counts = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }

    milestone_status_counts: dict[str, int] = (
        defaultdict(int)
    )

    for milestone in roadmap.get("milestones", []):
        milestone_status_counts[
            milestone.get("status", "planned")
        ] += 1

        total_progress += milestone.get(
            "progress_percentage",
            0.0,
        )

        for item in milestone.get(
            "feature_items",
            [],
        ):
            total_features += 1
            total_effort += item.get(
                "estimated_effort"
            ) or 0.0
            total_impact += item.get(
                "estimated_impact"
            ) or 0.0

            risk_level = item.get(
                "risk_level",
                "medium",
            )
            risk_counts[risk_level] = (
                risk_counts.get(risk_level, 0) + 1
            )

    milestone_count = len(
        roadmap.get("milestones", [])
    )

    average_progress = (
        round(total_progress / milestone_count, 2)
        if milestone_count
        else 0.0
    )

    average_impact = (
        round(total_impact / total_features, 2)
        if total_features
        else 0.0
    )

    return {
        "workspace_id": workspace_id,
        "roadmap_id": roadmap_id,
        "roadmap_version": roadmap["version"],
        "milestone_count": milestone_count,
        "feature_count": total_features,
        "total_estimated_effort": round(
            total_effort,
            2,
        ),
        "average_estimated_impact": average_impact,
        "average_milestone_progress": average_progress,
        "milestone_status_counts": dict(
            milestone_status_counts
        ),
        "risk_counts": risk_counts,
        "development_capacity": roadmap.get(
            "development_capacity"
        ),
        "capacity_unit": roadmap.get(
            "capacity_unit"
        ),
    }


async def get_product_strategy_context(
    workspace_id: str,
    roadmap_id: str,
) -> dict[str, Any] | None:
    """Prepare workspace data for the AI Strategy Advisor."""

    database = get_database()

    roadmap = await get_evidence_linked_roadmap(
        workspace_id,
        roadmap_id,
    )

    if roadmap is None:
        return None

    executive_summary = (
        await database.executive_summaries.find_one(
            {
                "workspace_id": workspace_id,
                "roadmap_id": roadmap_id,
                "is_current": True,
            },
            sort=[("created_at", DESCENDING)],
        )
    )

    metrics = await get_roadmap_dashboard_metrics(
        workspace_id,
        roadmap_id,
    )

    return {
        "roadmap": roadmap,
        "executive_summary": executive_summary,
        "dashboard_metrics": metrics,
    }
