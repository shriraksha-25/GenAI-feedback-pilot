from fastapi import APIRouter

from schemas.feedback import CustomerFeedback, FeedbackResponse
from services.feedback_service import process_feedback


feedback_router = APIRouter(
    prefix="/feedback",
    tags=["Customer Feedback"]
)


@feedback_router.post("/", response_model=FeedbackResponse)
def receive_feedback(feedback: CustomerFeedback):

    result = process_feedback(feedback.feedback_text)

    return {
        "message": "Customer feedback received successfully",
        "feedback_text": result["feedback_text"],
        "status": result["status"]
    }