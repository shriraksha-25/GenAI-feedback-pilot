"""Pydantic models for Milestone 4 roadmap planning."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


RoadmapStatus = Literal[
    "ai_draft",
    "under_review",
    "approved",
    "rejected",
    "archived",
]

MilestoneStatus = Literal[
    "planned",
    "in_progress",
    "completed",
    "blocked",
    "delayed",
]

RiskLevel = Literal[
    "low",
    "medium",
    "high",
    "critical",
]

ValidationStatus = Literal[
    "pending",
    "passed",
    "warning",
    "failed",
]

ReportStatus = Literal[
    "queued",
    "generating",
    "completed",
    "failed",
]


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""

    return datetime.now(timezone.utc)


class PlanningAssumption(BaseModel):
    """An assumption used while generating a roadmap."""

    assumption_id: str = Field(min_length=1)
    category: str = Field(min_length=1)
    description: str = Field(min_length=1)
    value: str | float | int | bool | None = None
    source: str | None = None


class RoadmapDependency(BaseModel):
    """Dependency between two roadmap features."""

    dependency_id: str = Field(min_length=1)
    feature_id: str = Field(min_length=1)
    depends_on_feature_id: str = Field(min_length=1)
    dependency_type: str = "finish_to_start"
    description: str | None = None
    is_mandatory: bool = True


class RoadmapFeatureItem(BaseModel):
    """Feature scheduled inside a roadmap milestone."""

    feature_id: str = Field(min_length=1)

    priority_score_id: str | None = None
    priority_score: float | None = None

    estimated_effort: float | None = Field(
        default=None,
        ge=0.0,
    )
    estimated_impact: float | None = Field(
        default=None,
        ge=0.0,
    )

    sequence_order: int = Field(default=1, ge=1)

    planned_start: datetime | None = None
    planned_end: datetime | None = None

    source_feedback_ids: list[str] = Field(
        default_factory=list
    )
    pain_points: list[str] = Field(default_factory=list)

    scheduling_reason: str | None = None
    dependency_feature_ids: list[str] = Field(
        default_factory=list
    )

    risk_level: RiskLevel = "medium"


class RoadmapMilestone(BaseModel):
    """A milestone containing scheduled feature items."""

    milestone_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str | None = None

    sequence: int = Field(ge=1)

    start_date: datetime | None = None
    end_date: datetime | None = None

    status: MilestoneStatus = "planned"
    progress_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
    )

    feature_items: list[RoadmapFeatureItem] = Field(
        default_factory=list
    )


class AIQualityMetrics(BaseModel):
    """Validation information for AI-generated output."""

    validation_status: ValidationStatus = "pending"

    completeness_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    relevance_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    evidence_coverage: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    missing_information: list[str] = Field(
        default_factory=list
    )
    warnings: list[str] = Field(default_factory=list)

    response_time_ms: int | None = Field(
        default=None,
        ge=0,
    )
    model_name: str | None = None
    evaluated_at: datetime | None = None


class RoadmapVersionRecord(BaseModel):
    """A versioned product roadmap snapshot."""

    roadmap_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)

    version: int = Field(default=1, ge=1)
    is_current: bool = True

    title: str = Field(min_length=1)
    description: str | None = None

    planning_horizon_start: datetime | None = None
    planning_horizon_end: datetime | None = None

    development_capacity: float | None = Field(
        default=None,
        ge=0.0,
    )
    capacity_unit: str = "story_points"

    planning_assumptions: list[PlanningAssumption] = Field(
        default_factory=list
    )
    milestones: list[RoadmapMilestone] = Field(
        default_factory=list
    )
    dependencies: list[RoadmapDependency] = Field(
        default_factory=list
    )

    source_feedback_ids: list[str] = Field(
        default_factory=list
    )
    source_feature_ids: list[str] = Field(
        default_factory=list
    )

    roadmap_type: Literal["baseline", "what_if"] = "baseline"
    base_roadmap_version: int | None = Field(
        default=None,
        ge=1,
    )

    review_status: RoadmapStatus = "ai_draft"
    change_summary: str | None = None

    quality_metrics: AIQualityMetrics = Field(
        default_factory=AIQualityMetrics
    )

    generated_by_ai: bool = True
    created_by: str | None = None
    created_at: datetime = Field(default_factory=utc_now)

    approved_by: str | None = None
    approved_at: datetime | None = None


class ExecutiveSummaryContent(BaseModel):
    """Structured content of an executive summary."""

    overview: str | None = None

    customer_pain_points: list[str] = Field(
        default_factory=list
    )
    priority_features: list[str] = Field(
        default_factory=list
    )
    product_opportunities: list[str] = Field(
        default_factory=list
    )

    roadmap_highlights: list[str] = Field(
        default_factory=list
    )
    risks: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(
        default_factory=list
    )
    expected_outcomes: list[str] = Field(
        default_factory=list
    )


class ExecutiveSummaryVersionRecord(BaseModel):
    """Versioned executive summary linked to a roadmap."""

    summary_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)

    roadmap_id: str = Field(min_length=1)
    roadmap_version: int = Field(ge=1)

    version: int = Field(default=1, ge=1)
    is_current: bool = True

    title: str = Field(min_length=1)
    content: ExecutiveSummaryContent = Field(
        default_factory=ExecutiveSummaryContent
    )

    source_feedback_ids: list[str] = Field(
        default_factory=list
    )
    source_feature_ids: list[str] = Field(
        default_factory=list
    )

    review_status: RoadmapStatus = "ai_draft"
    change_summary: str | None = None

    quality_metrics: AIQualityMetrics = Field(
        default_factory=AIQualityMetrics
    )

    generated_by_ai: bool = True
    created_by: str | None = None
    created_at: datetime = Field(default_factory=utc_now)

    approved_by: str | None = None
    approved_at: datetime | None = None


class ReportMetadataRecord(BaseModel):
    """Metadata for an asynchronously generated PDF report."""

    report_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)

    report_type: str = "executive_summary"

    roadmap_id: str | None = None
    roadmap_version: int | None = Field(
        default=None,
        ge=1,
    )

    summary_id: str | None = None
    summary_version: int | None = Field(
        default=None,
        ge=1,
    )

    generation_status: ReportStatus = "queued"

    file_name: str | None = None
    storage_key: str | None = None
    download_url: str | None = None
    mime_type: str = "application/pdf"
    file_size_bytes: int | None = Field(
        default=None,
        ge=0,
    )
    content_hash: str | None = None

    generated_by: str | None = None
    requested_at: datetime = Field(default_factory=utc_now)
    generated_at: datetime | None = None

    error_message: str | None = None


class RoadmapComparisonMetrics(BaseModel):
    """Comparison between original and simulated roadmaps."""

    original_capacity: float | None = Field(
        default=None,
        ge=0.0,
    )
    revised_capacity: float | None = Field(
        default=None,
        ge=0.0,
    )

    original_feature_count: int | None = Field(
        default=None,
        ge=0,
    )
    revised_feature_count: int | None = Field(
        default=None,
        ge=0,
    )

    original_total_effort: float | None = Field(
        default=None,
        ge=0.0,
    )
    revised_total_effort: float | None = Field(
        default=None,
        ge=0.0,
    )

    original_expected_impact: float | None = Field(
        default=None,
        ge=0.0,
    )
    revised_expected_impact: float | None = Field(
        default=None,
        ge=0.0,
    )


class RoadmapSimulationRecord(BaseModel):
    """A saved What-If Roadmap Simulator scenario."""

    simulation_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)

    roadmap_id: str = Field(min_length=1)
    base_roadmap_version: int = Field(ge=1)

    name: str = Field(min_length=1)
    description: str | None = None

    modified_capacity: float | None = Field(
        default=None,
        ge=0.0,
    )
    delayed_feature_ids: list[str] = Field(
        default_factory=list
    )
    removed_feature_ids: list[str] = Field(
        default_factory=list
    )
    changed_assumptions: list[PlanningAssumption] = Field(
        default_factory=list
    )

    result_roadmap_version: int | None = Field(
        default=None,
        ge=1,
    )

    comparison: RoadmapComparisonMetrics = Field(
        default_factory=RoadmapComparisonMetrics
    )

    created_by: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class AIQualityEvaluationRecord(BaseModel):
    """Queryable quality evaluation for the trust dashboard."""

    evaluation_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)

    entity_type: Literal[
        "roadmap",
        "executive_summary",
        "recommendation",
    ]
    entity_id: str = Field(min_length=1)
    entity_version: int | None = Field(default=None, ge=1)

    metrics: AIQualityMetrics = Field(
        default_factory=AIQualityMetrics
    )

    created_at: datetime = Field(default_factory=utc_now)