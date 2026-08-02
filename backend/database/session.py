"""SQLAlchemy async database engine and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from core.config import settings

connect_args = {}
if settings.use_sqlite:
    connect_args = {"check_same_thread": False, "timeout": 30}

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,
    pool_pre_ping=not settings.use_sqlite,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    import models  # noqa: F401
    from sqlalchemy import text

    from database.migrate import ensure_sqlite_columns

    async with engine.begin() as conn:
        if settings.use_sqlite:
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA busy_timeout=30000"))
        await conn.run_sync(Base.metadata.create_all)
        if settings.use_sqlite:
            await ensure_sqlite_columns(conn)
