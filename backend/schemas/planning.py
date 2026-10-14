from typing import Optional
from pydantic import BaseModel, Field


class CreatePlanningItemRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        description="Title of the product planning initiative",
    )

    description: Optional[str] = Field(
        default="",
        description="Problem and scope description",
    )

    priority: str = Field(
        default="Medium",
        description="Priority level: High, Medium or Low",
    )

    target_area: Optional[str] = Field(
        default="Core Product",
        description="Target functional area",
    )

    notes: Optional[str] = Field(
        default="",
        description="Implementation notes",
    )

    status: str = Field(
        default="Planned",
        description="Planning item status",
    )

    related_opportunity: Optional[str] = Field(
        default=None,
        description="Related AI-recommended opportunity",
    )


class UpdatePlanningItemRequest(BaseModel):
    status: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    target_area: Optional[str] = None
    notes: Optional[str] = None