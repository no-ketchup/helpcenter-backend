import os
import sys
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from alembic import command
from alembic.config import Config

from app.core import settings
from app.core.db import async_session_factory
from app.main import app

# Always enforce test env
os.environ.setdefault("ENVIRONMENT", "test")


# -------------------------------
# Database setup: migrations
# -------------------------------
@pytest_asyncio.fixture(scope="session", autouse=True)
async def apply_migrations():
    """Run alembic migrations before the test session."""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "app/migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    # Run migrations
    command.upgrade(alembic_cfg, "head")

    yield

    # Tear down: reset schema if Postgres (SQLite drops with process)
    if settings.DATABASE_URL.startswith("postgresql"):
        async with async_session_factory() as s:
            async with s.begin():
                await s.execute(text("DROP SCHEMA public CASCADE"))
                await s.execute(text("CREATE SCHEMA public"))


# -------------------------------
# HTTP client fixture
# -------------------------------
@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# -------------------------------
# Editor headers fixture
# -------------------------------
@pytest.fixture
def editor_headers():
    return {"x-dev-editor-key": settings.DEV_EDITOR_KEY}


# -------------------------------
# Session fixture
# -------------------------------
@pytest_asyncio.fixture
async def session() -> AsyncSession:
    """Provide a fresh DB session with rollback after each test."""
    async with async_session_factory() as s:
        trans = await s.begin()
        try:
            yield s
        finally:
            if trans.is_active:
                await trans.rollback()