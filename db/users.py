"""Users repository."""

from db.connection import execute, query_all, query_one
from db.models import User


def _row_to_user(row: dict) -> User:
    """Convert a database row to a User model."""
    return User(
        id=row["id"],
        pin=row["pin"],
        name=row["name"],
        created_at=row["created_at"],
    )


def get_by_id(user_id: int) -> User | None:
    """Get a user by ID."""
    row = query_one("SELECT * FROM users WHERE id = ?", (user_id,))
    if not row:
        return None
    return _row_to_user(row)


def get_by_pin(pin: str) -> User | None:
    """Get a user by their 4-digit PIN."""
    row = query_one("SELECT * FROM users WHERE pin = ?", (pin,))
    if not row:
        return None
    return _row_to_user(row)


def search_by_name(name: str) -> list[User]:
    """Search users by name (partial match)."""
    rows = query_all(
        "SELECT * FROM users WHERE LOWER(name) LIKE LOWER(?) ORDER BY name",
        (f"%{name}%",),
    )
    return [_row_to_user(row) for row in rows]


def create(pin: str, name: str) -> User:
    """Create a new user."""
    user_id = execute(
        "INSERT INTO users (pin, name) VALUES (?, ?)",
        (pin, name),
    )
    user = get_by_id(user_id)
    if not user:
        raise RuntimeError("Failed to create user")
    return user


def get_all() -> list[User]:
    """Get all users."""
    rows = query_all("SELECT * FROM users ORDER BY name")
    return [_row_to_user(row) for row in rows]
