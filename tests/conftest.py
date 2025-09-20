import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import async_session, engine
from app.data.seeds import seed
from alembic import command
from alembic.config import Config
import os


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """
    Run Alembic migrations and seed test DB once per session.
    Drops everything afterwards.
    """
    # Run Alembic migrations (upgrade head)
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "../app/migrations/alembic.ini"))
    alembic_cfg.set_main_option("script_location", "app/migrations")
    command.upgrade(alembic_cfg, "head")

    # Seed DB
    async with async_session() as session:
        assert isinstance(session, AsyncSession)
        await seed(session)

    yield

    # Teardown: drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(lambda conn: conn.exec_driver_sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))