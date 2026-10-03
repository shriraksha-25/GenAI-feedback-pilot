"""
ai/agents/context.py
======================
Shared helper used by every Milestone 3 generation task
(ai/agents/product_crew.py, ai/agents/assistant_crew.py): turns the
loosely-typed "feature context" dict the backend assembles from
Milestone 2 data into one formatted text block to embed in a prompt.

WHY A SHARED DICT SHAPE INSTEAD OF A PYDANTIC MODEL
--------------------------------------------------------
This is INPUT the backend builds by querying MongoDB for feedback
records related to one feature (grouped by `feature_opportunity` or
`feature_opportunity_group` from ai.services.feature_clustering), not
output an LLM has to be forced into a shape. A `TypedDict` (same
pattern already used for `FeatureRequestItem` in
ai/services/feature_clustering.py) documents the expected keys without
forcing the backend to construct a heavier object just to call a
function — every key below is optional, and this module is
deliberately tolerant of missing ones (see `format_context_block`).

WHERE THIS CONTEXT ACTUALLY COMES FROM
-------------------------------------------
This module does NOT fetch anything from MongoDB itself (the AI layer
stays database-free, per the project's existing boundary - see
ai/services/feedback_analyzer.py and docs/AI_INTEGRATION.md). The
backend is responsible for:
  1. Querying feedback records whose `feature_opportunity` (or
     `feature_opportunity_group`, if clustering has run) matches the
     feature being worked on.
  2. Collecting their `theme`, `pain_point`, `feature_opportunity`
     values and original `description` text + `feedback_id`.
  3. Building one `FeatureContext` dict from that and passing it to
     `generate_prd()` / `generate_user_stories()` / etc.
This is exactly what preserves traceability: every theme/pain-point/
feature-request string traces back to a real `feedback_id` because the
backend assembled it from real Milestone 2 output, not because the AI
module invented structure around a bare feature name.
"""

from __future__ import annotations

from typing import Optional, TypedDict


class EvidenceItem(TypedDict, total=False):
    feedback_id: Optional[str]
    text: str  # original (or cleaned) customer feedback text


class PriorityInfo(TypedDict, total=False):
    score: float
    reach: float
    impact: float
    confidence: float
    effort: float
    reasoning: str  # e.g. the evidence_summary from a prior explain_priority() call


class FeatureContext(TypedDict, total=False):
    """
    The context dict every Milestone 3 generation function accepts.
    All keys optional - see `format_context_block` for how missing
    keys are represented to the LLM (explicitly, never silently).

    feature_id:
        Backend-owned identifier, if one exists yet. Echoed back
        unchanged by the service functions - never generated here.
    feature_name:
        Short human name for the feature. Strongly recommended even
        when little else is known, since every M3 schema's "title" /
        "answer" needs *something* to anchor on.
    themes, pain_points, feature_requests:
        Lists of STRINGS, taken directly from Milestone 2's
        `analyze_feedback()` output across the feedback records that
        relate to this feature (i.e. the backend already filtered and
        aggregated these - this module does not do that aggregation).
    feature_opportunity_group:
        The cluster label from
        ai.services.feature_clustering.cluster_feature_requests(), if
        clustering has been run for this feature.
    supporting_evidence:
        List of {"feedback_id": ..., "text": ...} - the actual
        customer feedback text backing the above. This is what makes
        PRD/user-story/assistant output traceable back to real
        feedback rather than vague paraphrases.
    priority:
        Output of ai.services.prioritization.explain_priority(), if
        prioritization has already been run for this feature.
    prd, user_stories:
        Previously-generated PRD / user story output (plain dicts, as
        returned by generate_prd()/generate_user_stories()), if asking
        the Product Intelligence Assistant a question ABOUT an
        already-generated PRD or story set (e.g. "what risks does this
        PRD list?").
    """

    feature_id: Optional[str]
    feature_name: str
    themes: list[str]
    pain_points: list[str]
    feature_requests: list[str]
    feature_opportunity_group: Optional[str]
    supporting_evidence: list[EvidenceItem]
    priority: PriorityInfo
    prd: dict
    user_stories: list[dict]


def format_context_block(context: Optional[dict]) -> str:
    """
    Render a FeatureContext-shaped dict as a plain-text block for
    embedding in a prompt. Every section is always present in the
    output, explicitly saying "(none provided)" when a key is
    missing/empty - this matters because an LLM seeing a SECTION
    labeled "(none provided)" is far less likely to quietly invent
    content for it than an LLM that never saw the section header at
    all.
    """
    context = context or {}

    def _list_block(label: str, items) -> str:
        items = items or []
        if not items:
            return f"{label}: (none provided)"
        return f"{label}:\n" + "\n".join(f"  - {item}" for item in items)

    lines = []
    lines.append(f"Feature name: {context.get('feature_name') or '(not provided)'}")
    lines.append(_list_block("Themes (from customer feedback analysis)", context.get("themes")))
    lines.append(_list_block("Customer pain points (from customer feedback analysis)", context.get("pain_points")))
    lines.append(_list_block("Feature requests (from customer feedback analysis)", context.get("feature_requests")))

    group = context.get("feature_opportunity_group")
    lines.append(f"Feature opportunity group (clustered label): {group or '(not provided)'}")

    evidence = context.get("supporting_evidence") or []
    if not evidence:
        lines.append("Supporting evidence (original customer feedback): (none provided)")
    else:
        ev_lines = []
        for item in evidence:
            fid = item.get("feedback_id") or "unknown-id"
            text = item.get("text") or ""
            ev_lines.append(f'  - [feedback_id={fid}] "{text}"')
        lines.append("Supporting evidence (original customer feedback):\n" + "\n".join(ev_lines))

    priority = context.get("priority")
    if priority:
        lines.append(
            "Priority information: score={score}, reach={reach}, impact={impact}, "
            "confidence={confidence}, effort={effort}, reasoning={reasoning}".format(
                score=priority.get("score", "(n/a)"),
                reach=priority.get("reach", "(n/a)"),
                impact=priority.get("impact", "(n/a)"),
                confidence=priority.get("confidence", "(n/a)"),
                effort=priority.get("effort", "(n/a)"),
                reasoning=priority.get("reasoning", "(n/a)"),
            )
        )
    else:
        lines.append("Priority information: (none provided)")

    prd = context.get("prd")
    lines.append(f"Previously generated PRD available: {'yes' if prd else 'no'}")
    if prd:
        lines.append(f"  PRD title: {prd.get('title', '(n/a)')}")
        lines.append(_list_block("  PRD risks", prd.get("risks")))
        lines.append(_list_block("  PRD dependencies", prd.get("dependencies")))

    user_stories = context.get("user_stories")
    lines.append(f"Previously generated user stories available: {len(user_stories) if user_stories else 0}")

    return "\n".join(lines)
