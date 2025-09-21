from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import get_session
from app.domain.dtos.category import (
    CategoryCreateDTO,
    CategoryUpdateDTO,
    CategoryReadDTO,
)
from app.core.editor_guard import verify_dev_editor_key
from app.services.category import CategoryService

router = APIRouter(
    prefix="/dev-editor",
    dependencies=[Depends(verify_dev_editor_key)],
    tags=["dev-editor"],
)

service = CategoryService()


@router.post("/categories", response_model=CategoryReadDTO)
async def create_category(
    payload: CategoryCreateDTO, session: AsyncSession = Depends(get_session)
):
    return await service.create_category(session, payload)


@router.get("/categories", response_model=list[CategoryReadDTO])
async def list_categories(session: AsyncSession = Depends(get_session)):
    return await service.list_categories(session)


@router.get("/categories/{category_id}", response_model=CategoryReadDTO)
async def get_category(category_id: str, session: AsyncSession = Depends(get_session)):
    dto = await service.get_category(session, category_id)
    if not dto:
        raise HTTPException(404, "Category not found")
    return dto


@router.get("/categories/slug/{slug}", response_model=CategoryReadDTO)
async def get_category_by_slug(slug: str, session: AsyncSession = Depends(get_session)):
    dto = await service.get_category_by_slug(session, slug)
    if not dto:
        raise HTTPException(404, "Category not found")
    return dto


@router.put("/categories/{category_id}", response_model=CategoryReadDTO)
async def update_category(
    category_id: str,
    payload: CategoryUpdateDTO,
    session: AsyncSession = Depends(get_session),
):
    return await service.update_category(session, category_id, payload)


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str, session: AsyncSession = Depends(get_session)
):
    await service.delete_category(session, category_id)
    return {"detail": "Category deleted"}