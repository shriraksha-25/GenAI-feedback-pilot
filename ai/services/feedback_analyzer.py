"""
ai/services/feedback_analyzer.py
===================================
THE PUBLIC INTERFACE OF THE AI MODULE.

This is the ONLY file the backend teammate should ever need to import
from. Everything else in `ai/` (pandas, cleaning internals, file
paths, dataset loading, CrewAI agents) is an implementation detail the
backend does not need to know about.

    from ai.services.feedback_analyzer import analyze_feedback

    result = analyze_feedback(
        text="Payment failed during checkout",
        feedback_id="123",
        metadata={"source": "support_ticket", "product": "Mobile App"},
    )

See docs/AI_INTEGRATION.md for the full contract, and the docstring
below for the exact output shape.

MILESTONE 2 CHANGE
---------------------
Milestone 1 only cleaned and validated text. Milestone 2 adds one more
step after validation: run the three-agent CrewAI crew
(ai/agents/crew.py) on the cleaned text and fold its structured result
into the response. The `status` field's meaning is UNCHANGED — it
still only describes whether the input text itself was usable
("processed"/"rejected"), exactly as Milestone 1 tests already expect.
Whether the *AI analysis* succeeded is a separate concern, reported in
the new `ai_status` field, so nothing about the Milestone 1 contract
changes for callers who only cared about text cleaning.
"""

from __future__ import annotations

import logging
from typing import Optional

from ai.preprocessing.cleaning import clean_text, is_text_usable
from ai.config.config import MIN_DESCRIPTION_LENGTH
from ai.agents.crew import run_feedback_crew
from ai.agents.llm import LLMNotConfiguredError

logger = logging.getLogger("ai.services.feedback_analyzer")


def analyze_feedback(
    text: str,
    feedback_id: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Process one piece of feedback text and return a structured,
    JSON-compatible result: clean/validate the text (Milestone 1),
    then run it through the theme / pain-point / feature-request
    agents (Milestone 2).

    Parameters
    ----------
    text:
        The raw feedback/ticket description text. Required.
    feedback_id:
        Optional caller-supplied ID (e.g. a MongoDB _id or a ticket
        number), echoed back unchanged so the backend can match the
        result to its own record. If omitted, the output's
        `feedback_id` will be None.
    metadata:
        Optional dict of extra context (e.g. {"product": "...",
        "source": "support_ticket"}). Still not used by any AI logic
        as of Milestone 2 — accepted so the signature doesn't need to
        change again if a later milestone uses it (e.g. to bias theme
        extraction by product line).

    Returns
    -------
    dict, always with these keys:
        {
            "feedback_id": <str or None>,
            "cleaned_text": <str>,
            "status": "processed" | "rejected",      # was the TEXT usable?
            "error": <str>,                            # only if status == "rejected"

            # --- Milestone 2: present only when status == "processed" ---
            "ai_status": "completed" | "failed" | "not_configured",
            "theme": <str or None>,
            "pain_point": <str or None>,
            "feature_opportunity": <str or None>,       # None if no feature request found
            "feature_category": <str or None>,
            "confidence": {                              # None entries if ai_status != "completed"
                "theme": <float or None>,
                "pain_point": <float or None>,
                "feature_opportunity": <float or None>,
            },
            "sentiment": None,   # NOT part of this Milestone 2 scope — always None, never fabricated
            "category": None,    # NOT part of this Milestone 2 scope — always None, never fabricated
            "ai_error": <str>,   # only present if ai_status in ("failed", "not_configured")
        }

    Error handling
    --------------
    This function never raises for bad INPUT (None, empty string,
    wrong type, whitespace-only text, or an LLM/agent failure) — it
    always returns a dict. Text-validity problems produce
    `status: "rejected"`. AI-analysis problems (no provider configured,
    or the LLM/crew call itself failing) produce `status: "processed"`
    (the text itself was fine) with `ai_status: "not_configured"` or
    `"failed"` and an `ai_error` message — the caller decides what to
    do with unanalyzed feedback (e.g. store it and retry analysis
    later), rather than this function silently inventing placeholder
    AI results.
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
    result = {
        "feedback_id": feedback_id,
        "cleaned_text": cleaned,
        "status": "processed",
    }
    result.update(_run_ai_analysis(cleaned, feedback_id))
    return result


def _run_ai_analysis(cleaned_text: str, feedback_id: Optional[str]) -> dict:
    """
    Run the CrewAI agents on already-cleaned text and shape the result
    for merging into analyze_feedback()'s return dict. Isolated into
    its own function so analyze_feedback() stays readable, and so
    ai_status handling has one single place to change.
    """
    base = {
        "sentiment": None,  # not part of this Milestone 2 scope
        "category": None,  # not part of this Milestone 2 scope
        "theme": None,
        "pain_point": None,
        "feature_opportunity": None,
        "feature_category": None,
        "confidence": {"theme": None, "pain_point": None, "feature_opportunity": None},
    }

    try:
        analysis = run_feedback_crew(cleaned_text)
    except LLMNotConfiguredError as exc:
        logger.info("AI analysis skipped for feedback %s: %s", feedback_id, exc)
        base["ai_status"] = "not_configured"
        base["ai_error"] = str(exc)
        return base
    except Exception as exc:  # noqa: BLE001 - any agent/LLM failure must not crash the caller
        logger.error("AI analysis failed for feedback %s: %s", feedback_id, exc, exc_info=True)
        base["ai_status"] = "failed"
        base["ai_error"] = f"{type(exc).__name__}: {exc}"
        return base

    base.update(
        {
            "ai_status": "completed",
            "theme": analysis.theme,
            "pain_point": analysis.pain_point,
            "feature_opportunity": analysis.feature_request,
            "feature_category": analysis.feature_category,
            "confidence": {
                "theme": analysis.theme_confidence,
                "pain_point": analysis.pain_point_confidence,
                "feature_opportunity": analysis.feature_request_confidence,
            },
        }
    )
    return base
