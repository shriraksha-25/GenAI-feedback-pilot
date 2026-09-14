from typing import Any

from pymongo import AsyncMongoClient

from database.config import get_settings


_client: AsyncMongoClient | None = None
_database: Any = None


async def connect_to_mongodb() -> Any:
    """Connect to MongoDB and return the configured database."""

    global _client, _database

    settings = get_settings()

    _client = AsyncMongoClient(settings.mongodb_uri)

    # Verify that Atlas is reachable and the credentials are valid.
    await _client.admin.command("ping")

    _database = _client[settings.mongodb_database]

    return _database


def get_database() -> Any:
    """Return the active database connection."""

    if _database is None:
        raise RuntimeError(
            "MongoDB is not connected. Call connect_to_mongodb() first."
        )

    return _database


async def close_mongodb_connection() -> None:
    """Close the MongoDB connection."""

    global _client, _database

    if _client is not None:
        await _client.close()

    _client = None
    _database = None