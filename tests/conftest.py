import asyncio
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from alembic import command
from alembic.config import Config
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

# Set test environment before importing settings
os.environ["ENVIRONMENT"] = "test"

from app.core import settings
from app.core import db as core_db
from app.main import app


# -------------------------------
# Use a single event loop for the entire test session
# -------------------------------
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# -------------------------------
# Apply Alembic migrations once
# -------------------------------
@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    cfg = Config("alembic.ini")
    cfg.set_main_option("script_location", "app/migrations")
    cfg.set_main_option("sqlalchemy.url", settings.ACTIVE_DATABASE_URL)
    command.upgrade(cfg, "head")
    yield


# -------------------------------
# Session-scoped engine + sessionmaker
# -------------------------------
@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = core_db.get_engine()
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def async_sessionmaker(async_engine):
    factory = core_db.get_async_session_factory()
    return factory


# -------------------------------
# Database cleanup between tests
# -------------------------------
@pytest_asyncio.fixture(autouse=True)
async def cleanup_database(async_sessionmaker):
    """Clean up database before each test."""
    async with async_sessionmaker() as session:
        # Delete all data from tables in reverse dependency order
        from sqlalchemy import text
        await session.execute(text("DELETE FROM guidemedialink"))
        await session.execute(text("DELETE FROM guidecategorylink"))
        await session.execute(text("DELETE FROM media"))
        await session.execute(text("DELETE FROM userguide"))
        await session.execute(text("DELETE FROM category"))
        await session.execute(text("DELETE FROM feedback"))
        await session.commit()
    yield


# -------------------------------
# Override DB dependency to reuse sessionmaker
# -------------------------------
@pytest_asyncio.fixture(autouse=True)
async def override_get_session(async_sessionmaker):
    async def _override():
        async with async_sessionmaker() as session:
            yield session

    app.dependency_overrides[core_db.get_session] = _override
    yield
    app.dependency_overrides.clear()


# -------------------------------
# HTTP client
# -------------------------------
@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# -------------------------------
# Editor headers
# -------------------------------
@pytest.fixture
def editor_headers():
    return {"x-dev-editor-key": settings.DEV_EDITOR_KEY}