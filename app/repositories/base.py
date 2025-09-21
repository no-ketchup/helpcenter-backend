from typing import Generic, TypeVar, Type, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, select
from sqlalchemy import select as sa_select

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    """Generic async repository for SQLModel entities.
    Does not commit/rollback — caller controls transactions.
    """

    def __init__(self, model: Type[T]):
        self.model = model

    async def create(self, session: AsyncSession, obj: T) -> T:
        """Stage a new object for insertion (no commit)."""
        session.add(obj)
        return obj

    async def get(self, session: AsyncSession, id: str | int) -> Optional[T]:
        """Fetch an object by primary key."""
        return await session.get(self.model, id)

    async def list(self, session: AsyncSession) -> list[T]:
        """Fetch all objects."""
        result = await session.exec(select(self.model))
        return result.all()

    async def update(self, session: AsyncSession, id: str | int, **kwargs) -> Optional[T]:
        """Apply updates to an object by id (no commit)."""
        obj = await session.get(self.model, id)
        if not obj:
            return None
        for k, v in kwargs.items():
            setattr(obj, k, v)
        return obj

    async def delete(self, session: AsyncSession, id: str | int) -> bool:
        """Stage an object for deletion (no commit)."""
        obj = await session.get(self.model, id)
        if not obj:
            return False
        await session.delete(obj)
        return True

    async def get_by_field(self, session: AsyncSession, field: str, value) -> Optional[T]:
        """Fetch first object where a given field == value."""
        stmt = sa_select(self.model).where(getattr(self.model, field) == value)
        result = await session.exec(stmt)
        return result.first()