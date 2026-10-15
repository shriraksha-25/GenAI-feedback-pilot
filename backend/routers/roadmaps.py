from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.routers.auth import get_current_user
from database.milestone4_models import RoadmapStatus, RoadmapVersionRecord
from database.roadmap_repository import (
    save_roadmap_version,
    get_current_roadmap,
    get_roadmap_version,
    get_roadmap_history,
    list_workspace_roadmaps,
    update_roadmap_review_status,
)

roadmap_router = APIRouter(prefix="/roadmaps", tags=["Roadmap Planning"])


class RoadmapReviewRequest(BaseModel):
    status: RoadmapStatus


class GenerateRoadmapRequest(BaseModel):
    workspace_id: str = Field(default="default", min_length=1)
    title: str = Field(default="AI-Generated Product Roadmap", min_length=1)
    milestone_days: int = Field(default=30, ge=1, le=365)
    capacity_per_milestone: float = Field(default=40, gt=0)
    max_milestones: int = Field(default=4, ge=1, le=12)


def clean_document(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: clean_document(item)
            for key, item in value.items()
            if key != "_id"
        }
    if isinstance(value, list):
        return [clean_document(item) for item in value]
    return value


@roadmap_router.post("")
async def create_roadmap(
    request: RoadmapVersionRecord,
    current_user: dict = Depends(get_current_user),
):
    try:
        result = await save_roadmap_version(request)
        return clean_document(result)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@roadmap_router.post("/generate")
async def generate_ai_roadmap(
    request: GenerateRoadmapRequest,
    current_user: dict = Depends(get_current_user),
):
    from ai.services.roadmap_planner import generate_roadmap
    from database.feature_repository import list_features
    from database.feedback_repository import get_analyzed_feedback
    from database.priority_repository import get_workspace_priority_ranking

    try:
        features = await list_features(
            workspace_id=request.workspace_id,
            limit=100,
        )

        if not features:
            raise HTTPException(
                status_code=404,
                detail="No features found for this workspace.",
            )

        # Existing feature records may not contain an effort estimate.
        # Use a clearly marked placeholder so the planner can schedule them.
        for feature in features:
            effort = feature.get("estimated_effort")
            if effort is None or effort <= 0:
                effort = feature.get("effort")
            if effort is None or effort <= 0:
                effort = 1.0

            feature["estimated_effort"] = effort

        feedback = await get_analyzed_feedback(
            workspace_id=request.workspace_id,
            limit=100,
        )

        priority_scores = await get_workspace_priority_ranking(
            workspace_id=request.workspace_id,
            limit=100,
        )

        roadmap = await generate_roadmap(
            features,
            feedback=feedback,
            priority_scores=priority_scores,
            workspace_id=request.workspace_id,
            title=request.title,
            milestone_days=request.milestone_days,
            capacity_per_milestone=request.capacity_per_milestone,
            max_milestones=request.max_milestones,
        )

        saved_roadmap = await save_roadmap_version(roadmap)
        return clean_document(saved_roadmap)

    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"AI roadmap generation failed: {error}",
        ) from error


@roadmap_router.get("")
async def list_roadmaps(
    workspace_id: str = Query(..., min_length=1),
    status: RoadmapStatus | None = None,
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    result = await list_workspace_roadmaps(
        workspace_id=workspace_id,
        status=status,
        limit=limit,
    )
    return clean_document(result)


@roadmap_router.get("/{roadmap_id}/history")
async def roadmap_history(
    roadmap_id: str,
    workspace_id: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user),
):
    result = await get_roadmap_history(
        workspace_id=workspace_id,
        roadmap_id=roadmap_id,
    )
    return clean_document(result)


@roadmap_router.get("/{roadmap_id}/versions/{version}")
async def roadmap_version(
    roadmap_id: str,
    version: int,
    workspace_id: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user),
):
    if version < 1:
        raise HTTPException(
            status_code=400,
            detail="Version must be 1 or greater.",
        )

    result = await get_roadmap_version(
        workspace_id,
        roadmap_id,
        version,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Roadmap version not found.",
        )

    return clean_document(result)


@roadmap_router.get("/{roadmap_id}")
async def current_roadmap(
    roadmap_id: str,
    workspace_id: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user),
):
    result = await get_current_roadmap(
        workspace_id,
        roadmap_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Current roadmap not found.",
        )

    return clean_document(result)


@roadmap_router.patch("/{roadmap_id}/review")
async def review_roadmap(
    roadmap_id: str,
    request: RoadmapReviewRequest,
    workspace_id: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user),
):
    result = await update_roadmap_review_status(
        workspace_id=workspace_id,
        roadmap_id=roadmap_id,
        status=request.status,
        reviewed_by=current_user.get("email", "unknown"),
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Current roadmap not found.",
        )

    return clean_document(result)

