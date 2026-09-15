from typing import Any

from pymongo import ASCENDING, DESCENDING


async def create_indexes(database: Any) -> None:
    """Create indexes required by the application."""

    # Each user must have a unique email address.
    await database.users.create_index(
        [("email", ASCENDING)],
        unique=True,
        name="email_1",
    )

    # Each feedback record must have a unique feedback ID.
    await database.feedback.create_index(
        [("feedback_id", ASCENDING)],
        unique=True,
        name="unique_feedback_id",
    )

    # Support filtering feedback by workspace.
    await database.feedback.create_index(
        [("workspace_id", ASCENDING)],
        name="feedback_workspace",
    )

    # Support filtering feedback by source.
    await database.feedback.create_index(
        [("source", ASCENDING)],
        name="feedback_source",
    )

    # Support dashboard filtering by AI-generated theme.
    await database.feedback.create_index(
        [("ai_analysis.theme", ASCENDING)],
        name="feedback_theme",
    )

    # Support retrieving completed analysis by workspace and date.
    await database.feedback.create_index(
        [
            ("workspace_id", ASCENDING),
            ("ai_analysis.ai_status", ASCENDING),
            ("ai_analysis.analyzed_at", DESCENDING),
        ],
        name="feedback_analysis_status_date",
    )

    # Support dashboard grouping by feature category.
    await database.feedback.create_index(
        [
            ("workspace_id", ASCENDING),
            ("ai_analysis.feature_category", ASCENDING),
        ],
        name="feedback_feature_category",
    )

    # Support dashboard grouping by sentiment.
    await database.feedback.create_index(
        [
            ("workspace_id", ASCENDING),
            ("ai_analysis.sentiment", ASCENDING),
        ],
        name="feedback_sentiment",
    )

    # Support grouped feature-opportunity insights.
    await database.feedback.create_index(
        [
            ("workspace_id", ASCENDING),
            (
                "ai_analysis.feature_opportunity_group",
                ASCENDING,
            ),
        ],
        name="feedback_feature_group",
    )

    # Support finding workspaces belonging to a user.
    await database.workspaces.create_index(
        [("owner_id", ASCENDING)],
        name="workspace_owner",
    )

    # Support finding dataset imports for a workspace.
    await database.data_imports.create_index(
        [("workspace_id", ASCENDING)],
        name="data_import_workspace",
    )