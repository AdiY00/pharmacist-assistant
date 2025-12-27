"""Database connection utilities."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

DATA_DIR = Path(__file__).parent.parent / "data"
SQL_DIR = Path(__file__).parent / "sql"

DATABASE_PATH = DATA_DIR / "pharmacy.db"
SCHEMA_PATH = SQL_DIR / "schema.sql"
SEED_PATH = SQL_DIR / "seed.sql"


def get_connection() -> sqlite3.Connection:
    """Create a new database connection with foreign keys enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def query_one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    """Execute a query and return a single row as a dict."""
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None


def query_all(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    """Execute a query and return all rows as a list of dicts."""
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


def execute(sql: str, params: tuple[Any, ...] = ()) -> int:
    """Execute a statement and return the lastrowid."""
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        return cursor.lastrowid or 0


def execute_many(sql: str, params_list: list[tuple[Any, ...]]) -> None:
    """Execute a statement with multiple parameter sets."""
    with get_db() as conn:
        conn.executemany(sql, params_list)


def init_db(seed: bool = False) -> None:
    """Initialize the database with the schema and optionally seed data."""
    DATA_DIR.mkdir(exist_ok=True)

    with get_db() as conn:
        with open(SCHEMA_PATH) as f:
            conn.executescript(f.read())

        if seed and SEED_PATH.exists():
            with open(SEED_PATH) as f:
                conn.executescript(f.read())
