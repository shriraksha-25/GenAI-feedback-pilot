
"""Milestone 4 evidence-linked roadmap planning.

This module is AI-side only: it accepts normalized M2/M3 records and returns
JSON-compatible data. It does not read MongoDB or expose HTTP endpoints.
Scheduling is deterministic; the LLM generates optional roadmap explanations.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger("ai.services.roadmap_planner")


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


async def generate_roadmap(
    features: list[dict[str, Any]],
    *,
    feedback: list[dict[str, Any]] | None = None,
    priority_scores: list[dict[str, Any]] | None = None,
    workspace_id: str = "default",
    roadmap_id: str = "roadmap-draft",
    title: str = "AI-Generated Product Roadmap",
    horizon_start: datetime | None = None,
    milestone_days: int = 30,
    capacity_per_milestone: float = 40,
    max_milestones: int = 4,
) -> dict[str, Any]:
    """Create a deterministic schedule with optional CrewAI analysis."""
    if milestone_days <= 0 or capacity_per_milestone <= 0 or max_milestones <= 0:
        raise ValueError(
            "milestone_days, capacity_per_milestone and max_milestones must be positive"
        )

    start = horizon_start or datetime.now(timezone.utc)
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)

    feedback_by_id = {
        _text(item.get("feedback_id") or item.get("id")): item
        for item in (feedback or [])
        if _text(item.get("feedback_id") or item.get("id"))
    }

    scores_by_id: dict[str, dict[str, Any]] = {}
    for item in priority_scores or []:
        fid = _text(item.get("feature_id"))
        if fid:
            scores_by_id[fid] = item

    normalized = []
    warnings: list[str] = []
    seen: set[str] = set()

    for raw in features:
        fid = _text(raw.get("feature_id") or raw.get("id"))

        if not fid:
            warnings.append("Skipped a feature without feature_id/id.")
            continue

        if fid in seen:
            raise ValueError(f"Duplicate feature ID: {fid}")

        seen.add(fid)
        score_doc = scores_by_id.get(fid, {})

        # Prefer a score explicitly stored on the feature. Otherwise use the
        # persisted priority ranking's calculated_score field.
        raw_score = raw.get("priority_score")
        if raw_score is None:
            raw_score = score_doc.get(
                "calculated_score",
                score_doc.get(
                    "priority_score",
                    score_doc.get("score", 0),
                ),
            )

        try:
            score = float(raw_score or 0)
        except (TypeError, ValueError):
            score = 0.0
            warnings.append(
                f"Feature {fid} has an invalid priority score; treated as 0."
            )

        raw_effort = raw.get("estimated_effort", raw.get("effort"))

        try:
            effort = float(raw_effort) if raw_effort is not None else None
        except (TypeError, ValueError):
            effort = None

        if effort is None or effort <= 0:
            warnings.append(
                f"Feature {fid} has no positive estimated effort and cannot be scheduled."
            )

        deps = raw.get(
            "dependency_feature_ids",
            raw.get("dependencies", []),
        ) or []

        if isinstance(deps, str):
            deps = [deps]

        evidence = raw.get(
            "source_feedback_ids",
            raw.get("feedback_ids", []),
        ) or []

        if isinstance(evidence, str):
            evidence = [evidence]

        for evidence_id in evidence:
            if feedback_by_id and evidence_id not in feedback_by_id:
                warnings.append(
                    f"Feature {fid} references feedback ID {evidence_id} "
                    "not included in supplied feedback."
                )

        normalized.append({
            "feature_id": fid,
            "title": _text(raw.get("title") or raw.get("name")) or fid,
            "description": _text(raw.get("description")),
            "effort": effort,
            "score": score,
            "dependencies": list(
                dict.fromkeys(_text(d) for d in deps if _text(d))
            ),
            "evidence": list(
                dict.fromkeys(_text(e) for e in evidence if _text(e))
            ),
            "pain_points": list(
                raw.get("pain_points")
                or ([raw["pain_point"]] if raw.get("pain_point") else [])
            ),
            "impact": raw.get("estimated_impact"),
            "risk": raw.get("risk_level") or "medium",
        })

    by_id = {item["feature_id"]: item for item in normalized}

    for item in normalized:
        for dep in item["dependencies"]:
            if dep not in by_id:
                warnings.append(
                    f"Feature {item['feature_id']} depends on unknown feature {dep}."
                )

    # Detect dependency cycles before scheduling.
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(fid: str) -> None:
        if fid in visiting:
            raise ValueError(f"Dependency cycle detected involving feature {fid}")

        if fid in visited or fid not in by_id:
            return

        visiting.add(fid)

        for dep in by_id[fid]["dependencies"]:
            visit(dep)

        visiting.remove(fid)
        visited.add(fid)

    for fid in by_id:
        visit(fid)

    remaining = {
        item["feature_id"]
        for item in normalized
        if item["effort"] and item["effort"] > 0
    }

    scheduled_milestones: list[dict[str, Any]] = []
    scheduled_ids: set[str] = set()

    for milestone_index in range(max_milestones):
        capacity_left = float(capacity_per_milestone)

        candidates = sorted(
            (
                by_id[fid]
                for fid in remaining
                if all(
                    dep in scheduled_ids
                    for dep in by_id[fid]["dependencies"]
                )
            ),
            key=lambda item: (-item["score"], item["feature_id"]),
        )

        items = []

        for item in candidates:
            effort = item["effort"]

            if effort is None or effort > capacity_left:
                continue

            capacity_left -= effort
            scheduled_ids.add(item["feature_id"])
            remaining.remove(item["feature_id"])

            items.append({
                "feature_id": item["feature_id"],
                "priority_score": item["score"],
                "estimated_effort": effort,
                "estimated_impact": item["impact"],
                "sequence_order": len(items) + 1,
                "source_feedback_ids": item["evidence"],
                "pain_points": item["pain_points"],
                "dependency_feature_ids": item["dependencies"],
                "scheduling_reason": (
                    f"Ranked by supplied priority score ({item['score']}); "
                    "all declared dependencies were scheduled in an earlier milestone."
                    if item["dependencies"]
                    else (
                        f"Ranked by supplied priority score ({item['score']}) "
                        "and fits milestone capacity."
                    )
                ),
                "risk_level": item["risk"],
            })

        if not items:
            break

        m_start = start + timedelta(days=milestone_index * milestone_days)
        m_end = m_start + timedelta(days=milestone_days)

        scheduled_milestones.append({
            "milestone_id": f"{roadmap_id}-m{milestone_index + 1}",
            "name": f"Milestone {milestone_index + 1}",
            "description": (
                f"Features planned for days "
                f"{milestone_index * milestone_days + 1} to "
                f"{(milestone_index + 1) * milestone_days}."
            ),
            "sequence": milestone_index + 1,
            "start_date": m_start.isoformat(),
            "end_date": m_end.isoformat(),
            "feature_items": items,
        })

    for fid in sorted(remaining):
        item = by_id[fid]

        if any(
            dep not in scheduled_ids and dep in by_id
            for dep in item["dependencies"]
        ):
            warnings.append(
                f"Feature {fid} was not scheduled because a dependency "
                "could not be scheduled first."
            )
        else:
            warnings.append(
                f"Feature {fid} was not scheduled within the configured "
                "milestone capacity/horizon."
            )

    source_feedback_ids = sorted({
        evidence_id
        for item in normalized
        for evidence_id in item["evidence"]
    })

    dependencies = []

    for item in normalized:
        for dep in item["dependencies"]:
            if dep in by_id:
                dependencies.append({
                    "dependency_id": (
                        f"{roadmap_id}-dep-{item['feature_id']}-{dep}"
                    ),
                    "feature_id": item["feature_id"],
                    "depends_on_feature_id": dep,
                    "dependency_type": "finish_to_start",
                    "description": (
                        f"{item['title']} depends on {by_id[dep]['title']}."
                    ),
                    "is_mandatory": True,
                })

    # Build the existing deterministic roadmap first.
    roadmap = {
        "roadmap_id": roadmap_id,
        "workspace_id": workspace_id,
        "title": title,
        "description": (
            "Draft generated from supplied feature, priority "
            "and customer-evidence records."
        ),
        "planning_horizon_start": start.isoformat(),
        "planning_horizon_end": (
            start + timedelta(days=milestone_days * max_milestones)
        ).isoformat(),
        "development_capacity": capacity_per_milestone,
        "capacity_unit": "story_points",
        "planning_assumptions": [
            {
                "assumption_id": f"{roadmap_id}-capacity",
                "category": "team_capacity",
                "description": "Capacity per milestone was supplied by the caller.",
                "value": capacity_per_milestone,
                "source": "caller",
            },
            {
                "assumption_id": f"{roadmap_id}-duration",
                "category": "milestone_duration",
                "description": "Milestone duration was supplied by the caller.",
                "value": milestone_days,
                "source": "caller",
            },
        ],
        "milestones": scheduled_milestones,
        "dependencies": dependencies,
        "source_feedback_ids": source_feedback_ids,
        "source_feature_ids": [
            item["feature_id"] for item in normalized
        ],
        "roadmap_type": "baseline",
        "review_status": "ai_draft",
        "generated_by_ai": False,
        "quality_metrics": {
            "validation_status": "warning" if warnings else "passed",
            "completeness_score": (
                round(len(scheduled_ids) / len(normalized), 2)
                if normalized else 1.0
            ),
            "evidence_coverage": (
                round(
                    sum(bool(item["evidence"]) for item in normalized)
                    / len(normalized),
                    2,
                )
                if normalized else 1.0
            ),
            "warnings": warnings,
            "missing_information": [
                f"estimated_effort:{item['feature_id']}"
                for item in normalized
                if not item["effort"] or item["effort"] <= 0
            ],
            "model_name": "deterministic-roadmap-planner",
        },
    }

    # Gemini/CrewAI adds analysis only; it never controls the schedule.
    try:
        from crewai import Agent, Crew, Process, Task
        from ai.agents.llm import get_llm

        context = {
            "roadmap_title": roadmap["title"],
            "planning_horizon_start": roadmap["planning_horizon_start"],
            "planning_horizon_end": roadmap["planning_horizon_end"],
            "capacity_per_milestone": capacity_per_milestone,
            "milestones": roadmap["milestones"],
            "dependencies": roadmap["dependencies"],
            "planning_assumptions": roadmap["planning_assumptions"],
            "source_feature_ids": roadmap["source_feature_ids"],
            "source_feedback_ids": roadmap["source_feedback_ids"],
            "warnings": roadmap["quality_metrics"]["warnings"],
        }

        agent = Agent(
            role="Product Roadmap Analyst",
            goal=(
                "Explain roadmap priorities, dependencies, risks, "
                "and planning assumptions to a product team."
            ),
            backstory=(
                "You are a careful product planning analyst. "
                "Use only supplied facts. Never invent customer evidence, "
                "metrics, feature IDs, delivery promises, or dependencies. "
                "The supplied schedule is authoritative and must not be changed."
            ),
            llm=get_llm(),
            verbose=False,
            allow_delegation=False,
        )

        task = Task(
            description=(
                "Write a concise, actionable roadmap analysis with these sections: "
                "Planning Strategy, Priority Rationale, Dependencies, Risks, "
                "and Assumptions. Refer only to supplied data. Explicitly mention "
                "missing effort estimates or unscheduled features when applicable. "
                "Do not modify or replace the roadmap schedule.\n\n"
                "ROADMAP DATA:\n"
                + json.dumps(context, default=str, ensure_ascii=False)
            ),
            expected_output=(
                "A concise roadmap analysis grounded in the supplied data, "
                "with planning strategy, priorities, dependencies, risks, "
                "and assumptions."
            ),
            agent=agent,
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
        )

        result = await crew.kickoff_async()
        analysis = str(result).strip()

        if not analysis:
            raise ValueError("The roadmap analyst returned an empty response.")

        roadmap["ai_analysis"] = analysis
        roadmap["generated_by_ai"] = True
        roadmap["quality_metrics"]["model_name"] = "configured-crewai-llm"

    except Exception as exc:
        logger.warning(
            "Roadmap AI analysis unavailable; retaining deterministic roadmap: %s",
            type(exc).__name__,
        )
        roadmap["generated_by_ai"] = False
        roadmap["quality_metrics"]["model_name"] = "deterministic-roadmap-planner"
        roadmap["quality_metrics"]["warnings"].append(
            f"AI analysis unavailable: {type(exc).__name__}"
        )
        roadmap["quality_metrics"]["validation_status"] = "warning"

    return roadmap


def explain_priority_recommendation(feature: dict[str, Any]) -> dict[str, Any]:
    """Explain a supplied priority score without recalculating or inventing it."""
    fid = _text(feature.get("feature_id") or feature.get("id")) or None
    score = feature.get("priority_score", feature.get("score"))
    factors = feature.get("priority_factors") or feature.get("scoring_factors") or {}

    missing = []

    if score is None:
        missing.append("priority_score")

    if not factors:
        missing.append(
            "priority_factors (for example reach, impact, confidence, effort)"
        )

    evidence_ids = feature.get(
        "source_feedback_ids",
        feature.get("feedback_ids", []),
    ) or []

    if isinstance(evidence_ids, str):
        evidence_ids = [evidence_ids]

    dependencies = feature.get(
        "dependency_feature_ids",
        feature.get("dependencies", []),
    ) or []

    if isinstance(dependencies, str):
        dependencies = [dependencies]

    reasons = []

    if score is not None:
        reasons.append(
            f"Existing supplied priority score: {score}; "
            "this function does not recalculate it."
        )

    if factors:
        reasons.append(
            "Scoring factors supplied by the workspace: "
            + ", ".join(f"{key}={value}" for key, value in factors.items())
            + "."
        )

    if evidence_ids:
        reasons.append(
            f"The workspace links this feature to {len(evidence_ids)} feedback record(s)."
        )
    else:
        reasons.append(
            "No supporting feedback IDs were supplied for this feature."
        )

    if dependencies:
        reasons.append(
            "Scheduling may be constrained by dependencies: "
            + ", ".join(map(str, dependencies))
            + "."
        )

    return {
        "feature_id": fid,
        "priority_score": score,
        "priority_factors": factors,
        "supporting_feedback_ids": list(
            dict.fromkeys(_text(x) for x in evidence_ids if _text(x))
        ),
        "dependency_feature_ids": list(
            dict.fromkeys(_text(x) for x in dependencies if _text(x))
        ),
        "explanation": " ".join(reasons),
        "explanation_complete": not missing,
        "missing_information": missing,
        "interpretation_type": "deterministic_from_supplied_fields",
    }


def simulate_roadmap(
    roadmap: dict[str, Any],
    *,
    modified_capacity: float | None = None,
    delayed_feature_ids: list[str] | None = None,
    removed_feature_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Re-pack scheduled features for a what-if scenario without mutating input."""
    import copy

    base = copy.deepcopy(roadmap)
    delayed = set(delayed_feature_ids or [])
    removed = set(removed_feature_ids or [])

    original_items = [
        copy.deepcopy(item)
        for milestone in base.get("milestones", [])
        for item in milestone.get("feature_items", [])
    ]

    original_by_id = {
        item["feature_id"]: item for item in original_items
    }
    original_ids = set(original_by_id)

    if (delayed | removed) - original_ids:
        unknown = sorted((delayed | removed) - original_ids)
        raise ValueError(
            f"Unknown feature IDs in simulation: {', '.join(unknown)}"
        )

    revised_capacity = (
        modified_capacity
        if modified_capacity is not None
        else base.get("development_capacity")
    )

    if revised_capacity is not None and revised_capacity <= 0:
        raise ValueError("modified_capacity must be greater than 0")

    remaining = {fid for fid in original_ids if fid not in removed}
    scheduled: set[str] = set()
    new_milestones: list[dict[str, Any]] = []
    warnings: list[str] = []

    original_start = base.get("planning_horizon_start")

    try:
        start = (
            datetime.fromisoformat(original_start)
            if original_start else datetime.now(timezone.utc)
        )
    except (TypeError, ValueError):
        start = datetime.now(timezone.utc)

    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)

    milestone_days = 30
    existing_milestones = base.get("milestones", [])

    if existing_milestones:
        try:
            d1 = datetime.fromisoformat(existing_milestones[0]["start_date"])
            d2 = datetime.fromisoformat(existing_milestones[0]["end_date"])
            milestone_days = max(1, (d2 - d1).days)
        except (KeyError, TypeError, ValueError):
            pass

    sequence = 1

    while remaining:
        capacity_left = (
            float(revised_capacity)
            if revised_capacity is not None
            else float("inf")
        )

        ready = [
            original_by_id[fid]
            for fid in remaining
            if all(
                dep in scheduled or dep in removed
                for dep in original_by_id[fid].get(
                    "dependency_feature_ids", []
                )
            )
        ]

        ready.sort(
            key=lambda item: (
                item["feature_id"] in delayed,
                -float(item.get("priority_score") or 0),
                item["feature_id"],
            )
        )

        items = []

        for item in ready:
            effort = item.get("estimated_effort")

            if effort is None:
                warnings.append(
                    f"Feature {item['feature_id']} has no effort estimate "
                    "and cannot be repacked."
                )
                continue

            effort = float(effort)

            if effort > capacity_left:
                continue

            capacity_left -= effort
            scheduled.add(item["feature_id"])
            remaining.remove(item["feature_id"])
            items.append(item)

        if not items:
            for fid in sorted(remaining):
                warnings.append(
                    f"Feature {fid} could not be scheduled under the scenario "
                    "capacity/dependency constraints."
                )
            break

        m_start = start + timedelta(days=(sequence - 1) * milestone_days)
        m_end = m_start + timedelta(days=milestone_days)

        new_milestones.append({
            "milestone_id": (
                f"{base.get('roadmap_id', 'roadmap')}-what-if-m{sequence}"
            ),
            "name": f"What-If Milestone {sequence}",
            "description": (
                "Repacked under the scenario capacity and dependency constraints."
            ),
            "sequence": sequence,
            "start_date": m_start.isoformat(),
            "end_date": m_end.isoformat(),
            "feature_items": items,
        })

        sequence += 1

    new_sequence = {
        item["feature_id"]: milestone["sequence"]
        for milestone in new_milestones
        for item in milestone["feature_items"]
    }

    original_sequence = {
        item["feature_id"]: milestone.get("sequence")
        for milestone in base.get("milestones", [])
        for item in milestone.get("feature_items", [])
    }

    moved = sorted(
        fid
        for fid in original_ids
        if fid not in removed
        and new_sequence.get(fid) != original_sequence.get(fid)
    )

    revised = copy.deepcopy(base)
    revised["milestones"] = new_milestones
    revised["roadmap_type"] = "what_if"
    revised["base_roadmap_version"] = base.get("version", 1)
    revised["development_capacity"] = revised_capacity
    revised["change_summary"] = (
        f"What-if scenario: capacity={revised_capacity}; "
        f"delayed={sorted(delayed)}; removed={sorted(removed)}."
    )

    revised.setdefault("quality_metrics", {})["warnings"] = list(
        dict.fromkeys(warnings)
    )

    return {
        "roadmap": revised,
        "comparison": {
            "original_feature_count": len(original_ids),
            "revised_feature_count": sum(
                len(milestone.get("feature_items", []))
                for milestone in new_milestones
            ),
            "delayed_feature_ids": sorted(delayed),
            "removed_feature_ids": sorted(removed),
            "moved_feature_ids": moved,
            "original_capacity": roadmap.get("development_capacity"),
            "revised_capacity": revised_capacity,
            "capacity_change": (
                revised_capacity - roadmap["development_capacity"]
                if revised_capacity is not None
                and roadmap.get("development_capacity") is not None
                else None
            ),
            "warnings": list(dict.fromkeys(warnings)),
        },
    }
