from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import get_session_dependency
from app.core.rate_limiting import (
    rate_limit_dev_editor_read,
    rate_limit_dev_editor_write,
)
from app.domain.dtos.category import (
    CategoryCreateDTO,
    CategoryReadDTO,
    CategoryUpdateDTO,
)
from app.services.category import CategoryService

from .editor_guard import verify_dev_editor_key

router = APIRouter(
    prefix="/dev-editor",
    dependencies=[Depends(verify_dev_editor_key)],
    tags=["dev-editor"],
)

service = CategoryService()


@router.post("/categories", response_model=CategoryReadDTO)
@rate_limit_dev_editor_write()
async def create_category(
    request: Request,
    payload: CategoryCreateDTO,
    session: AsyncSession = Depends(get_session_dependency),
):
    return await service.create_category(session, payload)


@router.get("/categories", response_model=list[CategoryReadDTO])
@rate_limit_dev_editor_read()
async def list_categories(
    request: Request, session: AsyncSession = Depends(get_session_dependency)
):
    return await service.list_categories(session)


@router.get("/categories/{category_id}", response_model=CategoryReadDTO)
@rate_limit_dev_editor_read()
async def get_category(
    request: Request, category_id: str, session: AsyncSession = Depends(get_session_dependency)
):
    dto = await service.get_category(session, category_id)
    if not dto:
        raise HTTPException(404, "Category not found")
    return dto


@router.get("/categories/slug/{slug}", response_model=CategoryReadDTO)
@rate_limit_dev_editor_read()
async def get_category_by_slug(
    request: Request, slug: str, session: AsyncSession = Depends(get_session_dependency)
):
    dto = await service.get_category_by_slug(session, slug)
    if not dto:
        raise HTTPException(404, "Category not found")
    return dto


@router.put("/categories/{category_id}", response_model=CategoryReadDTO)
@rate_limit_dev_editor_write()
async def update_category(
    request: Request,
    category_id: str,
    payload: CategoryUpdateDTO,
    session: AsyncSession = Depends(get_session_dependency),
):
    return await service.update_category(session, category_id, payload)


@router.delete("/categories/{category_id}")
@rate_limit_dev_editor_write()
async def delete_category(
    request: Request, category_id: str, session: AsyncSession = Depends(get_session_dependency)
):
    await service.delete_category(session, category_id)
    return {"detail": "Category deleted"}
