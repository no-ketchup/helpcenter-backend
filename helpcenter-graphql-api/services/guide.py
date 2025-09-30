from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.dtos.guide import (
    GuideCreateDTO,
    GuideReadDTO,
    GuideUpdateDTO,
)
from app.repositories.guide import GuideRepository


class GuideService:
    def __init__(self, repo: GuideRepository | None = None):
        self.repo = repo or GuideRepository()

    async def create_guide(self, session: AsyncSession, dto: GuideCreateDTO) -> GuideReadDTO:
        """Create a new guide with rich text content."""
        obj = await self.repo.create_from_dto(session, dto)
        try:
            await session.commit()
            await session.refresh(obj)
            # Reload with categories to get the full DTO
            return await self.repo.get_read(session, obj.id)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=409, detail="Slug already exists")

    async def update_guide(
        self, session: AsyncSession, id: UUID, dto: GuideUpdateDTO
    ) -> GuideReadDTO:
        """Update a guide with rich text content."""
        obj = await self.repo.update_from_dto(session, id, dto)
        if not obj:
            raise HTTPException(status_code=404, detail="Guide not found")
        try:
            await session.commit()
            await session.refresh(obj)
            # Reload with categories to get the full DTO
            return await self.repo.get_read(session, obj.id)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=409, detail="Slug already exists")

    async def delete_guide(self, session: AsyncSession, id: UUID) -> None:
        """Delete a guide."""
        obj = await self.repo.get(session, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Guide not found")
        await self.repo.delete(session, id)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete guide")

    async def list_guides(
        self, session: AsyncSession, category_slug: str | None = None
    ) -> list[GuideReadDTO]:
        """List guides, optionally filtered by category slug."""
        return await self.repo.list_read(session, category_slug)

    async def get_guide(self, session: AsyncSession, id: UUID) -> GuideReadDTO | None:
        """Get a guide by ID."""
        return await self.repo.get_read(session, id)

    async def get_guide_by_slug(self, session: AsyncSession, slug: str) -> GuideReadDTO | None:
        """Get a guide by slug."""
        return await self.repo.get_read_by_slug(session, slug)

    async def list_guides_by_category(
        self, session: AsyncSession, category_id: str
    ) -> list[GuideReadDTO]:
        """List guides for a specific category."""
        return await self.repo.list_read_by_category(session, category_id)

    async def get_guide_categories(self, session: AsyncSession, guide_id: str) -> list:
        """Get categories for a specific guide."""
        return await self.repo.get_categories(session, guide_id)
