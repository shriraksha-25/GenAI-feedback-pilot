"""Feature prioritization storage and RICE score calculation."""

from datetime import datetime, timezone
from typing import Any

from pymongo import DESCENDING

from database.connection import get_database
from database.milestone3_models import (
    PriorityConfigurationRecord,
    PriorityInputs,
    PriorityScoreRecord,
)


def calculate_rice_score(
    inputs: PriorityInputs | dict[str, Any],
    weights: dict[str, float] | None = None,
) -> float:
    """Calculate a configurable RICE score."""

    input_model = (
        inputs
        if isinstance(inputs, PriorityInputs)
        else PriorityInputs.model_validate(inputs)
    )

    active_weights = weights or {
        "reach": 1.0,
        "impact": 1.0,
        "confidence": 1.0,
        "effort": 1.0,
    }

    weighted_reach = (
        input_model.reach * active_weights.get("reach", 1.0)
    )
    weighted_impact = (
        input_model.impact * active_weights.get("impact", 1.0)
    )
    weighted_confidence = (
        input_model.confidence
        * active_weights.get("confidence", 1.0)
    ) / 100.0

    weighted_effort = (
        input_model.effort * active_weights.get("effort", 1.0)
    )

    if weighted_effort <= 0:
        raise ValueError("Weighted effort must be greater than zero.")

    score = (
        weighted_reach
        * weighted_impact
        * weighted_confidence
    ) / weighted_effort

    return round(score, 2)


def build_rice_explanation(
    inputs: PriorityInputs,
    score: float,
) -> str:
    """Generate a human-readable explanation for a RICE score."""

    return (
        f"RICE score {score} was calculated using "
        f"reach={inputs.reach}, "
        f"impact={inputs.impact}, "
        f"confidence={inputs.confidence}%, and "
        f"effort={inputs.effort}."
    )


async def create_priority_configuration(
    configuration: PriorityConfigurationRecord | dict[str, Any],
) -> dict[str, Any]:
    """Create a workspace prioritization configuration."""

    database = get_database()

    configuration_model = (
        configuration
        if isinstance(
            configuration,
            PriorityConfigurationRecord,
        )
        else PriorityConfigurationRecord.model_validate(
            configuration
        )
    )

    document = configuration_model.model_dump(mode="python")

    if configuration_model.is_active:
        await database.priority_configurations.update_many(
            {
                "workspace_id": configuration_model.workspace_id,
                "is_active": True,
            },
            {
                "$set": {
                    "is_active": False,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

    await database.priority_configurations.insert_one(document)

    return document


async def get_active_priority_configuration(
    workspace_id: str,
) -> dict[str, Any] | None:
    """Retrieve the active prioritization configuration."""

    database = get_database()

    return await database.priority_configurations.find_one(
        {
            "workspace_id": workspace_id,
            "is_active": True,
        }
    )


async def save_priority_score(
    priority_score: PriorityScoreRecord | dict[str, Any],
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Calculate and save a feature priority score."""

    database = get_database()

    score_model = (
        priority_score
        if isinstance(priority_score, PriorityScoreRecord)
        else PriorityScoreRecord.model_validate(priority_score)
    )

    calculated_score = calculate_rice_score(
        score_model.inputs,
        weights,
    )

    document = score_model.model_dump(mode="python")
    document["calculated_score"] = calculated_score
    document["calculated_at"] = datetime.now(timezone.utc)

    if not document.get("explanation"):
        document["explanation"] = build_rice_explanation(
            score_model.inputs,
            calculated_score,
        )

    await database.priority_scores.insert_one(document)

    await database.features.update_one(
        {"feature_id": score_model.feature_id},
        {
            "$set": {
                "status": "prioritized",
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    return document


async def get_latest_priority_score(
    feature_id: str,
) -> dict[str, Any] | None:
    """Retrieve the newest priority score for a feature."""

    database = get_database()

    return await database.priority_scores.find_one(
        {"feature_id": feature_id},
        sort=[("calculated_at", DESCENDING)],
    )


async def get_priority_history(
    feature_id: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Retrieve previous priority calculations for a feature."""

    database = get_database()

    safe_limit = max(1, min(limit, 100))

    cursor = (
        database.priority_scores
        .find({"feature_id": feature_id})
        .sort("calculated_at", DESCENDING)
        .limit(safe_limit)
    )

    return [document async for document in cursor]


async def get_workspace_priority_ranking(
    workspace_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Return workspace priority scores from highest to lowest."""

    database = get_database()

    safe_limit = max(1, min(limit, 100))

    cursor = (
        database.priority_scores
        .find({"workspace_id": workspace_id})
        .sort("calculated_score", DESCENDING)
        .limit(safe_limit)
    )

    return [document async for document in cursor]