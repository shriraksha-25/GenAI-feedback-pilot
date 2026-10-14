
"""Product Intelligence Assistant chat service."""

import asyncio
from uuid import uuid4

from ai.services.product_assistant import ask_assistant
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
from database.traceability_queries import get_feature_traceability


def _as_dict(value) -> dict:
    """Normalize MongoDB/Pydantic-style values into a dictionary."""
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="python")
    return {}


def _unique_strings(*groups) -> list[str]:
    """Combine string values without introducing duplicates."""
    result = []
    seen = set()

    for group in groups:
        if isinstance(group, str):
            group = [group]

        for value in group or []:
            if not isinstance(value, str):
                continue

            value = value.strip()
            if value and value not in seen:
                seen.add(value)
                result.append(value)

    return result


def _build_assistant_context(
    traceability: dict | None,
    feature_id: str | None = None,
) -> dict:
    """Convert existing traceability records into the AI context schema."""
    if not traceability:
        return {}

    feature = _as_dict(traceability.get("feature"))
    evidence_records = [
        _as_dict(item)
        for item in (traceability.get("evidence") or [])
    ]
    feedback_records = [
        _as_dict(item)
        for item in (traceability.get("feedback") or [])
    ]

    priority_record = _as_dict(traceability.get("priority"))
    priority_inputs = _as_dict(priority_record.get("inputs"))

    prd_record = _as_dict(traceability.get("prd"))
    prd_content = _as_dict(prd_record.get("content"))

    stories = [
        _as_dict(story)
        for story in (traceability.get("user_stories") or [])
    ]

    feedback_by_id = {
        str(item["feedback_id"]): item
        for item in feedback_records
        if item.get("feedback_id") is not None
    }

    supporting_evidence = []

    for evidence in evidence_records:
        feedback_id = evidence.get("feedback_id")
        feedback_record = (
            feedback_by_id.get(str(feedback_id), {})
            if feedback_id is not None
            else {}
        )

        text = (
            evidence.get("excerpt")
            or feedback_record.get("description")
            or feedback_record.get("text")
            or feedback_record.get("content")
            or feedback_record.get("original_text")
            or ""
        )

        if feedback_id is not None or text:
            supporting_evidence.append({
                "feedback_id": (
                    str(feedback_id)
                    if feedback_id is not None
                    else None
                ),
                "text": str(text),
            })

    evidence_ids = {
        item["feedback_id"]
        for item in supporting_evidence
        if item.get("feedback_id")
    }

    for feedback in feedback_records:
        feedback_id = feedback.get("feedback_id")

        if (
            feedback_id is None
            or str(feedback_id) in evidence_ids
        ):
            continue

        text = (
            feedback.get("description")
            or feedback.get("text")
            or feedback.get("content")
            or feedback.get("original_text")
            or ""
        )

        supporting_evidence.append({
            "feedback_id": str(feedback_id),
            "text": str(text),
        })

    prd_context = {}

    if prd_record:
        prd_context = {
            "title": prd_record.get("title"),
            "risks": prd_content.get("risks") or [],
            "dependencies": prd_content.get("dependencies") or [],
            "overview": prd_content.get("overview"),
            "problem_statement": prd_content.get(
                "problem_statement"
            ),
            "functional_requirements": (
                prd_content.get("functional_requirements") or []
            ),
            "success_metrics": (
                prd_content.get("success_metrics") or []
            ),
            "review_status": prd_record.get("review_status"),
            "version": prd_record.get("version"),
        }

    priority_context = {}

    if priority_record:
        priority_context = {
            "score": priority_record.get("calculated_score"),
            "reach": priority_inputs.get("reach"),
            "impact": priority_inputs.get("impact"),
            "confidence": priority_inputs.get("confidence"),
            "effort": priority_inputs.get("effort"),
            "reasoning": priority_record.get("explanation"),
        }

    themes = _unique_strings(
        feature.get("theme"),
        [item.get("theme") for item in evidence_records],
    )

    pain_points = _unique_strings(
        feature.get("pain_point"),
        [item.get("pain_point") for item in evidence_records],
    )

    feature_requests = _unique_strings(
        feature.get("title"),
        feature.get("description"),
    )

    feature_status = feature.get("status") or "unknown"

    # The context formatter already displays feature_requests.
    # Including the status here ensures the existing AI prompt receives it.
    feature_requests.append(
        f"Current workflow status: {feature_status}"
    )

    return {
        "feature_id": feature_id or feature.get("feature_id"),
        "feature_name": feature.get("title") or "(not provided)",
        "feature_status": feature_status,
        "themes": themes,
        "pain_points": pain_points,
        "feature_requests": feature_requests,
        "feature_opportunity_group": (
            feature.get("feature_opportunity_group")
            or feature.get("feature_opportunity")
            or feature.get("feature_category")
        ),
        "supporting_evidence": supporting_evidence,
        "priority": priority_context,
        "prd": prd_context,
        "user_stories": stories,
    }


