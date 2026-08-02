"""Database schema catalog API."""

from fastapi import APIRouter
from sqlalchemy import inspect

from auth.deps import CurrentUser
from database.session import engine
from models.catalog import DATABASE_TABLES

router = APIRouter()


@router.get("/database/tables")
async def list_database_tables(user: CurrentUser):
    existing: list[str] = []
    try:
        async with engine.connect() as conn:
            tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
            existing = sorted(tables)
    except Exception:  # noqa: BLE001
        existing = []

    return {
        "canonical_tables": DATABASE_TABLES,
        "existing_tables": existing,
        "count": len(DATABASE_TABLES),
    }
