"""
Database configuration and session management.

Handles async SQLAlchemy engine creation with appropriate connection pooling
for different environments (test, development, production).
"""

import ssl
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.pool.impl import AsyncAdaptedQueuePool
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import settings

_engine = None
_async_session_factory = None


def _new_engine():
    """Create a new async engine with environment-appropriate pooling."""
    kwargs = {
        "echo": settings.DEBUG,
        "future": True,
    }

    if settings.ENVIRONMENT == "test":
        kwargs["poolclass"] = NullPool
    else:
        kwargs.update(
            {
                "poolclass": AsyncAdaptedQueuePool,
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_pre_ping": True,
                "pool_recycle": settings.DB_POOL_RECYCLE,
            }
        )

    url = make_url(settings.DATABASE_URL)
    connect_args = {}

    # Handle asyncpg + sslmode=require
    if url.drivername.startswith("postgresql+asyncpg"):
        if "sslmode=require" in str(url):
            ssl_context = ssl.create_default_context()
            connect_args["ssl"] = ssl_context
            # Remove sslmode from URL to avoid conflicts
            url_str = str(url).replace("?sslmode=require", "").replace("&sslmode=require", "")
            url = make_url(url_str)

    return create_async_engine(url, connect_args=connect_args, **kwargs)


def get_engine():
    """Get or create the global engine."""
    global _engine
    if _engine is None:
        _engine = _new_engine()
    return _engine


def get_async_session_factory():
    """Get or create the global session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = sessionmaker(
            bind=get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _async_session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    async_session_factory = get_async_session_factory()
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_session_dependency() -> AsyncSession:
    """FastAPI dependency that provides a database session."""
    async_session_factory = get_async_session_factory()
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


def close_engine():
    """Close the global engine."""
    global _engine, _async_session_factory
    if _engine is not None:
        _engine.sync_engine.dispose()
        _engine = None
        _async_session_factory = None
