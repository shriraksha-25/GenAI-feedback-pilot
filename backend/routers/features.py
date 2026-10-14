
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.feature_service import (
    create_feature_opportunity,
    get_feature_opportunity,
    get_feature_opportunities,
)
from database.connection import get_database
from database.feature_repository import (
    add_feature_evidence,
    get_feature_by_id,
    get_feature_evidence,
)

router = APIRouter(prefix="/features", tags=["Features"])

DEFAULT_WORKSPACE_ID = "default-workspace"


class LinkEvidenceRequest(BaseModel):
    feedback_ids: list[str] = Field(min_length=1)
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)


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


@router.post("/{feature_id}/evidence")
async def link_feature_evidence(
    feature_id: str,
    payload: LinkEvidenceRequest,
):
    feature = await get_feature_by_id(feature_id)

    if feature is None:
        raise HTTPException(status_code=404, detail="Feature not found")

    database = get_database()
    existing_evidence = await get_feature_evidence(feature_id)
    existing_feedback_ids = {
        item.get("feedback_id") for item in existing_evidence
    }

    linked = []
    skipped = []

    for feedback_id in payload.feedback_ids:
        if feedback_id in existing_feedback_ids:
            skipped.append(feedback_id)
            continue

        feedback = await database.feedback.find_one(
            {"feedback_id": feedback_id}
        )

        if feedback is None:
            raise HTTPException(
                status_code=404,
                detail=f"Feedback not found: {feedback_id}",
            )

        analysis = feedback.get("ai_analysis") or {}
        if not isinstance(analysis, dict):
            analysis = {}

        description = (
            feedback.get("description")
            or feedback.get("content")
            or feedback.get("text")
        )

        evidence = {
            "evidence_id": str(uuid4()),
            "workspace_id": feature["workspace_id"],
            "feature_id": feature_id,
            "feedback_id": feedback_id,
            "theme": (
                analysis.get("theme")
                or feedback.get("theme")
                or feature.get("theme")
            ),
            "pain_point": (
                analysis.get("pain_point")
                or feedback.get("pain_point")
                or feature.get("pain_point")
            ),
            "excerpt": description,
            "relevance_score": payload.relevance_score,
        }

        saved = await add_feature_evidence(evidence)
        linked.append({
            "feedback_id": feedback_id,
            "evidence_id": saved["evidence_id"],
        })
        existing_feedback_ids.add(feedback_id)

    updated_feature = await get_feature_by_id(feature_id)

    return {
        "message": "Feature evidence linking completed",
        "feature_id": feature_id,
        "source_feedback_ids": updated_feature.get(
            "source_feedback_ids", []
        ),
        "linked": linked,
        "skipped_already_linked": skipped,
    }
