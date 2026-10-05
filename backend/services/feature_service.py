from uuid import uuid4

from database.feature_repository import (
    create_feature,
    get_feature_by_id,
    list_features,
)


async def create_feature_opportunity(
    workspace_id: str,
    title: str,
    description: str | None = None,
    theme: str | None = None,
    pain_point: str | None = None,
    feature_category: str | None = None,
    source_feedback_ids: list[str] | None = None,
    created_by: str | None = None,
):
    feature = await create_feature(
        {
            "feature_id": str(uuid4()),
            "workspace_id": workspace_id,
            "title": title,
            "description": description,
            "theme": theme,
            "pain_point": pain_point,
            "feature_category": feature_category,
            "source_feedback_ids": source_feedback_ids or [],
            "created_by": created_by,
        }
    )

    feature.pop("_id", None)

    return feature


async def get_feature_opportunity(feature_id: str):
    feature = await get_feature_by_id(feature_id)

    if feature is None:
        raise ValueError("Feature not found.")

    feature.pop("_id", None)

    return feature


async def get_feature_opportunities(
    workspace_id: str,
):
    features = await list_features(
        workspace_id=workspace_id,
    )

    for feature in features:
        feature.pop("_id", None)

    return features