from typing import List, Optional
import strawberry
from sqlmodel import select
from app.core.db import get_session_cm
from app.domain.models import Category as CategoryModel
from app.domain.schema import Category as CategoryType


def to_category(model: CategoryModel) -> CategoryType:
    return CategoryType(
        id=str(model.id),
        name=model.name,
        description=model.description,
        slug=model.slug,
        createdAt=model.created_at,
        updatedAt=model.updated_at,
        guides=[],
    )


@strawberry.type
class CategoryQuery:
    @strawberry.field
    async def categories(self) -> List[CategoryType]:
        async with get_session_cm() as session:
            rows = (await session.exec(select(CategoryModel))).all()
            return [to_category(r) for r in rows]

    @strawberry.field
    async def category(self, slug: str) -> Optional[CategoryType]:
        async with get_session_cm() as session:
            obj = (await session.exec(
                select(CategoryModel).where(CategoryModel.slug == slug)
            )).first()
            return to_category(obj) if obj else None