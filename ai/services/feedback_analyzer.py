"""
ai/services/feedback_analyzer.py
===================================
THE PUBLIC INTERFACE OF THE AI MODULE.

This is the ONLY file the backend teammate should ever need to import
from. Everything else in `ai/` (pandas, cleaning internals, file
paths, dataset loading) is an implementation detail the backend does
not need to know about.

    from ai.services.feedback_analyzer import analyze_feedback

    result = analyze_feedback(
        text="Payment failed during checkout",
        feedback_id="123",
        metadata={"source": "support_ticket", "product": "Mobile App"},
    )

See docs/AI_INTEGRATION.md for the full contract, and the docstring
below for the exact Milestone 1 output shape.
"""

from __future__ import annotations

import logging
from typing import Optional

from ai.preprocessing.cleaning import clean_text, is_text_usable
from ai.config.config import MIN_DESCRIPTION_LENGTH

logger = logging.getLogger("ai.services.feedback_analyzer")


def analyze_feedback(
    text: str,
    feedback_id: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Process one piece of feedback text and return a structured,
    JSON-compatible result.

    Parameters
    ----------
    text:
        The raw feedback/ticket description text. Required.
    feedback_id:
        Optional caller-supplied ID (e.g. a MongoDB _id or a ticket
        number), echoed back unchanged so the backend can match the
        result to its own record. If omitted, the output's
        `feedback_id` will be None — the caller is responsible for
        tracking which request this result belongs to in that case.
    metadata:
        Optional dict of extra context (e.g. {"product": "...",
        "source": "support_ticket"}). Not used by any Milestone 1
        logic yet, but accepted now so the function signature does not
        need to change when Milestone 2 starts using it (e.g. product
        category might influence sentiment interpretation later).

    Returns
    -------
    dict — MILESTONE 1 SHAPE (this is what is actually implemented):
        {
            "feedback_id": <str or None>,
            "cleaned_text": <str>,
            "status": "processed" | "rejected",
            "error": <str, only present if status == "rejected">
        }

    PLANNED FUTURE SHAPE (Milestone 2+, NOT implemented here — do not
    assume these keys exist yet):
        {
            "feedback_id": "123",
            "cleaned_text": "Payment failed during checkout",
            "status": "processed",
            "sentiment": "negative",
            "category": "payment",
            "theme": "payment failure",
            "pain_point": "customers cannot complete payments",
            "feature_opportunity": "improved payment recovery"
        }

    Error handling
    --------------
    This function never raises for bad INPUT (None, empty string,
    wrong type, whitespace-only text) — it always returns a dict, with
    `status: "rejected"` and an `error` message, so one bad record from
    the backend can never crash the caller. It only raises if something
    genuinely unexpected happens internally (a real bug), which the
    caller should treat as a 500-level error, not a validation failure.
    """
    if not isinstance(text, str) or not text.strip():
        logger.info("Rejected feedback %s: empty or non-string text", feedback_id)
        return {
            "feedback_id": feedback_id,
            "cleaned_text": "",
            "status": "rejected",
            "error": "text is missing, empty, or not a string",
        }

    cleaned = clean_text(text)

    if not is_text_usable(cleaned, MIN_DESCRIPTION_LENGTH):
        logger.info("Rejected feedback %s: text too short after cleaning", feedback_id)
        return {
            "feedback_id": feedback_id,
            "cleaned_text": cleaned,
            "status": "rejected",
            "error": f"text shorter than {MIN_DESCRIPTION_LENGTH} characters after cleaning",
        }

    logger.info("Processed feedback %s", feedback_id)
    return {
        "feedback_id": feedback_id,
        "cleaned_text": cleaned,
        "status": "processed",
    }
