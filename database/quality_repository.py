"""AI quality evaluation persistence for Milestone 4."""

from datetime import datetime, timezone
from typing import Any

from pymongo import DESCENDING

from database.connection import get_database
from database.milestone4_models import (
    AIQualityEvaluationRecord,
)


async def _find_evaluated_entity(
    evaluation: AIQualityEvaluationRecord,
) -> tuple[Any, dict[str, Any]] | tuple[None, None]:
    """Find the roadmap or summary being evaluated."""

    database = get_database()

    if evaluation.entity_type == "roadmap":
        collection = database.roadmaps
        query: dict[str, Any] = {
            "workspace_id": evaluation.workspace_id,
            "roadmap_id": evaluation.entity_id,
        }

        if evaluation.entity_version is None:
            query["is_current"] = True
        else:
            query["version"] = evaluation.entity_version

        return collection, query

    if evaluation.entity_type == "executive_summary":
        collection = database.executive_summaries
        query = {
            "workspace_id": evaluation.workspace_id,
            "summary_id": evaluation.entity_id,
        }

        if evaluation.entity_version is None:
            query["is_current"] = True
        else:
            query["version"] = evaluation.entity_version

        return collection, query

    # Recommendations may be generated without a separate
    # persistent entity document.
    return None, None


async def save_quality_evaluation(
    evaluation: AIQualityEvaluationRecord
    | dict[str, Any],
) -> dict[str, Any]:
    """Store an AI evaluation and update the evaluated entity."""

    database = get_database()

    evaluation_model = (
        evaluation
        if isinstance(
            evaluation,
            AIQualityEvaluationRecord,
        )
        else AIQualityEvaluationRecord.model_validate(
            evaluation
        )
    )

    collection, entity_query = await _find_evaluated_entity(
        evaluation_model
    )

    if collection is not None and entity_query is not None:
        entity = await collection.find_one(
            entity_query,
            {"_id": 1},
        )

        if entity is None:
            raise ValueError(
                "The evaluated entity does not exist "
                "in this workspace."
            )

    document = evaluation_model.model_dump(mode="python")
    now = datetime.now(timezone.utc)

    if document["metrics"]["evaluated_at"] is None:
        document["metrics"]["evaluated_at"] = now

    document["created_at"] = now

    await database.ai_quality_evaluations.insert_one(
        document
    )

    if collection is not None and entity_query is not None:
        await collection.update_one(
            entity_query,
            {
                "$set": {
                    "quality_metrics": document["metrics"],
                }
            },
        )

    return document


async def get_latest_quality_evaluation(
    workspace_id: str,
    entity_type: str,
    entity_id: str,
) -> dict[str, Any] | None:
    """Retrieve the newest evaluation for an entity."""

    database = get_database()

    return await database.ai_quality_evaluations.find_one(
        {
            "workspace_id": workspace_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
        },
        sort=[("created_at", DESCENDING)],
    )


async def list_workspace_quality_evaluations(
    workspace_id: str,
    validation_status: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """List quality evaluations for one workspace."""

    database = get_database()

    query: dict[str, Any] = {
        "workspace_id": workspace_id,
    }

    if validation_status is not None:
        query["metrics.validation_status"] = (
            validation_status
        )

    safe_limit = max(1, min(limit, 500))

    cursor = (
        database.ai_quality_evaluations
        .find(query)
        .sort("created_at", DESCENDING)
        .limit(safe_limit)
    )

    return [document async for document in cursor]


async def get_quality_dashboard_metrics(
    workspace_id: str,
) -> dict[str, Any]:
    """Calculate AI Quality & Trust Dashboard metrics."""

    evaluations = (
        await list_workspace_quality_evaluations(
            workspace_id,
            limit=500,
        )
    )

    status_counts = {
        "pending": 0,
        "passed": 0,
        "warning": 0,
        "failed": 0,
    }

    completeness_values: list[float] = []
    relevance_values: list[float] = []
    evidence_values: list[float] = []
    response_times: list[int] = []

    missing_information_count = 0
    warning_count = 0

    for evaluation in evaluations:
        metrics = evaluation.get("metrics", {})

        status = metrics.get(
            "validation_status",
            "pending",
        )
        status_counts[status] = (
            status_counts.get(status, 0) + 1
        )

        completeness = metrics.get(
            "completeness_score"
        )
        relevance = metrics.get("relevance_score")
        evidence = metrics.get("evidence_coverage")
        response_time = metrics.get("response_time_ms")

        if completeness is not None:
            completeness_values.append(completeness)

        if relevance is not None:
            relevance_values.append(relevance)

        if evidence is not None:
            evidence_values.append(evidence)

        if response_time is not None:
            response_times.append(response_time)

        missing_information_count += len(
            metrics.get("missing_information", [])
        )
        warning_count += len(
            metrics.get("warnings", [])
        )

    def average(values: list[float | int]) -> float:
        if not values:
            return 0.0

        return round(sum(values) / len(values), 3)

    return {
        "workspace_id": workspace_id,
        "evaluation_count": len(evaluations),
        "validation_status_counts": status_counts,
        "average_completeness_score": average(
            completeness_values
        ),
        "average_relevance_score": average(
            relevance_values
        ),
        "average_evidence_coverage": average(
            evidence_values
        ),
        "average_response_time_ms": average(
            response_times
        ),
        "missing_information_count": (
            missing_information_count
        ),
        "warning_count": warning_count,
    }