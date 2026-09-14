from typing import Any

from pymongo import ASCENDING


async def create_indexes(database: Any) -> None:
    """Create indexes required by the application."""

    # Each user must have a unique email address.
    await database.users.create_index(
        [("email", ASCENDING)],
        unique=True,
        name="email_1",
    )

    # Each normalized feedback record must have a unique feedback ID.
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