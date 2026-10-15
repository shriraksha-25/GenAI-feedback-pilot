from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.routers.auth import get_current_user
from database.milestone4_models import (
    ExecutiveSummaryVersionRecord,
    RoadmapStatus,
)
from database.executive_summary_repository import (
    save_executive_summary_version,
    get_current_executive_summary,
    get_executive_summary_version,
    get_executive_summary_history,
    list_roadmap_summaries,
    update_executive_summary_status,
)

executive_summary_router = APIRouter(
    prefix="/executive-summaries",
    tags=["Executive Summaries"],
)


class ExecutiveSummaryReviewRequest(BaseModel):
    status: RoadmapStatus


class GenerateExecutiveSummaryRequest(BaseModel):
    workspace_id: str = Field(min_length=1)
    roadmap_id: str = Field(min_length=1)


def clean_document(value: Any) -> Any:
    """Remove MongoDB internal IDs from API responses."""
    if isinstance(value, dict):
        return {
            key: clean_document(item)
            for key, item in value.items()
            if key != "_id"
        }

    if isinstance(value, list):
        return [clean_document(item) for item in value]

    return value


@executive_summary_router.post("")
async def create_executive_summary(
    request: ExecutiveSummaryVersionRecord,
    current_user: dict = Depends(get_current_user),
):
    try:
        result = await save_executive_summary_version(request)
        return clean_document(result)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@executive_summary_router.post("/generate")
async def generate_ai_executive_summary(
    request: GenerateExecutiveSummaryRequest,
    current_user: dict = Depends(get_current_user),
):
    from ai.services.executive_summary_generator import (
        generate_executive_summary,
    )
    from database.feature_repository import list_features
    from database.feedback_repository import get_analyzed_feedback
    from database.roadmap_repository import get_current_roadmap

    try:
        roadmap = await get_current_roadmap(
            workspace_id=request.workspace_id,
            roadmap_id=request.roadmap_id,
        )

        if roadmap is None:
            raise HTTPException(
                status_code=404,
                detail="Current roadmap not found.",
            )

        features = await list_features(
            workspace_id=request.workspace_id,
            limit=100,
        )

        feedback = await get_analyzed_feedback(
            workspace_id=request.workspace_id,
            limit=100,
        )

        # CrewAI generation is async; await it inside this async route.
        result = await generate_executive_summary(
            roadmap,
            features=features,
            feedback=feedback,
            workspace_id=request.workspace_id,
            roadmap_id=request.roadmap_id,
        )

        if not isinstance(result, dict):
            raise HTTPException(
                status_code=500,
                detail="Executive summary generator returned an invalid result.",
            )

        if result.get("status") != "completed":
            status = result.get("status", "failed")
            error_detail = (
                result.get("error")
                or result.get("message")
                or f"Executive summary generation status: {status}"
            )
            status_code = 503 if status == "not_configured" else 500

            raise HTTPException(
                status_code=status_code,
                detail=str(error_detail),
            )

        summary = result.get("summary")

        if not isinstance(summary, dict):
            raise HTTPException(
                status_code=500,
                detail="Generated executive summary is missing.",
            )

        summary = dict(summary)
        summary["workspace_id"] = request.workspace_id
        summary["roadmap_id"] = request.roadmap_id
        summary["roadmap_version"] = roadmap.get("version", 1)

        saved_summary = await save_executive_summary_version(summary)
        return clean_document(saved_summary)

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
            detail=f"Executive summary generation failed: {error}",
        ) from error


@executive_summary_router.get("")
async def list_executive_summaries(
    workspace_id: str = Query(..., min_length=1),
    roadmap_id: str = Query(..., min_length=1),
    current_only: bool = True,
    current_user: dict = Depends(get_current_user),
):
    result = await list_roadmap_summaries(
        workspace_id=workspace_id,
        roadmap_id=roadmap_id,
        current_only=current_only,
    )
    return clean_document(result)


@executive_summary_router.get("/{summary_id}/history")
async def executive_summary_history(
    summary_id: str,
    workspace_id: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user),
):
    result = await get_executive_summary_history(
        workspace_id=workspace_id,
        summary_id=summary_id,
    )
    return clean_document(result)


@executive_summary_router.get("/{summary_id}/versions/{version}")
async def executive_summary_version(
    summary_id: str,
    version: int,
    workspace_id: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user),
):
    if version < 1:
        raise HTTPException(
            status_code=400,
            detail="Version must be 1 or greater.",
        )

    result = await get_executive_summary_version(
        workspace_id=workspace_id,
        summary_id=summary_id,
        version=version,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Executive summary version not found.",
        )

    return clean_document(result)


@executive_summary_router.patch("/{summary_id}/review")
async def review_executive_summary(
    summary_id: str,
    request: ExecutiveSummaryReviewRequest,
    workspace_id: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user),
):
    result = await update_executive_summary_status(
        workspace_id=workspace_id,
        summary_id=summary_id,
        status=request.status,
        reviewed_by=current_user.get("email", "unknown"),
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Current executive summary not found.",
        )

    return clean_document(result)


@executive_summary_router.get("/{summary_id}")
async def current_executive_summary(
    summary_id: str,
    workspace_id: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user),
):
    result = await get_current_executive_summary(
        workspace_id=workspace_id,
        summary_id=summary_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Current executive summary not found.",
        )

    return clean_document(result)
