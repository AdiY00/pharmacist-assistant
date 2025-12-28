"""Database repositories for data access."""

# Note: Import order matters to avoid circular imports.
# medications and users must be imported first since
# prescriptions and stock depend on them.
from db.repositories import medications as medications
from db.repositories import users as users
from db.repositories import prescriptions as prescriptions
from db.repositories import stock as stock

__all__ = [
    "medications",
    "prescriptions",
    "stock",
    "users",
]
