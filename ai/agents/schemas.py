"""
ai/agents/schemas.py
======================
Structured output models for all AI/GenAI agents in this project:
the three Milestone 2 feedback-analysis agents, and the Milestone 3
PRD / User Story / Acceptance Criteria / Priority Explanation /
Product Intelligence Assistant agents. Kept in one file (matching
Milestone 2's own convention) because every one of these models
exists for the same reason: forcing an LLM call into validated,
predictable structured data via CrewAI's `Task(output_pydantic=...)`.

WHY PYDANTIC HERE SPECIFICALLY
---------------------------------
ai/schemas/feedback.py (Milestone 1) deliberately uses plain
dataclasses so the AI module has no hard Pydantic dependency. That
reasoning no longer holds for this file: CrewAI itself is built on
Pydantic and its `Task(output_pydantic=...)` feature *requires* a
Pydantic `BaseModel` to get reliable, validated structured output
straight from the LLM instead of hand-parsing free-form text. Since
`crewai` (a new Milestone 2 dependency) already pulls in Pydantic
transitively, using it here adds no new dependency in practice.

These models describe what EACH INDIVIDUAL AGENT returns. They are an
internal implementation detail of the crew — the public function
`ai.services.feedback_analyzer.analyze_feedback()` flattens them into
the project's existing normalized field names
(`theme`, `pain_point`, `feature_opportunity`, ...) before returning
anything to the backend. The backend never needs to import this file.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# =======================================================================
# MILESTONE 2 — per-feedback analysis agent outputs
# =======================================================================
class ThemeResult(BaseModel):
    """Output of the Theme Extraction Agent."""

    theme: str = Field(..., description="Short (2-5 word) label for the main topic of the feedback, e.g. 'App Stability'.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model's confidence in this theme, from 0.0 to 1.0.")


class PainPointResult(BaseModel):
    """Output of the Customer Pain Point Identification Agent."""

    pain_point: str = Field(
        ...,
        description="One sentence describing the concrete problem/friction the customer experienced, in plain language.",
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model's confidence in this pain point, from 0.0 to 1.0.")


class FeatureRequestResult(BaseModel):
    """
    Output of the Feature Request Agent.

    `has_feature_request` is explicit rather than leaving the caller to
    guess from an empty string — plenty of feedback (e.g. a pure bug
    report) contains no feature request at all, and the agent must be
    able to say so honestly instead of inventing one.
    """

    has_feature_request: bool = Field(
        ..., description="True if the feedback contains an explicit or implicit feature request, False otherwise."
    )
    feature_request: Optional[str] = Field(
        None, description="Short description of the requested feature, in the customer's intent. None if has_feature_request is False."
    )
    feature_category: Optional[str] = Field(
        None,
        description="Broad functional category the request falls under, e.g. 'Reporting', 'Payments', 'Notifications'. None if has_feature_request is False.",
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model's confidence in this extraction, from 0.0 to 1.0.")


class AgentAnalysisResult(BaseModel):
    """
    The combined result of running all three agents on one piece of
    feedback. This is what `ai.agents.crew.run_feedback_crew()`
    returns — `ai.services.feedback_analyzer` flattens this into the
    dict shape documented in docs/AI_INTEGRATION.md.
    """

    theme: Optional[str] = None
    theme_confidence: Optional[float] = None
    pain_point: Optional[str] = None
    pain_point_confidence: Optional[float] = None
    feature_request: Optional[str] = None
    feature_category: Optional[str] = None
    feature_request_confidence: Optional[float] = None

    @classmethod
    def from_agent_outputs(
        cls,
        theme: ThemeResult,
        pain_point: PainPointResult,
        feature: FeatureRequestResult,
    ) -> "AgentAnalysisResult":
        return cls(
            theme=theme.theme,
            theme_confidence=theme.confidence,
            pain_point=pain_point.pain_point,
            pain_point_confidence=pain_point.confidence,
            feature_request=feature.feature_request if feature.has_feature_request else None,
            feature_category=feature.feature_category if feature.has_feature_request else None,
            feature_request_confidence=feature.confidence,
        )


# =======================================================================
# MILESTONE 3 — PRD / User Story / Acceptance Criteria / Prioritization /
# Product Intelligence Assistant agent outputs
# =======================================================================
#
# DESIGN NOTE SHARED BY ALL M3 MODELS BELOW
# --------------------------------------------
# Every field here is Optional (or an empty-list default) on purpose.
# The M3 brief is explicit: "If something is unavailable, use
# null/empty values ... instead of hallucinating." None of these
# models have a clever way to *enforce* that an LLM didn't invent
# something — that enforcement lives in the PROMPT (see
# ai/agents/product_crew.py and ai/agents/assistant_crew.py), which
# repeatedly instructs the agent to leave a field empty rather than
# guess. These schemas just make sure whatever the agent does return
# is at least the right TYPE and SHAPE for the backend to consume
# directly as JSON.


class PRDResult(BaseModel):
    """
    Structured PRD content. `title` is the only required field — every
    other section can be empty if the supplied context didn't contain
    enough evidence to fill it honestly, which is a valid and expected
    outcome, not an error.
    """

    title: str = Field(..., description="Short, specific PRD title for this feature.")
    problem_statement: Optional[str] = Field(None, description="The problem this feature addresses, grounded in the supplied pain points/evidence.")
    feature_summary: Optional[str] = Field(None, description="One to two sentence summary of what the feature is.")
    objective: Optional[str] = Field(None, description="What this feature is meant to achieve.")
    target_users: list[str] = Field(default_factory=list, description="User segments this feature is for, only if inferable from context.")
    customer_pain_points: list[str] = Field(default_factory=list, description="Pain points from the supplied context that justify this feature (should closely reflect the actual pain_points given, not new ones).")
    feature_requirements: list[str] = Field(default_factory=list, description="Concrete functional requirements for the feature.")
    user_value: Optional[str] = Field(None, description="Value delivered to the end user.")
    business_value: Optional[str] = Field(None, description="Value delivered to the business/product, only if supportable from context (e.g. priority/business info supplied) - otherwise leave empty rather than guessing at revenue/metrics.")
    scope: list[str] = Field(default_factory=list, description="What is explicitly included in this feature.")
    out_of_scope: list[str] = Field(default_factory=list, description="What is explicitly excluded from this feature.")
    assumptions: list[str] = Field(default_factory=list, description="Anything the PRD assumes that is NOT directly backed by the supplied evidence - this is where unsupported-but-reasonable inferences belong, kept separate from the evidence-backed sections above.")
    dependencies: list[str] = Field(default_factory=list, description="Other features/systems this depends on, only if evident from context.")
    risks: list[str] = Field(default_factory=list, description="Risks to delivering this feature, only if reasonably inferable.")
    success_metrics: list[str] = Field(default_factory=list, description="How success could be measured, only if reasonably inferable from context - do not invent specific numeric targets that weren't supplied.")
    supporting_evidence: list[str] = Field(default_factory=list, description="feedback_ids (or short quoted snippets) from the supplied supporting_evidence that back this PRD's claims - this is what preserves traceability back to real customer feedback.")


class UserStoryResult(BaseModel):
    """One user story in the standard 'As a / I want / so that' shape, plus its parts broken out for the backend to render however it wants."""

    user_story: str = Field(..., description="Full sentence: 'As a <user_type>, I want <goal>, so that <benefit>.'")
    user_type: str = Field(..., description="Who this story is written for, e.g. 'mobile app user', 'support agent'.")
    goal: str = Field(..., description="What the user wants to do.")
    benefit: str = Field(..., description="Why the user wants it / what they get out of it.")


class UserStoriesResult(BaseModel):
    """Wrapper so one Task can return a LIST of user stories as one structured object (CrewAI's output_pydantic needs a single top-level model)."""

    user_stories: list[UserStoryResult] = Field(default_factory=list)


class AcceptanceCriterionResult(BaseModel):
    """
    One acceptance criterion. `id` is a LOCAL label ("AC-1", "AC-2", ...)
    scoped to one generation call only — it is NOT a database ID. If the
    backend persists these, it should assign its own real ID and may
    keep this local id as a display label if useful.
    """

    id: str = Field(..., description='Local label for this criterion within this generation call, e.g. "AC-1".')
    criterion: str = Field(..., description="A specific, testable condition - never a vague statement like 'the feature should work properly'.")
    priority: str = Field("Must", description="MoSCoW priority for this criterion: 'Must', 'Should', or 'Could'.")


class AcceptanceCriteriaResult(BaseModel):
    """Wrapper so one Task can return a LIST of acceptance criteria as one structured object."""

    acceptance_criteria: list[AcceptanceCriterionResult] = Field(default_factory=list)


class PriorityExplanationResult(BaseModel):
    """
    The LLM-generated EXPLANATION half of prioritization. Never the
    numeric score itself - that's computed deterministically in
    ai/services/prioritization.py, not by this model or any LLM call.
    See that file's docstring for why.
    """

    impact_reasoning: str = Field(..., description="Plain-language explanation of why this feature may have the impact level it does, grounded in the supplied context.")
    supporting_pain_points: list[str] = Field(default_factory=list, description="Which of the supplied pain points support this priority, if any.")
    assumptions: list[str] = Field(default_factory=list, description="Any assumptions made in this explanation that aren't directly backed by the supplied context.")
    evidence_summary: Optional[str] = Field(None, description="One or two sentences summarizing the strongest evidence for or against prioritizing this feature highly.")


class AssistantResponse(BaseModel):
    """
    Output of the Product Intelligence Assistant for one question. The
    `grounded` flag plus `referenced_feedback_ids` are what let the
    backend/frontend show "based on N pieces of feedback" style
    attribution, and let a PM tell the difference between a real
    answer and an honest "I don't have that information."
    """

    answer: str = Field(..., description="The answer to the question, written for a Product Manager.")
    grounded: bool = Field(..., description="True if the answer is based on the supplied context; False if the question could not be answered from the given context (in which case `answer` should say so plainly rather than guessing).")
    referenced_feedback_ids: list[str] = Field(default_factory=list, description="feedback_ids from the supplied context that the answer actually draws on, if any were supplied and used.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model's confidence in this answer, from 0.0 to 1.0.")
