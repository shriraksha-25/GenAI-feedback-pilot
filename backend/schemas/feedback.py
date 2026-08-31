from pydantic import BaseModel, Field
from typing import Optional


class CustomerFeedback(BaseModel):
    feedback_text: str = Field(
        ...,
        min_length=5,
        description="Original feedback submitted by the customer"
    )

    source: str = Field(
        default="manual",
        description="Origin of the feedback"
    )

    customer_segment: Optional[str] = Field(
        default=None,
        description="Customer group associated with the feedback"
    )

    product_area: Optional[str] = Field(
        default=None,
        description="Product area related to the feedback"
    )

    language: str = Field(
        default="en",
        description="Language of the submitted feedback"
    )


class FeedbackResponse(BaseModel):
    message: str
    feedback_text: str
    status: str