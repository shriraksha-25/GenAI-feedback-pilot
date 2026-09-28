"""Conversation history for the Product Intelligence Assistant."""

from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING, DESCENDING, ReturnDocument

from database.connection import get_database
from database.milestone3_models import (
    ChatMessageRecord,
    ConversationRecord,
)


async def create_conversation(
    conversation: ConversationRecord | dict[str, Any],
) -> dict[str, Any]:
    """Create a Product Intelligence Assistant conversation."""

    database = get_database()

    conversation_model = (
        conversation
        if isinstance(conversation, ConversationRecord)
        else ConversationRecord.model_validate(conversation)
    )

    document = conversation_model.model_dump(mode="python")
    await database.conversations.insert_one(document)

    return document


async def get_conversation(
    conversation_id: str,
) -> dict[str, Any] | None:
    """Retrieve one conversation."""

    database = get_database()

    return await database.conversations.find_one(
        {"conversation_id": conversation_id}
    )


async def list_user_conversations(
    workspace_id: str,
    user_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Retrieve a user's conversations within a workspace."""

    database = get_database()
    safe_limit = max(1, min(limit, 100))

    cursor = (
        database.conversations
        .find(
            {
                "workspace_id": workspace_id,
                "user_id": user_id,
            }
        )
        .sort("updated_at", DESCENDING)
        .limit(safe_limit)
    )

    return [document async for document in cursor]


async def add_chat_message(
    message: ChatMessageRecord | dict[str, Any],
) -> dict[str, Any]:
    """Store a message and update the conversation timestamp."""

    database = get_database()

    message_model = (
        message
        if isinstance(message, ChatMessageRecord)
        else ChatMessageRecord.model_validate(message)
    )

    conversation = await database.conversations.find_one(
        {
            "conversation_id": message_model.conversation_id,
            "workspace_id": message_model.workspace_id,
        }
    )

    if conversation is None:
        raise ValueError("Conversation does not exist.")

    document = message_model.model_dump(mode="python")
    await database.chat_messages.insert_one(document)

    await database.conversations.update_one(
        {"conversation_id": message_model.conversation_id},
        {
            "$set": {
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    return document


async def get_conversation_messages(
    conversation_id: str,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Retrieve messages in chronological order."""

    database = get_database()
    safe_limit = max(1, min(limit, 500))

    cursor = (
        database.chat_messages
        .find({"conversation_id": conversation_id})
        .sort("created_at", ASCENDING)
        .limit(safe_limit)
    )

    return [document async for document in cursor]


async def get_conversation_with_messages(
    conversation_id: str,
) -> dict[str, Any] | None:
    """Retrieve a conversation and all its messages."""

    conversation = await get_conversation(conversation_id)

    if conversation is None:
        return None

    conversation["messages"] = await get_conversation_messages(
        conversation_id
    )

    return conversation


async def close_conversation(
    conversation_id: str,
) -> dict[str, Any] | None:
    """Mark a conversation as closed."""

    database = get_database()

    return await database.conversations.find_one_and_update(
        {"conversation_id": conversation_id},
        {
            "$set": {
                "status": "closed",
                "updated_at": datetime.now(timezone.utc),
            }
        },
        return_document=ReturnDocument.AFTER,
    )