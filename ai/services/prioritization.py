"""
ai/services/prioritization.py
================================
Feature prioritization: a deterministic RICE score, plus an optional
LLM-generated plain-language explanation of that score.

WHY THE SCORE ITSELF HAS NOTHING TO DO WITH THE LLM
---------------------------------------------------------
This was an explicit project requirement: "the scoring itself should
be deterministic and explainable rather than asking the LLM to
randomly assign a score." `calculate_rice_score()` below is pure
arithmetic - no LLM call, no network, no API key, nothing
non-deterministic about it. Given the same four numbers, it always
returns the same score. It doesn't even import anything from `ai.agents`.

RICE = (Reach x Impact x Confidence) / Effort

- Reach: how many users/customers this affects in a given time period
  (e.g. "estimated users per quarter").
- Impact: how much it affects each of them, typically scored on a
  simple scale (e.g. 0.25=minimal, 0.5=low, 1=medium, 2=high, 3=massive -
  the standard RICE impact scale, but you can score however the team
  agrees to).
- Confidence: how confident the team is in the Reach/Impact estimates,
  as a fraction (e.g. 1.0 = 100% confident, 0.8 = 80%, 0.5 = 50%).
- Effort: estimated person-time to build it (e.g. in person-months) -
  larger effort divides the score down.

WHO SUPPLIES REACH/IMPACT/CONFIDENCE/EFFORT?
-------------------------------------------------
Not this module, and not the LLM. These four numbers are business/PM
judgment calls - typically entered by a PM in the frontend (e.g. via
sliders or a form), possibly informed by analytics the backend/database
team owns. This module only computes the score FROM those numbers and
optionally explains it - it does not estimate, guess, or validate
Reach/Impact/Confidence/Effort beyond basic sanity checks (positive
numbers, Effort > 0).

WHY THIS LIVES IN THE AI MODULE AT ALL
-------------------------------------------
`calculate_rice_score()` is plain Python with zero AI dependency - it
could just as easily live in the backend. It's included here for
convenience (so `explain_priority()` can compute-then-explain in one
call) and because the project brief asked for "AI-side support for
prioritization." If the backend team would rather own the deterministic
calculation themselves (e.g. to avoid a round-trip to the AI module for
pure arithmetic), moving `calculate_rice_score()` is a trivial copy -
it has no dependencies on the rest of this module.
"""

from __future__ import annotations

import logging
from typing import Optional

from ai.agents.product_crew import run_priority_explanation_crew
from ai.agents.llm import LLMNotConfiguredError

logger = logging.getLogger("ai.services.prioritization")


def calculate_rice_score(reach: float, impact: float, confidence: float, effort: float) -> float:
    """
    Compute the RICE score deterministically. Raises ValueError for
    nonsensical inputs rather than silently producing a misleading
    number (e.g. a negative or infinite score).

    Parameters are plain RICE inputs (see module docstring) - this
    function does not interpret or validate their business meaning
    beyond basic sanity checks.
    """
    if effort <= 0:
        raise ValueError("effort must be greater than 0 (division by zero / undefined score otherwise).")
    if reach < 0 or impact < 0 or confidence < 0:
        raise ValueError("reach, impact, and confidence must be non-negative.")

    score = (reach * impact * confidence) / effort
    return round(score, 2)


def explain_priority(
    context: dict,
    reach: float,
    impact: float,
    confidence: float,
    effort: float,
    feature_id: Optional[str] = None,
) -> dict:
    """
    Compute the RICE score (deterministic) and, if a GenAI provider is
    configured, generate a plain-language explanation grounded in the
    supplied context (same ai_status pattern as every other M3/M2
    service function - never raises, never fabricates on failure).

    Parameters
    ----------
    context:
        A FeatureContext-shaped dict (see ai.agents.context) - themes,
        pain_points, feature_requests, supporting_evidence for this
        feature. Used only for the LLM explanation, never for the
        score itself.
    reach, impact, confidence, effort:
        The RICE inputs - see module docstring. Supplied by the caller
        (ultimately a PM via the backend), never estimated here.
    feature_id:
        Optional caller-supplied ID, echoed back unchanged.

    Returns
    -------
    dict, always containing:
        {
            "feature_id": <str or None>,
            "priority_score": <float>,       # ALWAYS present - pure arithmetic, cannot fail
            "reach": <float>, "impact": <float>, "confidence": <float>, "effort": <float>,
            "ai_status": "completed" | "failed" | "not_configured",
            "impact_reasoning": <str or None>,
            "supporting_pain_points": <list[str]>,
            "assumptions": <list[str]>,
            "evidence_summary": <str or None>,
            "ai_error": <str>,   # only if ai_status != "completed"
        }

    The score is computed and returned EVEN IF the LLM explanation
    fails or no provider is configured - prioritization numbers should
    never be blocked on GenAI availability.
    """
    score = calculate_rice_score(reach, impact, confidence, effort)

    result = {
        "feature_id": feature_id,
        "priority_score": score,
        "reach": reach,
        "impact": impact,
        "confidence": confidence,
        "effort": effort,
        "impact_reasoning": None,
        "supporting_pain_points": [],
        "assumptions": [],
        "evidence_summary": None,
    }

    # Give the explanation agent the already-computed score as part of
    # its context (see ai.agents.context.PriorityInfo) so it explains
    # THIS number, never a different one it might otherwise invent.
    explanation_context = dict(context or {})
    explanation_context["priority"] = {
        "score": score,
        "reach": reach,
        "impact": impact,
        "confidence": confidence,
        "effort": effort,
        "reasoning": "(to be generated)",
    }

    try:
        explanation = run_priority_explanation_crew(explanation_context)
    except LLMNotConfiguredError as exc:
        logger.info("Priority explanation skipped for feature %s: %s", feature_id, exc)
        result["ai_status"] = "not_configured"
        result["ai_error"] = str(exc)
        return result
    except Exception as exc:  # noqa: BLE001 - explanation failure must never block the (already-computed) score
        logger.error("Priority explanation failed for feature %s: %s", feature_id, exc, exc_info=True)
        result["ai_status"] = "failed"
        result["ai_error"] = f"{type(exc).__name__}: {exc}"
        return result

    result.update(
        {
            "ai_status": "completed",
            "impact_reasoning": explanation.impact_reasoning,
            "supporting_pain_points": explanation.supporting_pain_points,
            "assumptions": explanation.assumptions,
            "evidence_summary": explanation.evidence_summary,
        }
    )
    return result
