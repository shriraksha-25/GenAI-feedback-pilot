from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


ReviewStatus = Literal[
    "ai_draft",
    "under_review",
    "approved",
    "rejected",
]

FeatureStatus = Literal[
    "identified",
    "prioritized",
    "prd_generated",
    "stories_generated",
    "approved",
    "archived",
]


def utc_now() -> datetime:
    """Return the current UTC date and time."""

    return datetime.now(timezone.utc)


class FeatureRecord(BaseModel):
    """Feature opportunity created from Milestone 2 AI insights."""

    feature_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)

    title: str = Field(min_length=1)
    description: str | None = None

    theme: str | None = None
    pain_point: str | None = None
    feature_category: str | None = None

    source_feedback_ids: list[str] = Field(default_factory=list)

    status: FeatureStatus = "identified"

    created_by: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class FeatureEvidenceRecord(BaseModel):
    """Feedback evidence supporting a feature opportunity."""

    evidence_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    feature_id: str = Field(min_length=1)
    feedback_id: str = Field(min_length=1)

    theme: str | None = None
    pain_point: str | None = None
    excerpt: str | None = None

    relevance_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    created_at: datetime = Field(default_factory=utc_now)


class PriorityConfigurationRecord(BaseModel):
    """Configurable prioritization rules for a workspace."""

    configuration_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)

    name: str = Field(min_length=1)
    method: str = "RICE"

    weights: dict[str, float] = Field(
        default_factory=lambda: {
            "reach": 1.0,
            "impact": 1.0,
            "confidence": 1.0,
            "effort": 1.0,
        }
    )

    is_active: bool = True

    created_by: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class PriorityInputs(BaseModel):
    """Inputs used for RICE or configurable feature scoring."""

    reach: float = Field(default=0.0, ge=0.0)
    impact: float = Field(default=0.0, ge=0.0)
    confidence: float = Field(default=0.0, ge=0.0, le=100.0)
    effort: float = Field(default=1.0, gt=0.0)

    custom_values: dict[str, float] = Field(default_factory=dict)


class PriorityScoreRecord(BaseModel):
    """Calculated priority score and its explanation."""

    priority_score_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    feature_id: str = Field(min_length=1)
    configuration_id: str | None = None

    method: str = "RICE"
    inputs: PriorityInputs = Field(default_factory=PriorityInputs)

    calculated_score: float = 0.0
    rank: int | None = Field(default=None, ge=1)

    explanation: str | None = None
    recommendation: str | None = None

    calculated_by: str | None = None
    calculated_at: datetime = Field(default_factory=utc_now)


class PRDContent(BaseModel):
    """Structured content contained in a PRD version."""

    overview: str | None = None
    problem_statement: str | None = None

    target_users: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    non_goals: list[str] = Field(default_factory=list)

    functional_requirements: list[str] = Field(default_factory=list)
    non_functional_requirements: list[str] = Field(
        default_factory=list
    )

    success_metrics: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class PRDVersionRecord(BaseModel):
    """A versioned Product Requirements Document."""

    prd_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    feature_id: str = Field(min_length=1)

    version: int = Field(default=1, ge=1)
    is_current: bool = True

    title: str = Field(min_length=1)
    content: PRDContent = Field(default_factory=PRDContent)

    evidence_feedback_ids: list[str] = Field(default_factory=list)

    review_status: ReviewStatus = "ai_draft"
    change_summary: str | None = None

    generated_by_ai: bool = True
    created_by: str | None = None
    created_at: datetime = Field(default_factory=utc_now)

    approved_by: str | None = None
    approved_at: datetime | None = None


class AcceptanceCriterion(BaseModel):
    """Given-When-Then acceptance criterion."""

    criterion_id: str = Field(min_length=1)
    title: str | None = None

    given: str = Field(min_length=1)
    when: str = Field(min_length=1)
    then: str = Field(min_length=1)

    is_approved: bool = False


class UserStoryVersionRecord(BaseModel):
    """Versioned user story with acceptance criteria."""

    user_story_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    feature_id: str = Field(min_length=1)

    prd_id: str | None = None
    prd_version: int | None = Field(default=None, ge=1)

    version: int = Field(default=1, ge=1)
    is_current: bool = True

    title: str = Field(min_length=1)
    persona: str = Field(min_length=1)
    need: str = Field(min_length=1)
    value: str = Field(min_length=1)

    acceptance_criteria: list[AcceptanceCriterion] = Field(
        default_factory=list
    )

    evidence_feedback_ids: list[str] = Field(default_factory=list)

    priority: str | None = None
    review_status: ReviewStatus = "ai_draft"
    change_summary: str | None = None

    generated_by_ai: bool = True
    created_by: str | None = None
    created_at: datetime = Field(default_factory=utc_now)

    approved_by: str | None = None
    approved_at: datetime | None = None


class ConversationRecord(BaseModel):
    """Product Intelligence Assistant conversation."""

    conversation_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)

    feature_id: str | None = None
    title: str | None = None
    status: str = "active"

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ChatMessageRecord(BaseModel):
    """A message stored in an assistant conversation."""

    message_id: str = Field(min_length=1)
    conversation_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)

    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)

    feature_id: str | None = None
    prd_id: str | None = None
    user_story_id: str | None = None

    source_feedback_ids: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=utc_now)


class WorkflowEventRecord(BaseModel):
    """Audit history for the Milestone 3 workflow."""

    event_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    feature_id: str = Field(min_length=1)

    entity_type: str
    entity_id: str

    action: str
    previous_status: str | None = None
    new_status: str | None = None

    performed_by: str | None = None
    notes: str | None = None

    created_at: datetime = Field(default_factory=utc_now)