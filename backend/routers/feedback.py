from fastapi import APIRouter, HTTPException

from backend.schemas.feedback import CustomerFeedback, FeedbackResponse
from backend.services.feedback_service import process_feedback


feedback_router = APIRouter(
    prefix="/feedback",
    tags=["Customer Feedback"]
)


@feedback_router.post(
    "/",
    response_model=FeedbackResponse,
    responses={
        400: {
            "description": "Feedback rejected during preprocessing"
        }
    }
)
async def receive_feedback(feedback: CustomerFeedback):

    result = await process_feedback(
        feedback_text=feedback.feedback_text,
        source=feedback.source,
        customer_segment=feedback.customer_segment,
        product_area=feedback.product_area,
        language=feedback.language,
    )

    if result["status"] == "rejected":
        raise HTTPException(
            status_code=400,
            detail="Feedback was rejected during preprocessing."
        )

    return {
        "feedback_id": result["feedback_id"],
        "message": "Customer feedback received and analysed successfully",
        "feedback_text": result["feedback_text"],
        "status": result["status"],
        "ai_analysis": result["ai_analysis"],
    }