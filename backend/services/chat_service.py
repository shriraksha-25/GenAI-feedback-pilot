"""Backend orchestration for the Product Intelligence Assistant.

This layer owns database retrieval and conversation persistence; the AI
service remains database-agnostic and is called through ask_assistant().
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Any

from ai.services.product_assistant import ask_assistant
from database.connection import get_database
from database.conversation_repository import (
    add_chat_message,
    create_conversation,
    get_conversation,
    get_conversation_messages,
)
from database.milestone3_models import ChatMessageRecord, ConversationRecord


def _clean_doc(document: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in document.items() if k != "_id"}


async def build_feature_context(workspace_id: str, feature_id: str | None = None) -> dict[str, Any]:
    """Fetch relevant feature, analysis, priority and evidence context from MongoDB."""
    db = get_database()
    feature_query: dict[str, Any] = {"workspace_id": workspace_id}
    if feature_id:
        feature_query["feature_id"] = feature_id
    features = [
        _clean_doc(d) async for d in db.features.find(feature_query).limit(30)
    ]

    feedback_ids: set[str] = set()
    feature_summaries = []
    themes: list[str] = []
    pain_points: list[str] = []
    feature_requests: list[str] = []
    evidence: list[dict[str, str]] = []
    for feature in features:
        fid = feature.get("feature_id")
        for source_id in feature.get("source_feedback_ids") or []:
            if source_id:
                feedback_ids.add(str(source_id))
        title = feature.get("title") or feature.get("feature_name")
        if title:
            feature_requests.append(str(title))
        if feature.get("theme"):
            themes.append(str(feature["theme"]))
        if feature.get("pain_point"):
            pain_points.append(str(feature["pain_point"]))
        feature_summaries.append({
            "feature_id": fid,
            "feature_name": title,
            "description": feature.get("description"),
            "theme": feature.get("theme"),
            "pain_point": feature.get("pain_point"),
            "feature_category": feature.get("feature_category"),
            "status": feature.get("status"),
            "source_feedback_ids": feature.get("source_feedback_ids") or [],
            "priority": feature.get("priority") or feature.get("priority_result"),
        })

    evidence_query: dict[str, Any] = {"workspace_id": workspace_id}
    if feature_id:
        evidence_query["feature_id"] = feature_id
    evidence_docs = [
        _clean_doc(d) async for d in db.feature_evidence.find(evidence_query).limit(100)
    ]
    for item in evidence_docs:
        feedback_id = item.get("feedback_id")
        if feedback_id:
            feedback_ids.add(str(feedback_id))
        evidence.append({
            "feedback_id": str(feedback_id) if feedback_id else "",
            "text": str(item.get("excerpt") or item.get("text") or item.get("pain_point") or ""),
        })

    # Resolve original feedback text only for IDs linked to the requested workspace/features.
    if feedback_ids:
        feedback_docs = [
            _clean_doc(d) async for d in db.feedback.find({
                "workspace_id": workspace_id,
                "feedback_id": {"$in": list(feedback_ids)},
            }).limit(100)
        ]
        existing_ids = {x.get("feedback_id") for x in evidence}
        for record in feedback_docs:
            rid = str(record.get("feedback_id") or "")
            if rid and rid not in existing_ids:
                analysis = record.get("ai_analysis") or {}
                evidence.append({
                    "feedback_id": rid,
                    "text": str(record.get("description") or record.get("feedback_text") or ""),
                })
                if analysis.get("theme"):
                    themes.append(str(analysis["theme"]))
                if analysis.get("pain_point"):
                    pain_points.append(str(analysis["pain_point"]))
                if analysis.get("feature_request"):
                    feature_requests.append(str(analysis["feature_request"]))

    # Only provide actual priority context; do not calculate or invent scores here.
    priority = {}
    if len(features) == 1:
        priority = features[0].get("priority") or features[0].get("priority_result") or {}

    return {
        "feature_id": feature_id,
        "feature_name": feature_summaries[0].get("feature_name") if feature_id and feature_summaries else None,
        "features": feature_summaries,
        "themes": list(dict.fromkeys(themes)),
        "pain_points": list(dict.fromkeys(pain_points)),
        "feature_requests": list(dict.fromkeys(feature_requests)),
        "supporting_evidence": [item for item in evidence if item.get("feedback_id") and item.get("text")],
        "priority": priority,
    }


async def chat_with_assistant(
    *, question: str, workspace_id: str, user_id: str,
    conversation_id: str | None = None, feature_id: str | None = None,
) -> dict[str, Any]:
    """Run a grounded assistant turn while preserving stored conversation history."""
    question = question.strip()
    if not question:
        return {"status": "failed", "answer": None, "grounded": None,
                "referenced_feedback_ids": [], "confidence": None,
                "error": "question is required and cannot be empty.", "messages": []}

    now = datetime.now(timezone.utc)
    if conversation_id:
        conversation = await get_conversation(conversation_id)
        if not conversation or conversation.get("workspace_id") != workspace_id or conversation.get("user_id") != user_id:
            return {"conversation_id": conversation_id, "status": "failed", "answer": None,
                    "grounded": None, "referenced_feedback_ids": [], "confidence": None,
                    "error": "Conversation was not found for this user and workspace.", "messages": []}
    else:
        conversation_id = str(uuid4())
        await create_conversation(ConversationRecord(
            conversation_id=conversation_id, workspace_id=workspace_id, user_id=user_id,
            feature_id=feature_id, title=question[:100], status="active",
        ))

    history = await get_conversation_messages(conversation_id, limit=30)
    history_text = "\n".join(
        f"{item.get('role', 'unknown')}: {item.get('content', '')}"
        for item in history if item.get("role") in {"user", "assistant"}
    )
    context = await build_feature_context(workspace_id, feature_id)
    context["conversation_history"] = history_text or "(no previous messages)"
    question_for_ai = (
        f"Conversation history (for follow-up context only):\n{history_text or '(none)'}\n\n"
        f"Current user question:\n{question}"
    )

    user_message = ChatMessageRecord(
        message_id=str(uuid4()), conversation_id=conversation_id, workspace_id=workspace_id,
        role="user", content=question, feature_id=feature_id,
    )
    await add_chat_message(user_message)

    ai_result = ask_assistant(question_for_ai, context)
    answer = ai_result.get("answer")
    if ai_result.get("status") != "completed" or not answer:
        # Keep a clear, non-fabricated fallback in the existing response contract.
        answer = ("I couldn't generate an AI answer right now. Please check the AI model configuration and try again."
                  if ai_result.get("status") == "not_configured" else
                  "I couldn't generate an answer right now. Please try again.")

    if answer:
        await add_chat_message(ChatMessageRecord(
            message_id=str(uuid4()), conversation_id=conversation_id, workspace_id=workspace_id,
            role="assistant", content=str(answer), feature_id=feature_id,
            source_feedback_ids=ai_result.get("referenced_feedback_ids") or [],
        ))

    updated_history = await get_conversation_messages(conversation_id, limit=30)
    messages = [{k: v for k, v in item.items() if k not in {"_id"}} for item in updated_history]
    return {
        "conversation_id": conversation_id,
        "status": ai_result.get("status", "failed"),
        "answer": answer,
        "grounded": ai_result.get("grounded"),
        "referenced_feedback_ids": ai_result.get("referenced_feedback_ids", []),
        "confidence": ai_result.get("confidence"),
        "error": ai_result.get("error"),
        "messages": messages,
    }
