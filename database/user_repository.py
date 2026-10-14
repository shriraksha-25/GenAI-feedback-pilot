from typing import Any

from database.connection import get_database


async def create_user(
    name: str,
    email: str,
    password_hash: str,
) -> dict[str, Any]:
    """Create a new application user."""

    database = get_database()

    user = {
        "name": name,
        "email": email.strip().lower(),
        "password_hash": password_hash,
        "role": "product_manager",
        "is_active": True,
    }

    await database.users.insert_one(user)

    return user


async def get_user_by_email(
    email: str,
) -> dict[str, Any] | None:
    """Find a user by email address."""

    database = get_database()

    return await database.users.find_one(
        {"email": email.strip().lower()}
    )