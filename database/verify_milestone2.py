"""Verify Milestone 2 database operations using temporary test data."""

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from database.connection import (
    close_mongodb_connection,
    connect_to_mongodb,
)
from database.dashboard_queries import (
    get_dashboard_insights,
    get_feedback_trends,
)
from database.feedback_repository import (
    get_feedback_by_id,
    save_feedback_analysis,
)


async def verify_milestone2() -> None:
    """Run Milestone 2 database verification."""

    database = await connect_to_mongodb()
    feedback_id = f"M2-TEST-{uuid4()}"

    try:
        await database.feedback.insert_one(
            {
                "feedback_id": feedback_id,
                "workspace_id": "milestone-2-test",
                "source": "verification",
                "description": (
                    "The mobile application crashes during payment."
                ),
                "status": "processed",
                "created_at": datetime.now(timezone.utc),
                "ai_analysis": {
                    "ai_status": "pending",
                },
            }
        )

        updated = await save_feedback_analysis(
            feedback_id,
            {
                "ai_status": "completed",
                "theme": "App Stability",
                "sentiment": "negative",
                "pain_point": (
                    "Customers cannot complete mobile payments."
                ),
                "feature_opportunity": (
                    "Improve mobile payment stability."
                ),
                "feature_category": "Payments",
                "feature_opportunity_group": (
                    "Payment Reliability"
                ),
                "cluster_id": 0,
                "confidence": {
                    "theme": 0.95,
                    "pain_point": 0.91,
                    "feature_opportunity": 0.88,
                },
            },
        )

        assert updated is not None
        assert updated["ai_analysis"]["ai_status"] == "completed"

        retrieved = await get_feedback_by_id(feedback_id)

        assert retrieved is not None
        assert retrieved["ai_analysis"]["theme"] == "App Stability"

        insights = await get_dashboard_insights(
            workspace_id="milestone-2-test"
        )
        trends = await get_feedback_trends(
            workspace_id="milestone-2-test"
        )

        assert insights["total_analyzed"] == 1
        assert len(trends) == 1

        print("Milestone 2 database verification successful")
        print("Analysis storage: successful")
        print("Feedback retrieval: successful")
        print("Dashboard insights: successful")
        print("Trend analysis: successful")

    finally:
        await database.feedback.delete_one(
            {"feedback_id": feedback_id}
        )
        await close_mongodb_connection()
        print("Temporary test record removed")


if __name__ == "__main__":
    asyncio.run(verify_milestone2())