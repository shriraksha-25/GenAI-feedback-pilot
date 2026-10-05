from fastapi import APIRouter, HTTPException

from backend.services.feature_service import (
    create_feature_opportunity,
    get_feature_opportunity,
    get_feature_opportunities,
)

router = APIRouter(prefix="/features", tags=["Features"])


DEFAULT_WORKSPACE_ID = "default-workspace"


@router.post("")
async def create_feature(data: dict):
    try:
        return await create_feature_opportunity(
            workspace_id=data.get("workspace_id", DEFAULT_WORKSPACE_ID),
            title=data["title"],
            description=data.get("description"),
            theme=data.get("theme"),
            pain_point=data.get("pain_point"),
            feature_category=data.get("feature_category"),
            source_feedback_ids=data.get("source_feedback_ids"),
            created_by=data.get("created_by"),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_features(
    workspace_id: str = DEFAULT_WORKSPACE_ID,
):
    try:
        return await get_feature_opportunities(workspace_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{feature_id}")
async def get_feature(feature_id: str):
    try:
        return await get_feature_opportunity(feature_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))