"""
ai/services/product_assistant.py
===================================
PUBLIC INTERFACE for the Product Intelligence Assistant.

    from ai.services.product_assistant import ask_assistant

    result = ask_assistant(
        question="What customer feedback supports this feature?",
        context={...},  # FeatureContext-shaped, see ai/agents/context.py
    )
    # result["answer"], result["grounded"], result["referenced_feedback_ids"]

SCOPE REMINDER: this answers INFORMATIONAL questions grounded in
supplied context. It does not generate PRDs/user stories itself from a
chat message - see ai/agents/assistant_crew.py's module docstring for
why, and call ai.services.prd_generator.generate_prd() /
ai.services.user_story_generator.generate_user_stories() directly for
those actions instead.
"""

from __future__ import annotations

import logging
from typing import Optional

from ai.agents.assistant_crew import run_assistant_crew
from ai.agents.llm import LLMNotConfiguredError

logger = logging.getLogger("ai.services.product_assistant")


def ask_assistant(question: str, context: Optional[dict] = None) -> dict:
    """
    Answer one question using the supplied project context.

    Parameters
    ----------
    question:
        The PM's question, as free text. Required.
    context:
        FeatureContext-shaped dict (see ai.agents.context) - whatever
        themes/pain_points/feature_requests/supporting_evidence/prd/
        user_stories/priority info is relevant to this question. It is
        entirely the backend's responsibility to decide what's
        relevant and pass it in - this function does no retrieval of
        its own (see ai/agents/assistant_crew.py for why no RAG/vector
        DB is used at this project's scale).

    Returns
    -------
    dict, always with these keys:
        {
            "status": "completed" | "failed" | "not_configured",
            "answer": <str or None>,
            "grounded": <bool or None>,         # False if the context didn't support an answer
            "referenced_feedback_ids": <list[str]>,
            "confidence": <float or None>,
            "error": <str>,  # only if status != "completed"
        }

    Never raises. Rejects empty questions the same way
    ai.services.feedback_analyzer.analyze_feedback() rejects empty
    feedback text - with a clear status, not an exception.
    """
    if not question or not question.strip():
        return {
            "status": "failed",
            "answer": None,
            "grounded": None,
            "referenced_feedback_ids": [],
            "confidence": None,
            "error": "question is required and cannot be empty.",
        }

    try:
        result = run_assistant_crew(question, context or {})
    except LLMNotConfiguredError as exc:
        logger.info("Assistant query skipped: %s", exc)
        return {
            "status": "not_configured",
            "answer": None,
            "grounded": None,
            "referenced_feedback_ids": [],
            "confidence": None,
            "error": str(exc),
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Assistant query failed: %s", exc, exc_info=True)
        return {
            "status": "failed",
            "answer": None,
            "grounded": None,
            "referenced_feedback_ids": [],
            "confidence": None,
            "error": f"{type(exc).__name__}: {exc}",
        }

    logger.info("Assistant answered question (grounded=%s)", result.grounded)
    return {
        "status": "completed",
        "answer": result.answer,
        "grounded": result.grounded,
        "referenced_feedback_ids": result.referenced_feedback_ids,
        "confidence": result.confidence,
    }
