from uuid import uuid4

from database.feature_repository import get_feature_with_evidence
from database.milestone3_models import (
    PriorityConfigurationRecord,
    PriorityInputs,
    PriorityScoreRecord,
)
from database.priority_repository import (
    create_priority_configuration,
    get_active_priority_configuration,
    get_latest_priority_score,
    get_priority_history,
    get_workspace_priority_ranking,
    save_priority_score,
)


DEFAULT_RICE_WEIGHTS = {
    "reach": 1.0,
    "impact": 1.0,
    "confidence": 1.0,
    "effort": 1.0,
}


async def create_priority_config(
    workspace_id: str,
    name: str,
    method: str = "RICE",
    weights: dict[str, float] | None = None,
    created_by: str | None = None,
):
    if method.upper() != "RICE":
        raise ValueError(
            "Only RICE prioritization is currently supported."
        )

    configuration = PriorityConfigurationRecord(
        configuration_id=str(uuid4()),
        workspace_id=workspace_id,
        name=name,
        method="RICE",
        weights=weights or DEFAULT_RICE_WEIGHTS,
        is_active=True,
        created_by=created_by,
    )

    saved_configuration = await create_priority_configuration(
        configuration
    )

    saved_configuration.pop("_id", None)

    return saved_configuration


async def get_workspace_active_config(
    workspace_id: str,
):
    configuration = await get_active_priority_configuration(
        workspace_id
    )

    if configuration is None:
        raise ValueError(
            "No active priority configuration found."
        )

    configuration.pop("_id", None)

    return configuration


async def calculate_feature_priority(
    workspace_id: str,
    feature_id: str,
    reach: float,
    impact: float,
    confidence: float,
    effort: float,
    calculated_by: str | None = None,
):
    feature = await get_feature_with_evidence(feature_id)

    if feature is None:
        raise ValueError("Feature not found.")

    if feature.get("workspace_id") != workspace_id:
        raise ValueError(
            "Feature does not belong to the requested workspace."
        )

    active_configuration = (
        await get_active_priority_configuration(
            workspace_id
        )
    )

    configuration_id = None
    method = "RICE"
    weights = None

    if active_configuration:
        configuration_id = active_configuration.get(
            "configuration_id"
        )

        method = active_configuration.get(
            "method",
            "RICE",
        )

        weights = active_configuration.get(
            "weights"
        )

    inputs = PriorityInputs(
        reach=reach,
        impact=impact,
        confidence=confidence,
        effort=effort,
    )

    priority_record = PriorityScoreRecord(
        priority_score_id=str(uuid4()),
        workspace_id=workspace_id,
        feature_id=feature_id,
        configuration_id=configuration_id,
        method=method,
        inputs=inputs,
        calculated_by=calculated_by,
    )

    saved_score = await save_priority_score(
        priority_record,
        weights=weights,
    )

    saved_score.pop("_id", None)

    return saved_score


async def get_feature_latest_priority(
    feature_id: str,
):
    score = await get_latest_priority_score(
        feature_id
    )

    if score is None:
        raise ValueError(
            "Priority score not found for this feature."
        )

    score.pop("_id", None)

    return score


async def get_feature_priority_history(
    feature_id: str,
):
    history = await get_priority_history(
        feature_id
    )

    if not history:
        raise ValueError(
            "Priority history not found for this feature."
        )

    for item in history:
        item.pop("_id", None)

    return history


async def get_workspace_ranking(
    workspace_id: str,
):
    ranking = await get_workspace_priority_ranking(
        workspace_id
    )

    for position, item in enumerate(
        ranking,
        start=1,
    ):
        item.pop("_id", None)
        item["rank"] = position

    return ranking