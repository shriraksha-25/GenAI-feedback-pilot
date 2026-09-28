"""Versioned PRD and user-story persistence for Milestone 3."""

from datetime import datetime, timezone
from typing import Any

from pymongo import DESCENDING, ReturnDocument

from database.connection import get_database
from database.milestone3_models import (
    PRDVersionRecord,
    ReviewStatus,
    UserStoryVersionRecord,
)


async def save_prd_version(
    prd: PRDVersionRecord | dict[str, Any],
) -> dict[str, Any]:
    """Store a new PRD version without overwriting previous versions."""

    database = get_database()

    prd_model = (
        prd
        if isinstance(prd, PRDVersionRecord)
        else PRDVersionRecord.model_validate(prd)
    )

    latest = await database.prds.find_one(
        {"prd_id": prd_model.prd_id},
        sort=[("version", DESCENDING)],
    )

    next_version = 1

    if latest is not None:
        next_version = latest.get("version", 0) + 1

    document = prd_model.model_dump(mode="python")
    document["version"] = next_version
    document["is_current"] = True
    document["created_at"] = datetime.now(timezone.utc)

    await database.prds.update_many(
        {
            "prd_id": prd_model.prd_id,
            "is_current": True,
        },
        {
            "$set": {
                "is_current": False,
            }
        },
    )

    await database.prds.insert_one(document)

    await database.features.update_one(
        {"feature_id": prd_model.feature_id},
        {
            "$set": {
                "status": "prd_generated",
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    return document


async def get_current_prd(
    prd_id: str,
) -> dict[str, Any] | None:
    """Retrieve the current version of a PRD."""

    database = get_database()

    return await database.prds.find_one(
        {
            "prd_id": prd_id,
            "is_current": True,
        }
    )


async def get_current_prd_for_feature(
    feature_id: str,
) -> dict[str, Any] | None:
    """Retrieve the current PRD associated with a feature."""

    database = get_database()

    return await database.prds.find_one(
        {
            "feature_id": feature_id,
            "is_current": True,
        },
        sort=[("created_at", DESCENDING)],
    )


async def get_prd_history(
    prd_id: str,
) -> list[dict[str, Any]]:
    """Retrieve all versions of a PRD."""

    database = get_database()

    cursor = (
        database.prds
        .find({"prd_id": prd_id})
        .sort("version", DESCENDING)
    )

    return [document async for document in cursor]


async def update_prd_review_status(
    prd_id: str,
    status: ReviewStatus,
    reviewed_by: str,
) -> dict[str, Any] | None:
    """Update the review status of the current PRD."""

    database = get_database()
    now = datetime.now(timezone.utc)

    update_fields: dict[str, Any] = {
        "review_status": status,
    }

    if status == "approved":
        update_fields["approved_by"] = reviewed_by
        update_fields["approved_at"] = now
    else:
        update_fields["approved_by"] = None
        update_fields["approved_at"] = None

    return await database.prds.find_one_and_update(
        {
            "prd_id": prd_id,
            "is_current": True,
        },
        {
            "$set": update_fields,
        },
        return_document=ReturnDocument.AFTER,
    )


async def save_user_story_version(
    user_story: UserStoryVersionRecord | dict[str, Any],
) -> dict[str, Any]:
    """Store a new user-story version without deleting its history."""

    database = get_database()

    story_model = (
        user_story
        if isinstance(user_story, UserStoryVersionRecord)
        else UserStoryVersionRecord.model_validate(user_story)
    )

    latest = await database.user_stories.find_one(
        {"user_story_id": story_model.user_story_id},
        sort=[("version", DESCENDING)],
    )

    next_version = 1

    if latest is not None:
        next_version = latest.get("version", 0) + 1

    document = story_model.model_dump(mode="python")
    document["version"] = next_version
    document["is_current"] = True
    document["created_at"] = datetime.now(timezone.utc)

    await database.user_stories.update_many(
        {
            "user_story_id": story_model.user_story_id,
            "is_current": True,
        },
        {
            "$set": {
                "is_current": False,
            }
        },
    )

    await database.user_stories.insert_one(document)

    await database.features.update_one(
        {"feature_id": story_model.feature_id},
        {
            "$set": {
                "status": "stories_generated",
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    return document


async def get_current_user_story(
    user_story_id: str,
) -> dict[str, Any] | None:
    """Retrieve the current version of a user story."""

    database = get_database()

    return await database.user_stories.find_one(
        {
            "user_story_id": user_story_id,
            "is_current": True,
        }
    )


async def get_current_stories_for_feature(
    feature_id: str,
) -> list[dict[str, Any]]:
    """Retrieve all current user stories for a feature."""

    database = get_database()

    cursor = (
        database.user_stories
        .find(
            {
                "feature_id": feature_id,
                "is_current": True,
            }
        )
        .sort("created_at", DESCENDING)
    )

    return [document async for document in cursor]


async def get_user_story_history(
    user_story_id: str,
) -> list[dict[str, Any]]:
    """Retrieve every saved version of a user story."""

    database = get_database()

    cursor = (
        database.user_stories
        .find({"user_story_id": user_story_id})
        .sort("version", DESCENDING)
    )

    return [document async for document in cursor]


async def update_user_story_review_status(
    user_story_id: str,
    status: ReviewStatus,
    reviewed_by: str,
) -> dict[str, Any] | None:
    """Update the review status of the current user story."""

    database = get_database()
    now = datetime.now(timezone.utc)

    update_fields: dict[str, Any] = {
        "review_status": status,
    }

    if status == "approved":
        update_fields["approved_by"] = reviewed_by
        update_fields["approved_at"] = now
    else:
        update_fields["approved_by"] = None
        update_fields["approved_at"] = None

    return await database.user_stories.find_one_and_update(
        {
            "user_story_id": user_story_id,
            "is_current": True,
        },
        {
            "$set": update_fields,
        },
        return_document=ReturnDocument.AFTER,
    )