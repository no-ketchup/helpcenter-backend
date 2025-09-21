from typing import Generic, TypeVar
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, select

T = TypeVar("T", bound=SQLModel)

class BaseMapper(Generic[T]):
    model: type[T]

    async def create(self, session: AsyncSession, obj: T) -> T:
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def get(self, session: AsyncSession, id) -> T | None:
        return await session.get(self.model, id)

    async def list(self, session: AsyncSession) -> list[T]:
        result = await session.exec(select(self.model))
        return result.all()