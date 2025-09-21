from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.db import get_session
from app.domain.models import Category
from app.mappers.category import CategoryMapper

router = APIRouter(prefix="/dev-editor", tags=["dev-editor"])
category_mapper = CategoryMapper()

@router.post("/categories", response_model=Category)
async def create_category(category: Category, session: AsyncSession = Depends(get_session)):
    return await category_mapper.create(session, category)

@router.get("/categories", response_model=list[Category])
async def list_categories(session: AsyncSession = Depends(get_session)):
    return await category_mapper.list(session)

@router.get("/categories/{category_id}", response_model=Category)
async def get_category(category_id: str, session: AsyncSession = Depends(get_session)):
    category = await category_mapper.get(session, category_id)
    if not category:
        raise HTTPException(404, "Category not found")
    return category