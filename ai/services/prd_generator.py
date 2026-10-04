"""
ai/services/prd_generator.py
===============================
PUBLIC INTERFACE for PRD generation - this is what the backend
imports, mirroring `ai.services.feedback_analyzer.analyze_feedback()`
exactly: one function, a plain JSON-compatible dict in, a plain
JSON-compatible dict out, no CrewAI/Pydantic/LLM details leaked to
the caller.

    from ai.services.prd_generator import generate_prd

    result = generate_prd(
        context={
            "feature_name": "Save frequently used reports",
            "themes": ["Reporting"],
            "pain_points": ["Regenerating the same report every time is tedious."],
            "feature_requests": ["Save frequently used reports"],
            "supporting_evidence": [
                {"feedback_id": "42", "text": "I wish I could save my frequently used reports."}
            ],
        },
        feature_id="feat-001",
    )

See ai/agents/context.py for the full `context` shape (every key is
optional - the backend supplies whatever Milestone 2 data it has
gathered for this feature).
"""

from __future__ import annotations

import logging
from typing import Optional

from ai.agents.product_crew import run_prd_crew
from ai.agents.llm import LLMNotConfiguredError

logger = logging.getLogger("ai.services.prd_generator")


def generate_prd(context: dict, feature_id: Optional[str] = None) -> dict:
    """
    Generate a structured PRD from Milestone 2 feedback-analysis
    context (see ai.agents.context.FeatureContext for the expected
    shape).

    Parameters
    ----------
    context:
        FeatureContext-shaped dict - themes/pain_points/feature_requests/
        supporting_evidence gathered by the backend for one feature.
        An empty or sparse dict is valid input - the PRD will simply
        have more empty sections rather than failing (see Returns).
    feature_id:
        Optional caller-supplied ID (e.g. the backend/database's own
        feature identifier), echoed back unchanged. This module never
        generates or persists this ID - see module note on versioning
        below.

    Returns
    -------
    dict, always with these keys:
        {
            "feature_id": <str or None>,
            "status": "ai_draft" | "failed" | "not_configured",
            # "ai_draft" mirrors the team's planned status vocabulary
            # (AI Draft / Under Review / Approved) - this module only
            # ever produces the first one. Review/approval status
            # transitions are the backend/database's responsibility,
            # not this module's - it does not persist anything.
            "prd": <dict or None>,   # the PRDResult fields, flattened - see PRDResult in ai/agents/schemas.py
            "error": <str>,          # only present if status != "ai_draft"
        }

    Error handling
    --------------
    Never raises. If no GenAI provider is configured or the LLM call
    fails, returns `status: "not_configured"` / `"failed"` with
    `prd: None` and an `error` message - never a fabricated/partial PRD.
    """
    try:
        prd_result = run_prd_crew(context)
    except LLMNotConfiguredError as exc:
        logger.info("PRD generation skipped for feature %s: %s", feature_id, exc)
        return {"feature_id": feature_id, "status": "not_configured", "prd": None, "error": str(exc)}
    except Exception as exc:  # noqa: BLE001 - must never crash the caller
        logger.error("PRD generation failed for feature %s: %s", feature_id, exc, exc_info=True)
        return {"feature_id": feature_id, "status": "failed", "prd": None, "error": f"{type(exc).__name__}: {exc}"}

    logger.info("Generated PRD for feature %s", feature_id)
    return {
        "feature_id": feature_id,
        "status": "ai_draft",
        "prd": prd_result.model_dump(),
    }
