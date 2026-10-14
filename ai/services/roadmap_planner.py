"""Milestone 4 evidence-linked roadmap planning.

This module is AI-side only: it accepts normalized M2/M3 records and returns
JSON-compatible data. It does not read MongoDB or expose HTTP endpoints.
Scheduling is deterministic; the LLM is used only for optional explanations.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def generate_roadmap(
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
    """Create a dependency-aware, capacity-constrained roadmap draft.

    Feature dictionaries may include feature_id/id, title, description,
    source_feedback_ids, pain_point, estimated_effort/effort, priority_score,
    dependency_feature_ids/dependencies, and risk_level. Missing evidence is
    never invented: evidence IDs are carried through from supplied records.
    """
    if milestone_days <= 0 or capacity_per_milestone <= 0 or max_milestones <= 0:
        raise ValueError("milestone_days, capacity_per_milestone and max_milestones must be positive")
    start = horizon_start or datetime.now(timezone.utc)
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    feedback_by_id = {
        _text(item.get("feedback_id") or item.get("id")): item
        for item in (feedback or [])
        if _text(item.get("feedback_id") or item.get("id"))
    }
    scores_by_id = {}
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
        raw_score = raw.get("priority_score", score_doc.get("priority_score", score_doc.get("score", 0)))
        try:
            score = float(raw_score or 0)
        except (TypeError, ValueError):
            score = 0.0
            warnings.append(f"Feature {fid} has an invalid priority score; treated as 0.")
        raw_effort = raw.get("estimated_effort", raw.get("effort"))
        try:
            effort = float(raw_effort) if raw_effort is not None else None
        except (TypeError, ValueError):
            effort = None
        if effort is None or effort <= 0:
            warnings.append(f"Feature {fid} has no positive estimated effort and cannot be scheduled.")
        deps = raw.get("dependency_feature_ids", raw.get("dependencies", [])) or []
        if isinstance(deps, str):
            deps = [deps]
        evidence = raw.get("source_feedback_ids", raw.get("feedback_ids", [])) or []
        if isinstance(evidence, str):
            evidence = [evidence]
        for evidence_id in evidence:
            if feedback_by_id and evidence_id not in feedback_by_id:
                warnings.append(f"Feature {fid} references feedback ID {evidence_id} not included in supplied feedback.")
        normalized.append({
            "feature_id": fid,
            "title": _text(raw.get("title") or raw.get("name")) or fid,
            "description": _text(raw.get("description")),
            "effort": effort,
            "score": score,
            "dependencies": list(dict.fromkeys(_text(d) for d in deps if _text(d))),
            "evidence": list(dict.fromkeys(_text(e) for e in evidence if _text(e))),
            "pain_points": list(raw.get("pain_points") or ([raw["pain_point"]] if raw.get("pain_point") else [])),
            "impact": raw.get("estimated_impact"),
            "risk": raw.get("risk_level") or "medium",
        })

    by_id = {item["feature_id"]: item for item in normalized}
    for item in normalized:
        for dep in item["dependencies"]:
            if dep not in by_id:
                warnings.append(f"Feature {item['feature_id']} depends on unknown feature {dep}.")
    # A dependency cycle makes a safe schedule impossible, so fail explicitly.
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

    remaining = {item["feature_id"] for item in normalized if item["effort"] and item["effort"] > 0}
    scheduled_milestones: list[dict[str, Any]] = []
    scheduled_ids: set[str] = set()
    for milestone_index in range(max_milestones):
        capacity_left = float(capacity_per_milestone)
        candidates = sorted(
            (by_id[fid] for fid in remaining if all(dep in scheduled_ids for dep in by_id[fid]["dependencies"])),
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
                    if item["dependencies"] else
                    f"Ranked by supplied priority score ({item['score']}) and fits milestone capacity."
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
            "description": f"Features planned for days {milestone_index * milestone_days + 1}–{(milestone_index + 1) * milestone_days}.",
            "sequence": milestone_index + 1,
            "start_date": m_start.isoformat(),
            "end_date": m_end.isoformat(),
            "feature_items": items,
        })

    for fid in sorted(remaining):
        item = by_id[fid]
        if any(dep not in scheduled_ids and dep in by_id for dep in item["dependencies"]):
            warnings.append(f"Feature {fid} was not scheduled because a dependency could not be scheduled first.")
        else:
            warnings.append(f"Feature {fid} was not scheduled within the configured milestone capacity/horizon.")

    source_feedback_ids = sorted({e for item in normalized for e in item["evidence"]})
    dependencies = []
    for item in normalized:
        for dep in item["dependencies"]:
            if dep in by_id:
                dependencies.append({
                    "dependency_id": f"{roadmap_id}-dep-{item['feature_id']}-{dep}",
                    "feature_id": item["feature_id"],
                    "depends_on_feature_id": dep,
                    "dependency_type": "finish_to_start",
                    "description": f"{item['title']} depends on {by_id[dep]['title']}.",
                    "is_mandatory": True,
                })
    return {
        "roadmap_id": roadmap_id,
        "workspace_id": workspace_id,
        "title": title,
        "description": "Draft generated from supplied feature, priority and customer-evidence records.",
        "planning_horizon_start": start.isoformat(),
        "planning_horizon_end": (start + timedelta(days=milestone_days * max_milestones)).isoformat(),
        "development_capacity": capacity_per_milestone,
        "capacity_unit": "story_points",
        "planning_assumptions": [
            {"assumption_id": f"{roadmap_id}-capacity", "category": "team_capacity",
             "description": "Capacity per milestone was supplied by the caller.", "value": capacity_per_milestone, "source": "caller"},
            {"assumption_id": f"{roadmap_id}-duration", "category": "milestone_duration",
             "description": "Milestone duration was supplied by the caller.", "value": milestone_days, "source": "caller"},
        ],
        "milestones": scheduled_milestones,
        "dependencies": dependencies,
        "source_feedback_ids": source_feedback_ids,
        "source_feature_ids": [item["feature_id"] for item in normalized],
        "roadmap_type": "baseline",
        "review_status": "ai_draft",
        "generated_by_ai": False,
        "quality_metrics": {
            "validation_status": "warning" if warnings else "passed",
            "completeness_score": round(len(scheduled_ids) / len(normalized), 2) if normalized else 1.0,
            "evidence_coverage": round(sum(bool(i["evidence"]) for i in normalized) / len(normalized), 2) if normalized else 1.0,
            "warnings": warnings,
            "missing_information": [f"estimated_effort:{i['feature_id']}" for i in normalized if not i["effort"] or i["effort"] <= 0],
            "model_name": "deterministic-roadmap-planner",
        },
    }


def explain_priority_recommendation(feature: dict[str, Any]) -> dict[str, Any]:
    """Explain a supplied priority score without recalculating or inventing it.

    This deliberately reuses M3's score and scoring factors. It is a
    deterministic explanation scaffold, not an LLM-generated claim.
    """
    fid = _text(feature.get("feature_id") or feature.get("id")) or None
    score = feature.get("priority_score", feature.get("score"))
    factors = feature.get("priority_factors") or feature.get("scoring_factors") or {}
    missing = []
    if score is None:
        missing.append("priority_score")
    if not factors:
        missing.append("priority_factors (for example reach, impact, confidence, effort)")
    evidence_ids = feature.get("source_feedback_ids", feature.get("feedback_ids", [])) or []
    if isinstance(evidence_ids, str):
        evidence_ids = [evidence_ids]
    dependencies = feature.get("dependency_feature_ids", feature.get("dependencies", [])) or []
    if isinstance(dependencies, str):
        dependencies = [dependencies]
    reasons = []
    if score is not None:
        reasons.append(f"Existing supplied priority score: {score}; this function does not recalculate it.")
    if factors:
        reasons.append("Scoring factors supplied by the workspace: " + ", ".join(f"{k}={v}" for k, v in factors.items()) + ".")
    if evidence_ids:
        reasons.append(f"The workspace links this feature to {len(evidence_ids)} feedback record(s).")
    else:
        reasons.append("No supporting feedback IDs were supplied for this feature.")
    if dependencies:
        reasons.append("Scheduling may be constrained by dependencies: " + ", ".join(map(str, dependencies)) + ".")
    return {
        "feature_id": fid,
        "priority_score": score,
        "priority_factors": factors,
        "supporting_feedback_ids": list(dict.fromkeys(_text(x) for x in evidence_ids if _text(x))),
        "dependency_feature_ids": list(dict.fromkeys(_text(x) for x in dependencies if _text(x))),
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
    """Re-pack a roadmap's scheduled features for a what-if scenario.

    The input is not mutated. This is a deterministic comparison of the
    features already present in the supplied roadmap; it cannot restore
    features omitted from the original draft because their full input records
    are not available in the roadmap object.
    """
    import copy
    base = copy.deepcopy(roadmap)
    delayed = set(delayed_feature_ids or [])
    removed = set(removed_feature_ids or [])
    original_items = [copy.deepcopy(i) for m in base.get("milestones", []) for i in m.get("feature_items", [])]
    original_by_id = {i["feature_id"]: i for i in original_items}
    original_ids = set(original_by_id)
    if (delayed | removed) - original_ids:
        unknown = sorted((delayed | removed) - original_ids)
        raise ValueError(f"Unknown feature IDs in simulation: {', '.join(unknown)}")
    revised_capacity = modified_capacity if modified_capacity is not None else base.get("development_capacity")
    if revised_capacity is not None and revised_capacity <= 0:
        raise ValueError("modified_capacity must be greater than 0")

    remaining = {fid for fid in original_ids if fid not in removed}
    scheduled: set[str] = set()
    new_milestones: list[dict[str, Any]] = []
    warnings: list[str] = []
    original_start = base.get("planning_horizon_start")
    try:
        start = datetime.fromisoformat(original_start) if original_start else datetime.now(timezone.utc)
    except (TypeError, ValueError):
        start = datetime.now(timezone.utc)
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    milestone_days = 30
    existing_milestones = base.get("milestones", [])
    if len(existing_milestones) > 0:
        try:
            d1 = datetime.fromisoformat(existing_milestones[0]["start_date"])
            d2 = datetime.fromisoformat(existing_milestones[0]["end_date"])
            milestone_days = max(1, (d2 - d1).days)
        except (KeyError, TypeError, ValueError):
            pass
    sequence = 1
    while remaining:
        capacity_left = float(revised_capacity) if revised_capacity is not None else float("inf")
        ready = [original_by_id[fid] for fid in remaining
                 if all(dep in scheduled or dep in removed for dep in original_by_id[fid].get("dependency_feature_ids", []))]
        # Delayed features are considered only after all non-delayed ready items.
        ready.sort(key=lambda i: (i["feature_id"] in delayed, -float(i.get("priority_score") or 0), i["feature_id"]))
        items = []
        for item in ready:
            effort = item.get("estimated_effort")
            if effort is None:
                warnings.append(f"Feature {item['feature_id']} has no effort estimate and cannot be repacked.")
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
                warnings.append(f"Feature {fid} could not be scheduled under the scenario capacity/dependency constraints.")
            break
        m_start = start + timedelta(days=(sequence - 1) * milestone_days)
        m_end = m_start + timedelta(days=milestone_days)
        new_milestones.append({
            "milestone_id": f"{base.get('roadmap_id', 'roadmap')}-what-if-m{sequence}",
            "name": f"What-If Milestone {sequence}",
            "description": "Repacked under the scenario capacity and dependency constraints.",
            "sequence": sequence,
            "start_date": m_start.isoformat(),
            "end_date": m_end.isoformat(),
            "feature_items": items,
        })
        sequence += 1
    new_sequence = {i["feature_id"]: m["sequence"] for m in new_milestones for i in m["feature_items"]}
    original_sequence = {i["feature_id"]: m.get("sequence") for m in base.get("milestones", []) for i in m.get("feature_items", [])}
    moved = sorted(fid for fid in original_ids if fid not in removed and new_sequence.get(fid) != original_sequence.get(fid))
    revised = copy.deepcopy(base)
    revised["milestones"] = new_milestones
    revised["roadmap_type"] = "what_if"
    revised["base_roadmap_version"] = base.get("version", 1)
    revised["development_capacity"] = revised_capacity
    revised["change_summary"] = f"What-if scenario: capacity={revised_capacity}; delayed={sorted(delayed)}; removed={sorted(removed)}."
    revised.setdefault("quality_metrics", {})["warnings"] = list(dict.fromkeys(warnings))
    return {
        "roadmap": revised,
        "comparison": {
            "original_feature_count": len(original_ids),
            "revised_feature_count": sum(len(m.get("feature_items", [])) for m in new_milestones),
            "delayed_feature_ids": sorted(delayed),
            "removed_feature_ids": sorted(removed),
            "moved_feature_ids": moved,
            "original_capacity": roadmap.get("development_capacity"),
            "revised_capacity": revised_capacity,
            "capacity_change": (revised_capacity - roadmap["development_capacity"]) if revised_capacity is not None and roadmap.get("development_capacity") is not None else None,
            "warnings": list(dict.fromkeys(warnings)),
        },
    }
