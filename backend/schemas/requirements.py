from typing import Optional
from pydantic import BaseModel, Field


# =========================================================
# PRD
# =========================================================

class GeneratePRDRequest(BaseModel):
    feature_id: str = Field(
        ...,
        min_length=1,
        description="Feature ID used to generate the PRD",
    )

    workspace_id: str = Field(
        ...,
        min_length=1,
        description="Workspace that owns the feature",
    )

    requested_by: Optional[str] = Field(
        default=None,
        description="User requesting PRD generation",
    )


class PRDReviewRequest(BaseModel):
    status: str = Field(
        ...,
        description=(
            "Review status: ai_draft, under_review, "
            "approved or rejected"
        ),
    )

    reviewed_by: str = Field(
        ...,
        min_length=1,
        description="User reviewing the PRD",
    )


# =========================================================
# USER STORIES
# =========================================================

class GenerateUserStoriesRequest(BaseModel):
    feature_id: str = Field(
        ...,
        min_length=1,
    )

    workspace_id: str = Field(
        ...,
        min_length=1,
    )

    prd_id: Optional[str] = None

    requested_by: Optional[str] = None


class UserStoryReviewRequest(BaseModel):
    status: str = Field(
        ...,
        description=(
            "Review status: ai_draft, under_review, "
            "approved or rejected"
        ),
    )

    reviewed_by: str = Field(
        ...,
        min_length=1,
    )


# =========================================================
# PRIORITIZATION / RICE
# =========================================================

class CreatePriorityConfigurationRequest(BaseModel):
    workspace_id: str = Field(
        ...,
        min_length=1,
    )

    name: str = Field(
        ...,
        min_length=1,
    )

    method: str = Field(
        default="RICE",
    )

    weights: dict[str, float] = Field(
        default_factory=lambda: {
            "reach": 1.0,
            "impact": 1.0,
            "confidence": 1.0,
            "effort": 1.0,
        }
    )

    created_by: Optional[str] = None


class CalculatePriorityRequest(BaseModel):
    workspace_id: str = Field(
        ...,
        min_length=1,
    )

    feature_id: str = Field(
        ...,
        min_length=1,
    )

    reach: float = Field(
        default=0.0,
        ge=0,
    )

    impact: float = Field(
        default=0.0,
        ge=0,
    )

    confidence: float = Field(
        default=0.0,
        ge=0,
        le=100,
    )

    effort: float = Field(
        default=1.0,
        gt=0,
    )

    calculated_by: Optional[str] = None