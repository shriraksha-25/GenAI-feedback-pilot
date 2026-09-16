import asyncio

from fastapi import APIRouter

from ai.services.feature_clustering import cluster_feature_requests
from database.connection import get_database
from database.dashboard_queries import (
    get_dashboard_insights as fetch_dashboard_insights,
    get_feedback_trends as fetch_feedback_trends,
)


insights_router = APIRouter(
    prefix="/insights",
    tags=["Product Insights"]
)


# =========================================================
# CONSOLIDATED DASHBOARD
# =========================================================

@insights_router.get("/dashboard")
async def get_dashboard():
    try:
        dashboard = await fetch_dashboard_insights()

        return {
            "dashboard": dashboard,
            "database_status": "connected"
        }

    except RuntimeError:
        return {
            "dashboard": {
                "total_analyzed": 0,
                "themes": [],
                "pain_points": [],
                "feature_categories": [],
                "feature_requests": [],
                "sentiments": []
            },
            "database_status": "unavailable"
        }


# =========================================================
# SUMMARY
# =========================================================

@insights_router.get("/summary")
async def get_insights_summary():
    try:
        database = get_database()
        feedback_collection = database["feedback"]

        total_feedback = await feedback_collection.count_documents({})

        negative_feedback = await feedback_collection.count_documents(
            {"ai_analysis.sentiment": "negative"}
        )

        return {
            "total_feedback": total_feedback,
            "negative_feedback": negative_feedback,
            "database_status": "connected"
        }

    except RuntimeError:
        return {
            "total_feedback": 0,
            "negative_feedback": 0,
            "database_status": "unavailable"
        }


# =========================================================
# SENTIMENTS
# =========================================================

@insights_router.get("/sentiments")
async def get_sentiment_insights():
    try:
        database = get_database()
        feedback_collection = database["feedback"]

        pipeline = [
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
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]

        cursor = await feedback_collection.aggregate(pipeline)

        sentiments = []

        async for item in cursor:
            sentiments.append({
                "sentiment": item["_id"],
                "count": item["count"]
            })

        return {
            "sentiments": sentiments,
            "database_status": "connected"
        }

    except RuntimeError:
        return {
            "sentiments": [],
            "database_status": "unavailable"
        }


# =========================================================
# CATEGORIES
# =========================================================

@insights_router.get("/categories")
async def get_category_insights():
    try:
        database = get_database()
        feedback_collection = database["feedback"]

        pipeline = [
            {
                "$match": {
                    "ai_analysis.category": {
                        "$nin": [None, ""]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$ai_analysis.category",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]

        cursor = await feedback_collection.aggregate(pipeline)

        categories = []

        async for item in cursor:
            categories.append({
                "category": item["_id"],
                "count": item["count"]
            })

        return {
            "categories": categories,
            "database_status": "connected"
        }

    except RuntimeError:
        return {
            "categories": [],
            "database_status": "unavailable"
        }


# =========================================================
# THEMES
# =========================================================

@insights_router.get("/themes")
async def get_theme_insights():
    try:
        database = get_database()
        feedback_collection = database["feedback"]

        pipeline = [
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
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]

        cursor = await feedback_collection.aggregate(pipeline)

        themes = []

        async for item in cursor:
            themes.append({
                "theme": item["_id"],
                "count": item["count"]
            })

        return {
            "themes": themes,
            "database_status": "connected"
        }

    except RuntimeError:
        return {
            "themes": [],
            "database_status": "unavailable"
        }


# =========================================================
# PAIN POINTS
# =========================================================

@insights_router.get("/pain-points")
async def get_pain_point_insights():
    try:
        database = get_database()
        feedback_collection = database["feedback"]

        pipeline = [
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
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]

        cursor = await feedback_collection.aggregate(pipeline)

        pain_points = []

        async for item in cursor:
            pain_points.append({
                "pain_point": item["_id"],
                "count": item["count"]
            })

        return {
            "pain_points": pain_points,
            "database_status": "connected"
        }

    except RuntimeError:
        return {
            "pain_points": [],
            "database_status": "unavailable"
        }


# =========================================================
# FEATURE REQUESTS
# =========================================================

@insights_router.get("/feature-requests")
async def get_feature_request_insights():
    try:
        database = get_database()
        feedback_collection = database["feedback"]

        pipeline = [
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
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]

        cursor = await feedback_collection.aggregate(pipeline)

        feature_requests = []

        async for item in cursor:
            feature_requests.append({
                "feature_request": item["_id"],
                "count": item["count"]
            })

        return {
            "feature_requests": feature_requests,
            "database_status": "connected"
        }

    except RuntimeError:
        return {
            "feature_requests": [],
            "database_status": "unavailable"
        }


# =========================================================
# FEATURE CLUSTERS
# =========================================================

@insights_router.get("/feature-clusters")
async def get_feature_clusters():
    try:
        database = get_database()
        feedback_collection = database["feedback"]

        cursor = feedback_collection.find(
            {
                "ai_analysis.feature_opportunity": {
                    "$nin": [None, ""]
                }
            },
            {
                "feedback_id": 1,
                "ai_analysis.feature_opportunity": 1
            }
        )

        items = []

        async for document in cursor:
            ai_analysis = document.get("ai_analysis", {})

            feature_request = ai_analysis.get(
                "feature_opportunity"
            )

            if feature_request:
                items.append({
                    "feedback_id": document.get("feedback_id"),
                    "feature_request": feature_request
                })

        if not items:
            return {
                "feature_clusters": [],
                "database_status": "connected"
            }

        clustered_items = await asyncio.to_thread(
            cluster_feature_requests,
            items
        )

        clusters = {}

        for item in clustered_items:
            group = item["feature_opportunity_group"]

            if group not in clusters:
                clusters[group] = {
                    "feature_opportunity_group": group,
                    "count": 0,
                    "requests": []
                }

            clusters[group]["count"] += 1

            clusters[group]["requests"].append({
                "feedback_id": item.get("feedback_id"),
                "feature_request": item.get("feature_request")
            })

        feature_clusters = sorted(
            clusters.values(),
            key=lambda cluster: cluster["count"],
            reverse=True
        )

        return {
            "feature_clusters": feature_clusters,
            "database_status": "connected"
        }

    except RuntimeError:
        return {
            "feature_clusters": [],
            "database_status": "unavailable"
        }


# =========================================================
# TRENDS
# =========================================================

@insights_router.get("/trends")
async def get_feedback_trends():
    try:
        trends = await fetch_feedback_trends()

        return {
            "trends": trends,
            "database_status": "connected"
        }

    except RuntimeError:
        return {
            "trends": [],
            "database_status": "unavailable"
        }