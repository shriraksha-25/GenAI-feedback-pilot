"""What-If Roadmap Simulator persistence."""

from datetime import datetime, timezone
from typing import Any

from pymongo import DESCENDING, ReturnDocument

from database.connection import get_database
from database.milestone4_models import (
    RoadmapComparisonMetrics,
    RoadmapSimulationRecord,
)


async def create_roadmap_simulation(
    simulation: RoadmapSimulationRecord | dict[str, Any],
) -> dict[str, Any]:
    """Create a saved what-if roadmap scenario."""

    database = get_database()

    simulation_model = (
        simulation
        if isinstance(simulation, RoadmapSimulationRecord)
        else RoadmapSimulationRecord.model_validate(
            simulation
        )
    )

    base_roadmap = await database.roadmaps.find_one(
        {
            "workspace_id": simulation_model.workspace_id,
            "roadmap_id": simulation_model.roadmap_id,
            "version": simulation_model.base_roadmap_version,
        },
        {"_id": 1, "source_feature_ids": 1},
    )

    if base_roadmap is None:
        raise ValueError(
            "The base roadmap version does not exist "
            "in this workspace."
        )

    known_feature_ids = set(
        base_roadmap.get("source_feature_ids", [])
    )

    changed_feature_ids = set(
        simulation_model.delayed_feature_ids
    ) | set(simulation_model.removed_feature_ids)

    unknown_feature_ids = (
        changed_feature_ids - known_feature_ids
    )

    if unknown_feature_ids:
        unknown_text = ", ".join(
            sorted(unknown_feature_ids)
        )
        raise ValueError(
            "Simulation contains features that are not "
            f"in the base roadmap: {unknown_text}"
        )

    document = simulation_model.model_dump(
        mode="python"
    )
    document["created_at"] = datetime.now(timezone.utc)

    await database.roadmap_simulations.insert_one(
        document
    )

    return document


async def get_roadmap_simulation(
    workspace_id: str,
    simulation_id: str,
) -> dict[str, Any] | None:
    """Retrieve one simulation with workspace isolation."""

    database = get_database()

    return await database.roadmap_simulations.find_one(
        {
            "workspace_id": workspace_id,
            "simulation_id": simulation_id,
        }
    )


async def save_simulation_result(
    workspace_id: str,
    simulation_id: str,
    result_roadmap_version: int,
    comparison: RoadmapComparisonMetrics
    | dict[str, Any],
) -> dict[str, Any] | None:
    """Link a generated roadmap version to a simulation."""

    database = get_database()

    simulation = await database.roadmap_simulations.find_one(
        {
            "workspace_id": workspace_id,
            "simulation_id": simulation_id,
        }
    )

    if simulation is None:
        return None

    result_roadmap = await database.roadmaps.find_one(
        {
            "workspace_id": workspace_id,
            "roadmap_id": simulation["roadmap_id"],
            "version": result_roadmap_version,
            "roadmap_type": "what_if",
        },
        {"_id": 1},
    )

    if result_roadmap is None:
        raise ValueError(
            "The what-if roadmap version does not exist."
        )

    comparison_model = (
        comparison
        if isinstance(
            comparison,
            RoadmapComparisonMetrics,
        )
        else RoadmapComparisonMetrics.model_validate(
            comparison
        )
    )

    return (
        await database.roadmap_simulations
        .find_one_and_update(
            {
                "workspace_id": workspace_id,
                "simulation_id": simulation_id,
            },
            {
                "$set": {
                    "result_roadmap_version": (
                        result_roadmap_version
                    ),
                    "comparison": (
                        comparison_model.model_dump(
                            mode="python"
                        )
                    ),
                }
            },
            return_document=ReturnDocument.AFTER,
        )
    )


async def list_roadmap_simulations(
    workspace_id: str,
    roadmap_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List simulations created for a roadmap."""

    database = get_database()
    safe_limit = max(1, min(limit, 100))

    cursor = (
        database.roadmap_simulations
        .find(
            {
                "workspace_id": workspace_id,
                "roadmap_id": roadmap_id,
            }
        )
        .sort("created_at", DESCENDING)
        .limit(safe_limit)
    )

    return [document async for document in cursor]
