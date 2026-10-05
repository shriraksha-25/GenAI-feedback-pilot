import asyncio

from fastapi import APIRouter, HTTPException, Query

from backend.schemas.feedback import CustomerFeedback, FeedbackResponse
from backend.services.feedback_service import process_feedback

from database.connection import get_database
from database.feedback_repository import (
    get_analyzed_feedback,
    save_feedback_analysis,
)
from database.models import AIAnalysis

from ai.services.feedback_analyzer import analyze_feedback


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
            detail="Feedback rejected during preprocessing."
        )

    return {
        "feedback_id": result["feedback_id"],
        "message": "Customer feedback received and analysed successfully",
        "feedback_text": result["feedback_text"],
        "status": result["status"],
        "ai_analysis": result["ai_analysis"],
    }


@feedback_router.get("/")
async def get_feedback(
    limit: int = Query(default=50, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
):
    feedback = await get_analyzed_feedback(
        limit=limit,
        skip=skip,
    )

    for item in feedback:
        if "_id" in item:
            item["_id"] = str(item["_id"])

    return {
        "items": feedback,
        "total": len(feedback),
    }


@feedback_router.post("/analyze")
async def analyze_all_feedback():
    """
    Re-run AI analysis only for feedback records
    that are not already successfully analyzed.
    """

    database = get_database()

    feedback_records = await database["feedback"].find({}).to_list(
        length=1000
    )

    analyzed_count = 0
    skipped_count = 0
    failed_count = 0

    for record in feedback_records:
        try:
            feedback_id = record.get("feedback_id")
            feedback_text = record.get("description", "").strip()

            if not feedback_id or not feedback_text:
                failed_count += 1
                continue

            # ---------------------------------------------------------
            # Skip records that are already successfully analyzed.
            # This prevents unnecessary Gemini API calls and
            # helps avoid free-tier rate-limit errors.
            # ---------------------------------------------------------
            existing_analysis = record.get("ai_analysis") or {}

            if existing_analysis.get("ai_status") == "completed":
                skipped_count += 1
                continue

            # Run synchronous CrewAI analysis outside
            # FastAPI's running event loop.
            result = await asyncio.to_thread(
                analyze_feedback,
                text=feedback_text,
                feedback_id=feedback_id,
                metadata={
                    "source": record.get("source", "manual"),
                    "customer_segment": record.get("customer_segment"),
                    "product_area": record.get("product"),
                    "language": "en",
                },
            )

            ai_analysis = AIAnalysis(
                sentiment=result.get("sentiment"),
                category=result.get("category"),
                theme=result.get("theme"),
                pain_point=result.get("pain_point"),
                feature_opportunity=result.get("feature_opportunity"),
                feature_category=result.get("feature_category"),
                confidence=result.get("confidence"),
                ai_status=result.get("ai_status", "pending"),
                ai_error=result.get("ai_error"),
            )

            await save_feedback_analysis(
                feedback_id,
                ai_analysis,
            )

            # Count only genuinely completed AI analysis as analyzed.
            if result.get("ai_status") == "completed":
                analyzed_count += 1
            else:
                failed_count += 1

        except Exception:
            failed_count += 1

    return {
        "message": "Batch AI analysis completed.",
        "total_feedback": len(feedback_records),
        "analyzed": analyzed_count,
        "skipped": skipped_count,
        "failed": failed_count,
    }