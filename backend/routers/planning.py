
from fastapi import APIRouter, Depends, HTTPException

from backend.routers.auth import get_current_user
from backend.schemas.planning import (
    CreatePlanningItemRequest,
    UpdatePlanningItemRequest,
)
from backend.services.planning_service import (
    get_planning_items,
    create_planning_item,
    update_planning_item,
)


planning_router = APIRouter(
    prefix="/planning",
    tags=["Product Planning"],
)


@planning_router.get("")
async def list_planning_items(
    current_user: dict = Depends(get_current_user),
):
    return await get_planning_items()


@planning_router.post("")
async def create_plan(
    request: CreatePlanningItemRequest,
    current_user: dict = Depends(get_current_user),
):
    return await create_planning_item(request)


@planning_router.put("/{item_id}")
async def update_plan(
    item_id: str,
    request: UpdatePlanningItemRequest,
    current_user: dict = Depends(get_current_user),
):
    result = await update_planning_item(
        item_id,
        request,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Planning item not found",
        )

    return result
