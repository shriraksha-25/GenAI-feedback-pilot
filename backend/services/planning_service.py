from datetime import datetime, timezone
from uuid import uuid4

from database.connection import get_database


PLANNING_COLLECTION = "planning_items"


async def get_planning_items():
    db = get_database()

    cursor = db[PLANNING_COLLECTION].find(
        {},
        {"_id": 0},
    ).sort("created_at", -1)

    return await cursor.to_list(length=100)


async def create_planning_item(data):
    db = get_database()

    item = {
        "id": str(uuid4()),
        "title": data.title,
        "description": data.description or "",
        "priority": data.priority or "Medium",
        "target_area": data.target_area or "Core Product",
        "notes": data.notes or "",
        "status": data.status or "Planned",
        "related_opportunity": data.related_opportunity,
        "created_at": datetime.now(timezone.utc),
    }

    await db[PLANNING_COLLECTION].insert_one(item)

    item.pop("_id", None)
    return item


async def update_planning_item(item_id, data):
    db = get_database()

    update_data = {
        key: value
        for key, value in data.model_dump(exclude_unset=True).items()
        if value is not None
    }

    if not update_data:
        return None

    result = await db[PLANNING_COLLECTION].update_one(
        {"id": item_id},
        {"$set": update_data},
    )

    if result.matched_count == 0:
        return None

    return await db[PLANNING_COLLECTION].find_one(
        {"id": item_id},
        {"_id": 0},
    )