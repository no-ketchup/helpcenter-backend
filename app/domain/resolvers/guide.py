from typing import List, Optional
import strawberry
from sqlmodel import select
from app.core.db import get_session_cm
from app.domain.models import UserGuide as GuideModel, Category as CategoryModel
from app.domain.schema import UserGuide as GuideType, Category as CategoryType


def to_guide(model: GuideModel, include_categories=True) -> GuideType:
    return GuideType(
        id=str(model.id),
        title=model.title,
        slug=model.slug,
        estimatedReadTime=model.estimated_read_time,
        body=model.body,
        createdAt=model.created_at,
        updatedAt=model.updated_at,
        categories=[CategoryType(
            id=str(c.id),
            name=c.name,
            description=c.description,
            slug=c.slug,
            createdAt=c.created_at,
            updatedAt=c.updated_at,
            guides=[]
        ) for c in model.categories] if include_categories else [],
        media=[],
    )


@strawberry.type
class GuideQuery:
    @strawberry.field
    async def guides(self, categorySlug: Optional[str] = None) -> List[GuideType]:
        async with get_session_cm() as session:
            query = select(GuideModel)
            if categorySlug:
                query = query.where(GuideModel.categories.any(CategoryModel.slug == categorySlug))
            rows = (await session.exec(query)).all()
            return [to_guide(r) for r in rows]

    @strawberry.field
    async def guide(self, slug: str) -> Optional[GuideType]:
        async with get_session_cm() as session:
            obj = (await session.exec(
                select(GuideModel).where(GuideModel.slug == slug)
            )).first()
            return to_guide(obj) if obj else None