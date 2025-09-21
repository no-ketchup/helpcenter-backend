from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.repositories.base import BaseRepository
from app.domain.models import Category
from app.domain.dtos.category import CategoryCreateDTO, CategoryUpdateDTO, CategoryReadDTO
from app.utils.time import utcnow


class CategoryRepository(BaseRepository[Category]):
    def __init__(self):
        super().__init__(Category)

    async def create_from_dto(self, session: AsyncSession, dto: CategoryCreateDTO) -> Category:
        """Stage a new Category from DTO. Caller must commit/refresh."""
        obj = Category(**dto.model_dump())
        session.add(obj)
        return obj

    async def update_from_dto(self, session: AsyncSession, id: str, dto: CategoryUpdateDTO) -> Category:
        """Stage updates on a Category. Caller must commit/refresh."""
        obj = await self.get(session, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Category not found")

        for field, value in dto.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)

        obj.updated_at = utcnow()
        return obj

    async def delete(self, session: AsyncSession, id: str) -> None:
        """Stage a Category for deletion. Caller must commit/rollback."""
        obj = await self.get(session, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Category not found")
        await session.delete(obj)

    async def list_read(self, session: AsyncSession) -> list[CategoryReadDTO]:
        """Return all categories as DTOs (read-only, safe)."""
        rows = await self.list(session)
        return [CategoryReadDTO.model_validate(r) for r in rows]

    async def get_read(self, session: AsyncSession, id: str) -> CategoryReadDTO | None:
        obj = await self.get(session, id)
        return CategoryReadDTO.model_validate(obj) if obj else None

    async def get_by_slug(self, session: AsyncSession, slug: str) -> Category | None:
        return await self.get_by_field(session, "slug", slug)

    async def get_read_by_slug(self, session: AsyncSession, slug: str) -> CategoryReadDTO | None:
        obj = await self.get_by_slug(session, slug)
        return CategoryReadDTO.model_validate(obj) if obj else None