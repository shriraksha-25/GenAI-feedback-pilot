from uuid import uuid4

from database.conversation_repository import (
    add_chat_message,
    close_conversation,
    create_conversation,
    get_conversation,
    get_conversation_with_messages,
    list_user_conversations,
)
from database.milestone3_models import (
    ChatMessageRecord,
    ConversationRecord,
)
from database.traceability_queries import (
    get_feature_traceability,
)


async def create_new_conversation(
    workspace_id: str,
    user_id: str,
    feature_id: str | None = None,
    title: str | None = None,
):
    conversation = ConversationRecord(
        conversation_id=str(uuid4()),
        workspace_id=workspace_id,
        user_id=user_id,
        feature_id=feature_id,
        title=title or "Product Intelligence Conversation",
        status="active",
    )

    saved_conversation = await create_conversation(
        conversation
    )

    saved_conversation.pop("_id", None)

    return saved_conversation


def _build_grounded_response(
    user_message: str,
    traceability: dict | None,
) -> str:
    """
    Temporary grounded assistant.

    This provides deterministic responses using workspace data
    until the Milestone 3 AI conversational module is integrated.
    """

    if traceability is None:
        return (
            "I could not find product context for the selected feature."
        )

    feature = traceability.get("feature") or {}
    priority = traceability.get("priority")
    prd = traceability.get("prd")
    user_stories = traceability.get("user_stories") or []
    evidence = traceability.get("evidence") or []
    feedback = traceability.get("feedback") or []

    feature_title = feature.get(
        "title",
        "the selected feature",
    )

    message = user_message.lower()

    if "priority" in message or "rice" in message:
        if priority:
            score = priority.get(
                "calculated_score",
                "not available",
            )

            explanation = priority.get(
                "explanation"
            )

            response = (
                f"{feature_title} currently has a "
                f"priority score of {score}."
            )

            if explanation:
                response += f" {explanation}"

            return response

        return (
            f"No priority score has been calculated "
            f"for {feature_title} yet."
        )

    if "prd" in message or "requirement" in message:
        if prd:
            return (
                f"The current PRD for {feature_title} is "
                f"'{prd.get('title', 'Untitled PRD')}', "
                f"version {prd.get('version', 1)}, "
                f"with review status "
                f"'{prd.get('review_status', 'unknown')}'."
            )

        return (
            f"No PRD is currently available "
            f"for {feature_title}."
        )

    if (
        "story" in message
        or "stories" in message
        or "acceptance" in message
    ):
        return (
            f"{feature_title} currently has "
            f"{len(user_stories)} current user "
            f"story or stories linked to it."
        )

    if (
        "feedback" in message
        or "evidence" in message
    ):
        return (
            f"{feature_title} is linked to "
            f"{len(feedback)} feedback record(s) "
            f"and {len(evidence)} evidence record(s)."
        )

    priority_summary = "no priority score"

    if priority:
        priority_summary = (
            f"priority score "
            f"{priority.get('calculated_score', 'N/A')}"
        )

    prd_summary = "no PRD"

    if prd:
        prd_summary = (
            f"PRD version {prd.get('version', 1)} "
            f"with status "
            f"{prd.get('review_status', 'unknown')}"
        )

    return (
        f"{feature_title} currently has "
        f"{priority_summary}, {prd_summary}, "
        f"{len(user_stories)} current user story/stories, "
        f"and {len(feedback)} linked feedback record(s)."
    )


async def send_message(
    conversation_id: str,
    workspace_id: str,
    content: str,
    feature_id: str | None = None,
    prd_id: str | None = None,
    user_story_id: str | None = None,
):
    conversation = await get_conversation(
        conversation_id
    )

    if conversation is None:
        raise ValueError("Conversation not found.")

    if conversation.get("workspace_id") != workspace_id:
        raise ValueError(
            "Conversation does not belong to this workspace."
        )

    if conversation.get("status") == "closed":
        raise ValueError(
            "Conversation is already closed."
        )

    active_feature_id = (
        feature_id
        or conversation.get("feature_id")
    )

    user_message = ChatMessageRecord(
        message_id=str(uuid4()),
        conversation_id=conversation_id,
        workspace_id=workspace_id,
        role="user",
        content=content,
        feature_id=active_feature_id,
        prd_id=prd_id,
        user_story_id=user_story_id,
        source_feedback_ids=[],
    )

    saved_user_message = await add_chat_message(
        user_message
    )

    saved_user_message.pop("_id", None)

    traceability = None

    if active_feature_id:
        traceability = await get_feature_traceability(
            active_feature_id
        )

    assistant_content = _build_grounded_response(
        user_message=content,
        traceability=traceability,
    )

    source_feedback_ids = []

    if traceability:
        feature = traceability.get("feature") or {}

        source_feedback_ids = feature.get(
            "source_feedback_ids",
            [],
        )

    assistant_message = ChatMessageRecord(
        message_id=str(uuid4()),
        conversation_id=conversation_id,
        workspace_id=workspace_id,
        role="assistant",
        content=assistant_content,
        feature_id=active_feature_id,
        prd_id=prd_id,
        user_story_id=user_story_id,
        source_feedback_ids=source_feedback_ids,
    )

    saved_assistant_message = await add_chat_message(
        assistant_message
    )

    saved_assistant_message.pop("_id", None)

    return {
        "user_message": saved_user_message,
        "assistant_message": saved_assistant_message,
    }


async def get_full_conversation(
    conversation_id: str,
):
    conversation = await get_conversation_with_messages(
        conversation_id
    )

    if conversation is None:
        raise ValueError("Conversation not found.")

    conversation.pop("_id", None)

    for message in conversation.get("messages", []):
        message.pop("_id", None)

    return conversation


async def get_user_conversation_list(
    workspace_id: str,
    user_id: str,
):
    conversations = await list_user_conversations(
        workspace_id=workspace_id,
        user_id=user_id,
    )

    for conversation in conversations:
        conversation.pop("_id", None)

    return conversations


async def close_existing_conversation(
    conversation_id: str,
):
    conversation = await close_conversation(
        conversation_id
    )

    if conversation is None:
        raise ValueError("Conversation not found.")

    conversation.pop("_id", None)

    return conversation