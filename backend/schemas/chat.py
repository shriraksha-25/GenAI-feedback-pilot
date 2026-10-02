from typing import Optional

from pydantic import BaseModel, Field


class CreateConversationRequest(BaseModel):
    workspace_id: str = Field(
        ...,
        min_length=1,
    )

    user_id: str = Field(
        ...,
        min_length=1,
    )

    feature_id: Optional[str] = None

    title: Optional[str] = None


class SendChatMessageRequest(BaseModel):
    workspace_id: str = Field(
        ...,
        min_length=1,
    )

    content: str = Field(
        ...,
        min_length=1,
    )

    feature_id: Optional[str] = None

    prd_id: Optional[str] = None

    user_story_id: Optional[str] = None


class ListConversationsRequest(BaseModel):
    workspace_id: str = Field(
        ...,
        min_length=1,
    )

    user_id: str = Field(
        ...,
        min_length=1,
    )