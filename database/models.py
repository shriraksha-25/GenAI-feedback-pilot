from datetime import datetime, timezone

from pydantic import BaseModel, Field


class AnalysisConfidence(BaseModel):
    """Confidence scores returned by the AI analysis."""

    theme: float | None = Field(default=None, ge=0.0, le=1.0)
    pain_point: float | None = Field(default=None, ge=0.0, le=1.0)
    feature_opportunity: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class AIAnalysis(BaseModel):
    """Milestone 2 AI-generated analysis stored with feedback."""

    ai_status: str = "pending"
    theme: str | None = None
    sentiment: str | None = None
    category: str | None = None
    pain_point: str | None = None
    feature_opportunity: str | None = None
    feature_category: str | None = None
    feature_opportunity_group: str | None = None
    cluster_id: int | None = None
    confidence: AnalysisConfidence = Field(
        default_factory=AnalysisConfidence
    )
    ai_error: str | None = None
    analyzed_at: datetime | None = None
    analysis_updated_at: datetime | None = None


class FeedbackRecord(BaseModel):
    """Canonical feedback structure shared with the AI module."""

    feedback_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    product: str | None = None
    ticket_type: str | None = None
    subject: str | None = None
    description: str = Field(min_length=1)
    priority: str | None = None
    status: str | None = None
    channel: str | None = None
    customer_satisfaction: float | None = None
    created_at: str | None = None
    ai_analysis: AIAnalysis = Field(default_factory=AIAnalysis)


class StoredFeedbackRecord(FeedbackRecord):
    """Feedback record with an optional workspace relationship."""

    workspace_id: str | None = None


class UserRecord(BaseModel):
    """Application user stored in MongoDB."""

    name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    role: str = "product_manager"
    is_active: bool = True


class WorkspaceMember(BaseModel):
    """A user belonging to a workspace."""

    user_id: str
    role: str = "member"


class WorkspaceRecord(BaseModel):
    """Product-management workspace."""

    name: str = Field(min_length=1)
    description: str | None = None
    owner_id: str
    members: list[WorkspaceMember] = Field(default_factory=list)
    status: str = "active"


class DataImportRecord(BaseModel):
    """Metadata for an imported feedback dataset."""

    workspace_id: str
    file_name: str = Field(min_length=1)
    source: str
    status: str = "planned"
    total_records: int = Field(default=0, ge=0)
    valid_records: int = Field(default=0, ge=0)
    duplicate_records: int = Field(default=0, ge=0)
    invalid_records: int = Field(default=0, ge=0)
    uploaded_by: str
    uploaded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )