from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from ..domain.dtos.category import (
    CategoryCreateDTO,
    CategoryReadDTO,
    CategoryUpdateDTO,
)
from ..repositories.category import CategoryRepository


class CategoryService:
    def __init__(self, repo: CategoryRepository | None = None):
        self.repo = repo or CategoryRepository()

    async def create_category(
        self, session: AsyncSession, dto: CategoryCreateDTO
    ) -> CategoryReadDTO:
        obj = await self.repo.create_from_dto(session, dto)
        try:
            await session.commit()
            await session.refresh(obj)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=409, detail="Slug already exists")
        return CategoryReadDTO.model_validate(obj)

    async def update_category(
        self, session: AsyncSession, id: str, dto: CategoryUpdateDTO
    ) -> CategoryReadDTO:
        obj = await self.repo.update_from_dto(session, id, dto)
        try:
            await session.commit()
            await session.refresh(obj)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=409, detail="Slug already exists")
        return CategoryReadDTO.model_validate(obj)

    async def delete_category(self, session: AsyncSession, id: str) -> None:
        await self.repo.delete(session, id)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete category")

    async def list_categories(self, session: AsyncSession) -> list[CategoryReadDTO]:
        return await self.repo.list_read(session)

    async def get_category(self, session: AsyncSession, id: str) -> CategoryReadDTO | None:
        return await self.repo.get_read(session, id)

    async def get_category_by_slug(
        self, session: AsyncSession, slug: str
    ) -> CategoryReadDTO | None:
        return await self.repo.get_read_by_slug(session, slug)
