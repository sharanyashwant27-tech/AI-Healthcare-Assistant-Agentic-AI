"""Lightweight schema ensure for local SQLite (create_all does not ALTER columns)."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from core.logging import get_logger

logger = get_logger(__name__)

# table -> list of (column, ddl_type)
SQLITE_COLUMN_ADDS = {
    "doctors": [("hospital_id", "INTEGER")],
    "appointments": [("hospital_id", "INTEGER")],
    "lab_reports": [
        ("doctor_id", "INTEGER"),
        ("hospital_id", "INTEGER"),
    ],
}


async def ensure_sqlite_columns(conn: AsyncConnection) -> None:
    for table, columns in SQLITE_COLUMN_ADDS.items():
        exists = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name=:t"),
            {"t": table},
        )
        if not exists.first():
            continue
        info = await conn.execute(text(f"PRAGMA table_info({table})"))
        present = {row[1] for row in info.fetchall()}
        for col, col_type in columns:
            if col in present:
                continue
            await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
            logger.info("sqlite_column_added", table=table, column=col)
