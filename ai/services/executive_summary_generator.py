"""Milestone 4 executive-summary generation using CrewAI."""
from __future__ import annotations

import json
import logging
from typing import Any

from ai.agents.llm import LLMNotConfiguredError, get_llm
from ai.agents.schemas import ExecutiveSummaryResult

logger = logging.getLogger("ai.services.executive_summary_generator")


def _record_ids(records: list[dict[str, Any]]) -> set[str]:
    """Return identifiers belonging to records actually supplied to the AI."""
    ids: set[str] = set()

    for record in records:
        if not isinstance(record, dict):
            continue

        for key in ("feedback_id", "feature_id", "id", "_id"):
            value = record.get(key)
            if value is not None and str(value).strip():
                ids.add(str(value))
                break

    return ids


async def generate_executive_summary(
    roadmap: dict[str, Any],
    *,
    features: list[dict[str, Any]] | None = None,
    feedback: list[dict[str, Any]] | None = None,
    workspace_id: str = "default",
    roadmap_id: str | None = None,
    summary_id: str = "executive-summary-draft",
) -> dict[str, Any]:
    """Generate a validated summary grounded in available workspace evidence."""
    if not isinstance(roadmap, dict) or not roadmap:
        return {
            "status": "failed",
            "summary": None,
            "error": "roadmap is required and cannot be empty.",
        }

    features = features or []
    feedback = feedback or []

    # Only allow IDs from records actually retrieved for this workspace.
    valid_feedback_ids = _record_ids(feedback)
    valid_feature_ids = _record_ids(features)

    context = {
        "roadmap": roadmap,
        "features": features,
        "feedback": feedback,
        "allowed_feedback_ids": sorted(valid_feedback_ids),
        "allowed_feature_ids": sorted(valid_feature_ids),
    }

    try:
        from crewai import Agent, Crew, Process, Task

        agent = Agent(
            role="Product Roadmap Executive Analyst",
            goal=(
                "Summarize roadmap decisions, risks, dependencies, "
                "and expected outcomes for leadership."
            ),
            backstory=(
                "You are a careful product strategy analyst. "
                "Never invent customer evidence or metrics. "
                "Cite only identifiers from the supplied evidence."
            ),
            llm=get_llm(),
            verbose=False,
            allow_delegation=False,
        )

        task = Task(
            description=(
                "Create a concise executive summary from the supplied JSON. "
                "Use only facts in the context. Do not invent metrics, "
                "feedback, feature IDs, or promises. Mention uncertainty "
                "as a risk or assumption. source_feedback_ids must be a "
                "subset of allowed_feedback_ids, and source_feature_ids "
                "must be a subset of allowed_feature_ids. Keep recommendations "
                "actionable.\n\nCONTEXT JSON:\n"
                + json.dumps(context, default=str, ensure_ascii=False)
            ),
            expected_output="A validated structured executive summary.",
            agent=agent,
            output_pydantic=ExecutiveSummaryResult,
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
        )

        result = await crew.kickoff_async()
        parsed = getattr(result, "pydantic", None)

        if parsed is None:
            raise ValueError(
                "The summary agent did not return validated structured output."
            )

        summary = parsed.model_dump()

        summary_feedback_ids = [
            str(value)
            for value in summary.get("source_feedback_ids", [])
            if str(value) in valid_feedback_ids
        ]
        summary_feature_ids = [
            str(value)
            for value in summary.get("source_feature_ids", [])
            if str(value) in valid_feature_ids
        ]

        content_keys = (
            "overview",
            "customer_pain_points",
            "priority_features",
            "product_opportunities",
            "roadmap_highlights",
            "risks",
            "dependencies",
            "recommendations",
            "expected_outcomes",
        )

        return {
            "status": "completed",
            "summary": {
                "summary_id": summary_id,
                "workspace_id": workspace_id,
                "roadmap_id": (
                    roadmap_id
                    or roadmap.get("roadmap_id", "roadmap-draft")
                ),
                "roadmap_version": int(roadmap.get("version", 1)),
                "title": (
                    f"Executive Summary — "
                    f"{roadmap.get('title', 'Product Roadmap')}"
                ),
                "content": {
                    key: summary[key]
                    for key in content_keys
                },
                "source_feedback_ids": summary_feedback_ids,
                "source_feature_ids": summary_feature_ids,
                "generated_by_ai": True,
                "quality_metrics": {
                    "validation_status": "passed",
                    "evidence_coverage": (
                        len(summary_feedback_ids) / len(valid_feedback_ids)
                        if valid_feedback_ids
                        else 1.0
                    ),
                    "missing_information": [],
                    "warnings": (
                        ["No workspace feedback records were available."]
                        if not valid_feedback_ids
                        else []
                    ),
                    "model_name": "configured-crewai-llm",
                },
            },
        }

    except LLMNotConfiguredError as exc:
        return {
            "status": "not_configured",
            "summary": None,
            "error": str(exc),
        }
    except Exception as exc:
        logger.exception("Executive summary generation failed")
        return {
            "status": "failed",
            "summary": None,
            "error": f"{type(exc).__name__}: {exc}",
        }
