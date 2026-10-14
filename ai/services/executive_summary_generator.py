"""Milestone 4 executive-summary generation using the configured CrewAI LLM."""
from __future__ import annotations

import json
import logging
from typing import Any

from ai.agents.llm import LLMNotConfiguredError, get_llm
from ai.agents.schemas import ExecutiveSummaryResult

logger = logging.getLogger("ai.services.executive_summary_generator")


def generate_executive_summary(
    roadmap: dict[str, Any],
    *,
    features: list[dict[str, Any]] | None = None,
    feedback: list[dict[str, Any]] | None = None,
    workspace_id: str = "default",
    roadmap_id: str | None = None,
    summary_id: str = "executive-summary-draft",
) -> dict[str, Any]:
    """Generate a validated summary grounded in provided roadmap and M2/M3 evidence.

    Returns a stable status envelope. No fabricated summary is returned when
    the LLM is not configured or fails.
    """
    if not isinstance(roadmap, dict) or not roadmap:
        return {"status": "failed", "summary": None, "error": "roadmap is required and cannot be empty."}
    features = features or []
    feedback = feedback or []
    source_feedback_ids = sorted({
        str(fid) for fid in roadmap.get("source_feedback_ids", [])
        if fid is not None
    })
    source_feature_ids = sorted({
        str(fid) for fid in roadmap.get("source_feature_ids", [])
        if fid is not None
    })
    context = {
        "roadmap": roadmap,
        "features": features,
        "feedback": feedback,
        "allowed_feedback_ids": source_feedback_ids,
        "allowed_feature_ids": source_feature_ids,
    }
    try:
        from crewai import Agent, Crew, Process, Task
        llm = get_llm()
        agent = Agent(
            role="Product Roadmap Executive Analyst",
            goal="Summarize roadmap decisions, risks, dependencies, and expected outcomes for leadership.",
            backstory=("You are a careful product strategy analyst. You distinguish facts from assumptions, "
                       "never invent customer evidence, and cite only identifiers present in the supplied context."),
            llm=llm,
            verbose=False,
            allow_delegation=False,
        )
        task = Task(
            description=(
                "Create a concise executive summary from the JSON context below. Use only facts in the context. "
                "Do not invent metrics, feedback, feature IDs, or promises. Mention uncertainty as a risk or assumption. "
                "source_feedback_ids must be a subset of allowed_feedback_ids and source_feature_ids a subset of "
                "allowed_feature_ids. Keep recommendations actionable.\n\nCONTEXT JSON:\n"
                + json.dumps(context, default=str, ensure_ascii=False)
            ),
            expected_output="A validated structured executive summary.",
            agent=agent,
            output_pydantic=ExecutiveSummaryResult,
        )
        result = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False).kickoff()
        parsed = getattr(result, "pydantic", None)
        if parsed is None:
            raise ValueError("The summary agent did not return validated structured output.")
        summary = parsed.model_dump()
        # Enforce traceability in code, not only in the prompt.
        summary["source_feedback_ids"] = [x for x in summary.get("source_feedback_ids", []) if x in source_feedback_ids]
        summary["source_feature_ids"] = [x for x in summary.get("source_feature_ids", []) if x in source_feature_ids]
        return {
            "status": "completed",
            "summary": {
                "summary_id": summary_id,
                "workspace_id": workspace_id,
                "roadmap_id": roadmap_id or roadmap.get("roadmap_id", "roadmap-draft"),
                "roadmap_version": int(roadmap.get("version", 1)),
                "title": f"Executive Summary — {roadmap.get('title', 'Product Roadmap')}",
                "content": {key: summary[key] for key in (
                    "overview", "customer_pain_points", "priority_features", "product_opportunities",
                    "roadmap_highlights", "risks", "dependencies", "recommendations", "expected_outcomes"
                )},
                "source_feedback_ids": summary["source_feedback_ids"],
                "source_feature_ids": summary["source_feature_ids"],
                "generated_by_ai": True,
                "quality_metrics": {
                    "validation_status": "passed",
                    "evidence_coverage": (
                        len(summary["source_feedback_ids"]) / len(source_feedback_ids)
                        if source_feedback_ids else 1.0
                    ),
                    "missing_information": [],
                    "warnings": [],
                    "model_name": "configured-crewai-llm",
                },
            },
        }
    except LLMNotConfiguredError as exc:
        return {"status": "not_configured", "summary": None, "error": str(exc)}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Executive summary generation failed")
        return {"status": "failed", "summary": None, "error": f"{type(exc).__name__}: {exc}"}
