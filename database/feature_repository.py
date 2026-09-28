"""Store and retrieve Milestone 3 feature opportunities."""

from datetime import datetime, timezone
from typing import Any

from pymongo import DESCENDING, ReturnDocument

from database.connection import get_database
from database.milestone3_models import (
    FeatureEvidenceRecord,
    FeatureRecord,
    FeatureStatus,
)


async def create_feature(
    feature: FeatureRecord | dict[str, Any],
) -> dict[str, Any]:
    """Create a feature opportunity from Milestone 2 insights."""

    database = get_database()

    feature_model = (
        feature
        if isinstance(feature, FeatureRecord)
        else FeatureRecord.model_validate(feature)
    )

    document = feature_model.model_dump(mode="python")
    await database.features.insert_one(document)

    return document


async def get_feature_by_id(
    feature_id: str,
) -> dict[str, Any] | None:
    """Retrieve one feature using its public feature ID."""

    database = get_database()

    return await database.features.find_one(
        {"feature_id": feature_id}
    )


async def list_features(
    workspace_id: str,
    status: str | None = None,
    limit: int = 50,
    skip: int = 0,
) -> list[dict[str, Any]]:
    """Retrieve features belonging to a workspace."""

    database = get_database()

    query: dict[str, Any] = {
        "workspace_id": workspace_id,
    }

    if status is not None:
        query["status"] = status

    safe_limit = max(1, min(limit, 100))
    safe_skip = max(0, skip)

    cursor = (
        database.features
        .find(query)
        .sort("updated_at", DESCENDING)
        .skip(safe_skip)
        .limit(safe_limit)
    )

    return [document async for document in cursor]


async def update_feature_status(
    feature_id: str,
    status: FeatureStatus,
) -> dict[str, Any] | None:
    """Update a feature's workflow status."""

    database = get_database()

    return await database.features.find_one_and_update(
        {"feature_id": feature_id},
        {
            "$set": {
                "status": status,
                "updated_at": datetime.now(timezone.utc),
            }
        },
        return_document=ReturnDocument.AFTER,
    )


async def add_feature_evidence(
    evidence: FeatureEvidenceRecord | dict[str, Any],
) -> dict[str, Any]:
    """Link one feedback record to a feature opportunity."""

    database = get_database()

    evidence_model = (
        evidence
        if isinstance(evidence, FeatureEvidenceRecord)
        else FeatureEvidenceRecord.model_validate(evidence)
    )

    document = evidence_model.model_dump(mode="python")
    await database.feature_evidence.insert_one(document)

    await database.features.update_one(
        {"feature_id": evidence_model.feature_id},
        {
            "$addToSet": {
                "source_feedback_ids": evidence_model.feedback_id
            },
            "$set": {
                "updated_at": datetime.now(timezone.utc),
            },
        },
    )

    return document


async def get_feature_evidence(
    feature_id: str,
) -> list[dict[str, Any]]:
    """Retrieve all evidence linked to a feature."""

    database = get_database()

    cursor = (
        database.feature_evidence
        .find({"feature_id": feature_id})
        .sort("created_at", DESCENDING)
    )

    return [document async for document in cursor]


async def get_feature_with_evidence(
    feature_id: str,
) -> dict[str, Any] | None:
    """Retrieve a feature together with its supporting evidence."""

    feature = await get_feature_by_id(feature_id)

    if feature is None:
        return None

    feature["evidence"] = await get_feature_evidence(feature_id)

    return feature


async def get_features_for_feedback(
    feedback_id: str,
) -> list[dict[str, Any]]:
    """Find all features supported by a feedback record."""

    database = get_database()

    cursor = (
        database.features
        .find({"source_feedback_ids": feedback_id})
        .sort("updated_at", DESCENDING)
    )

    return [document async for document in cursor]