def _build_grounded_response(
    user_message: str,
    traceability: dict | None,
) -> str:
    """Provide a deterministic response grounded in database records."""
    if traceability is None:
        return (
            "I could not find product context for the selected feature."
        )

    feature = _as_dict(traceability.get("feature"))
    priority = traceability.get("priority")
    prd = traceability.get("prd")
    user_stories = traceability.get("user_stories") or []
    evidence = traceability.get("evidence") or []
    feedback = traceability.get("feedback") or []

    feature_title = feature.get("title", "The selected feature")
    feature_status = feature.get("status") or "unknown"
    message = user_message.lower()

    status_terms = (
        "status",
        "current state",
        "workflow",
        "progress",
        "stage",
    )

    if any(term in message for term in status_terms):
        return (
            f"{feature_title} currently has workflow status "
            f"'{feature_status}'. There are {len(user_stories)} "
            f"linked user story/stories, {len(feedback)} linked "
            f"feedback record(s), and {len(evidence)} evidence "
            "record(s)."
        )

    if "priority" in message or "rice" in message:
        if priority:
            priority = _as_dict(priority)
            response = (
                f"{feature_title} currently has a priority score of "
                f"{priority.get('calculated_score', 'not available')}."
            )

            if priority.get("explanation"):
                response += f" {priority['explanation']}"

            return response

        return (
            f"No priority score has been calculated for "
            f"{feature_title} yet."
        )

    if "prd" in message or "requirement" in message:
        if prd:
            prd = _as_dict(prd)
            return (
                f"The current PRD for {feature_title} is "
                f"'{prd.get('title', 'Untitled PRD')}', version "
                f"{prd.get('version', 1)}, with review status "
                f"'{prd.get('review_status', 'unknown')}'."
            )

        return f"No PRD is currently available for {feature_title}."

    if any(word in message for word in (
        "story", "stories", "acceptance"
    )):
        return (
            f"{feature_title} currently has {len(user_stories)} "
            "current user story or stories linked to it."
        )

    if "feedback" in message or "evidence" in message:
        return (
            f"{feature_title} is linked to {len(feedback)} feedback "
            f"record(s) and {len(evidence)} evidence record(s). "
            "Only linked records are counted."
        )

    priority_summary = "no priority score"

    if priority:
        priority = _as_dict(priority)
        priority_summary = (
            f"priority score "
            f"{priority.get('calculated_score', 'N/A')}"
        )

    prd_summary = "no PRD"

    if prd:
        prd = _as_dict(prd)
        prd_summary = (
            f"PRD version {prd.get('version', 1)} with status "
            f"{prd.get('review_status', 'unknown')}"
        )

    return (
        f"{feature_title} currently has workflow status "
        f"'{feature_status}', {priority_summary}, {prd_summary}, "
        f"{len(user_stories)} current user story/stories, and "
        f"{len(feedback)} linked feedback record(s)."
    )


async def create_new_conversation(
    workspace_id: str,
    user_id: str,
    feature_id: str | None = None,
    title: str | None = None,
):
    """Create a new conversation."""
    conversation = ConversationRecord(
        conversation_id=str(uuid4()),
        workspace_id=workspace_id,
        user_id=user_id,
        feature_id=feature_id,
        title=title or "Product Intelligence Conversation",
        status="active",
    )

    saved_conversation = await create_conversation(conversation)
    saved_conversation.pop("_id", None)

    return saved_conversation


async def send_message(
    conversation_id: str,
    workspace_id: str,
    content: str,
    feature_id: str | None = None,
    prd_id: str | None = None,
    user_story_id: str | None = None,
):
    """Save a user message and generate an assistant response."""
    content = content.strip()

    if not content:
        raise ValueError("Message content cannot be empty.")

    conversation = await get_conversation(conversation_id)

    if conversation is None:
        raise ValueError("Conversation not found.")

    if conversation.get("workspace_id") != workspace_id:
        raise ValueError(
            "Conversation does not belong to this workspace."
        )

    if conversation.get("status") == "closed":
        raise ValueError("Conversation is already closed.")

    active_feature_id = feature_id or conversation.get("feature_id")

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

    saved_user_message = await add_chat_message(user_message)
    saved_user_message.pop("_id", None)

    traceability = None

    if active_feature_id:
        traceability = await get_feature_traceability(
            active_feature_id
        )

    assistant_content = None
    referenced_feedback_ids = []

    if traceability:
        ai_context = _build_assistant_context(
            traceability,
            feature_id=active_feature_id,
        )

        try:
            ai_result = await asyncio.to_thread(
                ask_assistant,
                content,
                ai_context,
            )

            if (
                ai_result.get("status") == "completed"
                and isinstance(ai_result.get("answer"), str)
                and ai_result["answer"].strip()
            ):
                assistant_content = ai_result["answer"].strip()
                referenced_feedback_ids = (
                    ai_result.get("referenced_feedback_ids") or []
                )

        except Exception:
            # Keep chat available if the AI provider fails.
            assistant_content = None

    if not assistant_content:
        assistant_content = _build_grounded_response(
            user_message=content,
            traceability=traceability,
        )

    if not referenced_feedback_ids and traceability:
        feature = _as_dict(traceability.get("feature"))
        referenced_feedback_ids = (
            feature.get("source_feedback_ids") or []
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
        source_feedback_ids=referenced_feedback_ids,
    )

    saved_assistant_message = await add_chat_message(
        assistant_message
    )
    saved_assistant_message.pop("_id", None)

    return {
        "user_message": saved_user_message,
        "assistant_message": saved_assistant_message,
    }


async def get_full_conversation(conversation_id: str):
    """Return a conversation with its message history."""
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
    """Return conversations belonging to a user and workspace."""
    conversations = await list_user_conversations(
        workspace_id=workspace_id,
        user_id=user_id,
    )

    for conversation in conversations:
        conversation.pop("_id", None)

    return conversations


async def close_existing_conversation(conversation_id: str):
    """Close an existing conversation."""
    conversation = await close_conversation(conversation_id)

    if conversation is None:
        raise ValueError("Conversation not found.")

    conversation.pop("_id", None)

    return conversation
