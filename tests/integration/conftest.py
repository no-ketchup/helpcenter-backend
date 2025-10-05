"""Configuration for integration tests - WITH REAL DATABASE."""

import asyncio
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import text

# Set test environment for integration tests
os.environ["ENVIRONMENT"] = "test"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["DEV_EDITOR_KEY"] = "test-editor-key"

# Use PostgreSQL test database (like in GitHub Actions)
test_db_url = os.getenv("TEST_DATABASE_URL_ASYNC", "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db")
os.environ["DATABASE_URL_ASYNC"] = test_db_url

from graphql_api.main import app
from common.core.db import get_async_session_factory


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(test_db_url)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine):
    """Create test database session."""
    async with AsyncSession(test_engine) as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def test_session_maker(test_engine):
    """Create test session maker."""
    async_session_factory = async_sessionmaker(
        test_engine, class_=SQLModelAsyncSession, expire_on_commit=False
    )
    return async_session_factory


@pytest_asyncio.fixture(autouse=True)
async def cleanup_database(test_session):
    """Clean up database before each test."""
    async with test_session as session:
        # Delete all data from tables in reverse dependency order
        await session.execute(text("DELETE FROM guidemedialink"))
        await session.execute(text("DELETE FROM guidecategorylink"))
        await session.execute(text("DELETE FROM userguide"))
        await session.execute(text("DELETE FROM media"))
        await session.execute(text("DELETE FROM category"))
        await session.execute(text("DELETE FROM feedback"))
        await session.commit()


@pytest.fixture
async def async_client():
    """Create async test client for integration tests."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

