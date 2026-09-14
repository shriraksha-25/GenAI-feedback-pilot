from uuid import uuid4

from ai.services.feedback_analyzer import analyze_feedback
from database.connection import get_database
from database.models import StoredFeedbackRecord


async def process_feedback(feedback_text: str):

    # Send feedback to AI module
    result = analyze_feedback(
        text=feedback_text
    )

    cleaned_text = result["cleaned_text"]
    status = result["status"]

    # Prepare feedback record for MongoDB
    feedback_record = StoredFeedbackRecord(
        feedback_id=str(uuid4()),
        source="manual",
        description=cleaned_text,
        status=status,
    )

    # Get active MongoDB connection
    database = get_database()

    # Store feedback in MongoDB
    await database["feedback"].insert_one(
        feedback_record.model_dump()
    )

    return {
        "feedback_text": cleaned_text,
        "status": status
    }