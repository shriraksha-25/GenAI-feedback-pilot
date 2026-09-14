import asyncio

from database.connection import (
    close_mongodb_connection,
    connect_to_mongodb,
)
from database.indexes import create_indexes


async def initialize_database() -> None:
    """Test MongoDB connectivity and create application indexes."""

    database = await connect_to_mongodb()

    try:
        await create_indexes(database)

        collections = await database.list_collection_names()

        print("MongoDB connection successful")
        print(f"Database: {database.name}")
        print("Indexes created successfully")
        print(f"Collections: {', '.join(sorted(collections))}")

    finally:
        await close_mongodb_connection()


if __name__ == "__main__":
    try:
        asyncio.run(initialize_database())
    except Exception as error:
        print(f"Database initialization failed: {error}")
        raise SystemExit(1)