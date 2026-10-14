
import asyncio

from database.connection import (
    connect_to_mongodb,
    close_mongodb_connection,
)


async def main():
    try:
        print("Connecting to MongoDB Atlas...")

        db = await connect_to_mongodb()

        print("MongoDB connection: SUCCESS")
        print("Database:", db.name)

        ping_result = await db.command("ping")
        print("MongoDB ping:", ping_result)

        roadmap_count = await db.roadmaps.count_documents({})
        summary_count = await db.executive_summaries.count_documents({})

        print("\n--- Existing Database Records ---")
        print("Roadmap records:", roadmap_count)
        print("Executive summary records:", summary_count)

        print("\nDatabase connectivity and read checks: PASS")

    except Exception as error:
        print("\nDatabase test: FAILED")
        print("Error type:", type(error).__name__)
        print("Error details:", str(error))

    finally:
        await close_mongodb_connection()
        print("\nMongoDB connection closed.")


if __name__ == "__main__":
    asyncio.run(main())
