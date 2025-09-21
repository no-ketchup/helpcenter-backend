from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core import settings

# Async engine
engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    echo=settings.DEBUG,
    future=True,
)

# Session factory
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Context manager for internal code/tests
@asynccontextmanager
async def get_session_cm() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for GraphQL, services, or tests."""
    async with async_session_factory() as session:
        yield session

# FastAPI dependency
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields a session per request."""
    async with async_session_factory() as session:
        yield session