"""
Base repository for SQLModel entities.

Provides generic CRUD operations with async SQLAlchemy sessions.
Caller controls transaction commits/rollbacks.
"""

from typing import Generic, Optional, Type, TypeVar

from sqlalchemy import select as sa_select
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    """Generic async repository for SQLModel entities."""

    def __init__(self, model: Type[T]):
        self.model = model

    async def create(self, session: AsyncSession, obj: T) -> T:
        """Stage a new object for insertion."""
        session.add(obj)
        return obj

    async def get(self, session: AsyncSession, id: str | int) -> Optional[T]:
        """Fetch an object by primary key."""
        return await session.get(self.model, id)

    async def list(self, session: AsyncSession) -> list[T]:
        """Fetch all objects."""
        result = await session.execute(sa_select(self.model))
        return result.scalars().all()

    async def update(self, session: AsyncSession, obj: T) -> T:
        """Stage an object for update."""
        session.add(obj)
        return obj

    async def delete(self, session: AsyncSession, id: str | int) -> bool:
        """Delete an object by primary key."""
        obj = await session.get(self.model, id)
        if obj:
            await session.delete(obj)
            return True
        return False

    async def get_by_field(self, session: AsyncSession, field: str, value: any) -> Optional[T]:
        """Get an object by a specific field value."""
        from sqlalchemy import select as sa_select

        stmt = sa_select(self.model).where(getattr(self.model, field) == value)
        result = await session.execute(stmt)
        return result.scalars().first()
