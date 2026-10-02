from fastapi import APIRouter, HTTPException, Query

from backend.schemas.chat import (
    CreateConversationRequest,
    SendChatMessageRequest,
)
from backend.services.chat_service import (
    create_new_conversation,
    send_message,
    get_full_conversation,
    get_user_conversation_list,
    close_existing_conversation,
)


chat_router = APIRouter(
    prefix="/chat",
    tags=["Product Intelligence Assistant"],
)


@chat_router.post("/conversations")
async def create_conversation(
    request: CreateConversationRequest,
):
    try:
        return await create_new_conversation(
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            feature_id=request.feature_id,
            title=request.title,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@chat_router.post(
    "/conversations/{conversation_id}/messages"
)
async def send_conversation_message(
    conversation_id: str,
    request: SendChatMessageRequest,
):
    try:
        return await send_message(
            conversation_id=conversation_id,
            workspace_id=request.workspace_id,
            content=request.content,
            feature_id=request.feature_id,
            prd_id=request.prd_id,
            user_story_id=request.user_story_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@chat_router.get(
    "/conversations/{conversation_id}"
)
async def get_conversation(
    conversation_id: str,
):
    try:
        return await get_full_conversation(
            conversation_id=conversation_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@chat_router.get("/conversations")
async def list_conversations(
    workspace_id: str = Query(..., min_length=1),
    user_id: str = Query(..., min_length=1),
):
    return await get_user_conversation_list(
        workspace_id=workspace_id,
        user_id=user_id,
    )


@chat_router.patch(
    "/conversations/{conversation_id}/close"
)
async def close_conversation(
    conversation_id: str,
):
    try:
        return await close_existing_conversation(
            conversation_id=conversation_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )