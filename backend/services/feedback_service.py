import asyncio
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from ai.services.feedback_analyzer import analyze_feedback
from database.connection import get_database
from database.models import StoredFeedbackRecord, AIAnalysis


async def process_feedback(
    feedback_text: str,
    source: str = "manual",
    customer_segment: Optional[str] = None,
    product_area: Optional[str] = None,
    language: str = "en",
):
    feedback_id = str(uuid4())

    result = await asyncio.to_thread(
        analyze_feedback,
        text=feedback_text,
        feedback_id=feedback_id,
        metadata={
            "source": source,
            "customer_segment": customer_segment,
            "product_area": product_area,
            "language": language,
        },
    )

    cleaned_text = result["cleaned_text"]
    status = result["status"]

    ai_analysis = AIAnalysis(
        sentiment=result.get("sentiment"),
        category=result.get("category"),
        theme=result.get("theme"),
        pain_point=result.get("pain_point"),
        feature_opportunity=result.get("feature_opportunity"),
        feature_category=result.get("feature_category"),
        confidence=result.get("confidence"),
        ai_status=result.get("ai_status"),
        ai_error=result.get("ai_error"),
    )

    feedback_record = StoredFeedbackRecord(
        feedback_id=feedback_id,
        source=source,
        product=product_area,
        description=cleaned_text,
        status=status,
        created_at=datetime.now(timezone.utc).isoformat(),
        ai_analysis=ai_analysis,
    )

    try:
        database = get_database()
        await database["feedback"].insert_one(
            feedback_record.model_dump()
        )
    except RuntimeError:
        pass

    return {
        "feedback_id": feedback_id,
        "feedback_text": cleaned_text,
        "status": status,
        "ai_analysis": ai_analysis.model_dump(),
    }