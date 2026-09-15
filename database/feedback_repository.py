"""Store and retrieve analyzed customer feedback."""

from datetime import datetime, timezone
from typing import Any

from pymongo import DESCENDING, ReturnDocument

from database.connection import get_database
from database.models import AIAnalysis


async def save_feedback_analysis(
    feedback_id: str,
    analysis: AIAnalysis | dict[str, Any],
) -> dict[str, Any] | None:
    """Save Milestone 2 analysis results in an existing feedback record."""

    database = get_database()
    now = datetime.now(timezone.utc)

    analysis_model = (
        analysis
        if isinstance(analysis, AIAnalysis)
        else AIAnalysis.model_validate(analysis)
    )

    analysis_data = analysis_model.model_dump(mode="python")

    if analysis_data["analyzed_at"] is None:
        analysis_data["analyzed_at"] = now

    analysis_data["analysis_updated_at"] = now

    return await database.feedback.find_one_and_update(
        {"feedback_id": feedback_id},
        {
            "$set": {
                "ai_analysis": analysis_data,
                "updated_at": now,
            }
        },
        return_document=ReturnDocument.AFTER,
    )


async def get_feedback_by_id(
    feedback_id: str,
) -> dict[str, Any] | None:
    """Retrieve one feedback record using its feedback ID."""

    database = get_database()

    return await database.feedback.find_one(
        {"feedback_id": feedback_id}
    )


async def get_analyzed_feedback(
    workspace_id: str | None = None,
    limit: int = 50,
    skip: int = 0,
) -> list[dict[str, Any]]:
    """Retrieve feedback records with completed AI analysis."""

    database = get_database()

    query: dict[str, Any] = {
        "ai_analysis.ai_status": "completed"
    }

    if workspace_id is not None:
        query["workspace_id"] = workspace_id

    safe_limit = max(1, min(limit, 100))
    safe_skip = max(0, skip)

    cursor = (
        database.feedback
        .find(query)
        .sort("ai_analysis.analyzed_at", DESCENDING)
        .skip(safe_skip)
        .limit(safe_limit)
    )

    return [document async for document in cursor]