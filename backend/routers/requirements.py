from fastapi import APIRouter, HTTPException

from backend.schemas.requirements import (
    GeneratePRDRequest,
    PRDReviewRequest,
    GenerateUserStoriesRequest,
    UserStoryReviewRequest,
)
from backend.services.requirements_service import (
    generate_prd_for_feature,
    review_prd,
    get_feature_current_prd,
    get_prd_version_history,
    generate_user_stories_for_feature,
    get_user_story_by_id,
    get_user_story_version_history,
    review_user_story,
)


requirements_router = APIRouter(
    prefix="/requirements",
    tags=["Product Requirements"],
)


# =========================================================
# PRD
# =========================================================

@requirements_router.post("/prd/generate")
async def generate_prd(request: GeneratePRDRequest):
    try:
        return await generate_prd_for_feature(
            feature_id=request.feature_id,
            workspace_id=request.workspace_id,
            requested_by=request.requested_by,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@requirements_router.get("/prd/feature/{feature_id}")
async def get_current_prd(feature_id: str):
    try:
        return await get_feature_current_prd(
            feature_id=feature_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@requirements_router.get("/prd/{prd_id}/history")
async def get_prd_history(prd_id: str):
    try:
        return await get_prd_version_history(
            prd_id=prd_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@requirements_router.patch("/prd/{prd_id}/review")
async def update_prd_review(
    prd_id: str,
    request: PRDReviewRequest,
):
    try:
        return await review_prd(
            prd_id=prd_id,
            status=request.status,
            reviewed_by=request.reviewed_by,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


# =========================================================
# USER STORIES + ACCEPTANCE CRITERIA
# =========================================================

@requirements_router.post("/stories/generate")
async def generate_user_stories(
    request: GenerateUserStoriesRequest,
):
    try:
        return await generate_user_stories_for_feature(
            feature_id=request.feature_id,
            workspace_id=request.workspace_id,
            prd_id=request.prd_id,
            requested_by=request.requested_by,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@requirements_router.get("/stories/{user_story_id}")
async def get_user_story(
    user_story_id: str,
):
    try:
        return await get_user_story_by_id(
            user_story_id=user_story_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@requirements_router.get("/stories/{user_story_id}/history")
async def get_user_story_history(
    user_story_id: str,
):
    try:
        return await get_user_story_version_history(
            user_story_id=user_story_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@requirements_router.patch("/stories/{user_story_id}/review")
async def update_user_story_review(
    user_story_id: str,
    request: UserStoryReviewRequest,
):
    try:
        return await review_user_story(
            user_story_id=user_story_id,
            status=request.status,
            reviewed_by=request.reviewed_by,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )