from fastapi import APIRouter, HTTPException

from backend.schemas.requirements import (
    CreatePriorityConfigurationRequest,
    CalculatePriorityRequest,
)
from backend.services.priority_service import (
    create_priority_config,
    get_workspace_active_config,
    calculate_feature_priority,
    get_feature_latest_priority,
    get_feature_priority_history,
    get_workspace_ranking,
)


priority_router = APIRouter(
    prefix="/priority",
    tags=["Feature Prioritization"],
)


@priority_router.post("/configuration")
async def create_configuration(
    request: CreatePriorityConfigurationRequest,
):
    try:
        return await create_priority_config(
            workspace_id=request.workspace_id,
            name=request.name,
            method=request.method,
            weights=request.weights,
            created_by=request.created_by,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@priority_router.get("/configuration/{workspace_id}")
async def get_active_configuration(
    workspace_id: str,
):
    try:
        return await get_workspace_active_config(
            workspace_id=workspace_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@priority_router.post("/calculate")
async def calculate_priority(
    request: CalculatePriorityRequest,
):
    try:
        return await calculate_feature_priority(
            workspace_id=request.workspace_id,
            feature_id=request.feature_id,
            reach=request.reach,
            impact=request.impact,
            confidence=request.confidence,
            effort=request.effort,
            calculated_by=request.calculated_by,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@priority_router.get("/feature/{feature_id}")
async def get_latest_priority(
    feature_id: str,
):
    try:
        return await get_feature_latest_priority(
            feature_id=feature_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@priority_router.get("/feature/{feature_id}/history")
async def get_priority_history(
    feature_id: str,
):
    try:
        return await get_feature_priority_history(
            feature_id=feature_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@priority_router.get("/ranking/{workspace_id}")
async def get_priority_ranking(
    workspace_id: str,
):
    return await get_workspace_ranking(
        workspace_id=workspace_id,
    )