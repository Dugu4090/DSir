from __future__ import annotations

import os

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from src.db.base import Base
from src.db.session import get_db
from src.main import app

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), ".test_db.sqlite")
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"


@pytest_asyncio.fixture(scope="session")
def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    return engine


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_tables(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(test_engine):
    conn = await test_engine.connect()
    session = AsyncSession(bind=conn)

    yield session

    await session.close()
    # Cleanup all data after each test for isolation
    async with test_engine.begin() as cleanup_conn:
        for table in reversed(Base.metadata.sorted_tables):
            await cleanup_conn.execute(table.delete())
    await conn.close()


@pytest_asyncio.fixture
async def client(db_session):
    from fastapi.testclient import TestClient

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
