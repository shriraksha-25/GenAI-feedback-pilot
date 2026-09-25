"""MongoDB aggregation queries for dashboard insights and trends."""

from datetime import datetime, timedelta, timezone
from typing import Any

from database.connection import get_database


def _analysis_match(
    workspace_id: str | None = None,
) -> dict[str, Any]:
    """Build the common filter for completed analysis records."""

    match: dict[str, Any] = {
        "ai_analysis.ai_status": "completed"
    }

    if workspace_id is not None:
        match["workspace_id"] = workspace_id

    return match


async def get_dashboard_insights(
    workspace_id: str | None = None,
    item_limit: int = 10,
) -> dict[str, Any]:
    """Return summary information required by the dashboard."""

    database = get_database()
    safe_limit = max(1, min(item_limit, 50))

    pipeline = [
        {"$match": _analysis_match(workspace_id)},
        {
            "$facet": {
                "total_analyzed": [
                    {"$count": "count"}
                ],
                "themes": [
                    {
                        "$match": {
                            "ai_analysis.theme": {
                                "$nin": [None, ""]
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": "$ai_analysis.theme",
                            "count": {"$sum": 1},
                        }
                    },
                    {"$sort": {"count": -1}},
                    {"$limit": safe_limit},
                ],
                "pain_points": [
                    {
                        "$match": {
                            "ai_analysis.pain_point": {
                                "$nin": [None, ""]
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": "$ai_analysis.pain_point",
                            "count": {"$sum": 1},
                        }
                    },
                    {"$sort": {"count": -1}},
                    {"$limit": safe_limit},
                ],
                "feature_categories": [
                    {
                        "$match": {
                            "ai_analysis.feature_category": {
                                "$nin": [None, ""]
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": "$ai_analysis.feature_category",
                            "count": {"$sum": 1},
                        }
                    },
                    {"$sort": {"count": -1}},
                    {"$limit": safe_limit},
                ],
                "feature_requests": [
                    {
                        "$match": {
                            "ai_analysis.feature_opportunity": {
                                "$nin": [None, ""]
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": "$ai_analysis.feature_opportunity",
                            "count": {"$sum": 1},
                        }
                    },
                    {"$sort": {"count": -1}},
                    {"$limit": safe_limit},
                ],
                "sentiments": [
                    {
                        "$match": {
                            "ai_analysis.sentiment": {
                                "$nin": [None, ""]
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": "$ai_analysis.sentiment",
                            "count": {"$sum": 1},
                        }
                    },
                    {"$sort": {"count": -1}},
                ],
            }
        },
    ]

    cursor = await database.feedback.aggregate(pipeline)
    results = [result async for result in cursor]

    if not results:
        return {
            "total_analyzed": 0,
            "themes": [],
            "pain_points": [],
            "feature_categories": [],
            "feature_requests": [],
            "sentiments": [],
        }

    dashboard = results[0]
    total_result = dashboard.get("total_analyzed", [])

    dashboard["total_analyzed"] = (
        total_result[0]["count"] if total_result else 0
    )

    return dashboard


async def get_feedback_trends(
    workspace_id: str | None = None,
    days: int = 30,
) -> list[dict[str, Any]]:
    """Return daily analyzed-feedback totals for trend charts."""

    database = get_database()
    safe_days = max(1, min(days, 365))
    start_date = datetime.now(timezone.utc) - timedelta(
        days=safe_days
    )

    match = _analysis_match(workspace_id)
    match["ai_analysis.analyzed_at"] = {"$gte": start_date}

    pipeline = [
        {"$match": match},
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$ai_analysis.analyzed_at",
                    }
                },
                "feedback_count": {"$sum": 1},
                "feature_request_count": {
                    "$sum": {
                        "$cond": [
                            {
                                "$ne": [
                                    "$ai_analysis.feature_opportunity",
                                    None,
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "average_theme_confidence": {
                    "$avg": "$ai_analysis.confidence.theme"
                },
            }
        },
        {"$sort": {"_id": 1}},
        {
            "$project": {
                "_id": 0,
                "date": "$_id",
                "feedback_count": 1,
                "feature_request_count": 1,
                "average_theme_confidence": 1,
            }
        },
    ]

    cursor = await database.feedback.aggregate(pipeline)
    return [result async for result in cursor]