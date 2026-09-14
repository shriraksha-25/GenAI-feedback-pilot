"""
ai/agents/schemas.py
======================
Structured output models for the three Milestone 2 agents.

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
