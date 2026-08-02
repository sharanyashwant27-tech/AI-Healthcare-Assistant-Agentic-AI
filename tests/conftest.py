import os

os.environ.setdefault("USE_SQLITE", "true")
os.environ.setdefault("SQLITE_PATH", "./test_ai_healthcare.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-ai-healthcare-assistant")
os.environ.setdefault("APP_DEBUG", "false")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from database import Base, engine, init_db
from main import app
from database import AsyncSessionLocal
from utils.seed import seed_database


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await seed_database(session)
        await session.commit()
    yield


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
