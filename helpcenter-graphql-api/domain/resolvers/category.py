from datetime import datetime
from typing import List, Optional

import strawberry

from app.domain.schema import Category as CategoryType
from app.domain.schema import UserGuide as GuideType
from app.services.category import CategoryService
from app.services.guide import GuideService


def to_guide(
    id: str,
    title: str,
    slug: str,
    estimated_read_time: int,
    created_at: datetime,
    updated_at: Optional[datetime] = None,
) -> GuideType:
    return GuideType(
        id=id,
        title=title,
        slug=slug,
        estimatedReadTime=estimated_read_time,
        body={"blocks": []},  # Empty body for category listings
        createdAt=created_at,
        updatedAt=updated_at,
        categories=[],
        media=[],
    )


def to_category(
    id: str,
    name: str,
    description: str,
    slug: str,
    created_at: datetime,
    updated_at: Optional[datetime] = None,
    guides: List = None,
) -> CategoryType:
    return CategoryType(
        id=id,
        name=name,
        description=description,
        slug=slug,
        createdAt=created_at,
        updatedAt=updated_at,
        guides=guides or [],
    )


@strawberry.type
class CategoryQuery:
    @strawberry.field
    async def categories(self, info) -> List[CategoryType]:
        get_session = info.context["get_session"]
        async with get_session() as session:
            category_service = CategoryService()
            guide_service = GuideService()

            # Get all categories from database
            categories_dto = await category_service.list_categories(session)

            # Convert to GraphQL types and include guides
            result = []
            for category_dto in categories_dto:
                # Get guides for this category
                guides_dto = await guide_service.list_guides_by_category(session, category_dto.id)

                # Convert guides to GraphQL types
                guides = []
                for guide_dto in guides_dto:
                    guides.append(
                        GuideType(
                            id=guide_dto.id,
                            title=guide_dto.title,
                            slug=guide_dto.slug,
                            estimatedReadTime=guide_dto.estimated_read_time,
                            body=guide_dto.body,
                            createdAt=guide_dto.created_at,
                            updatedAt=guide_dto.updated_at,
                            categories=[],  # Avoid circular reference
                            media=[],
                        )
                    )

                # Convert category to GraphQL type
                result.append(
                    CategoryType(
                        id=category_dto.id,
                        name=category_dto.name,
                        description=category_dto.description,
                        slug=category_dto.slug,
                        createdAt=category_dto.created_at,
                        updatedAt=category_dto.updated_at,
                        guides=guides,
                    )
                )

            return result

    @strawberry.field
    async def category(self, info, slug: str) -> Optional[CategoryType]:
        get_session = info.context["get_session"]
        async with get_session() as session:
            category_service = CategoryService()
            guide_service = GuideService()

            # Get category by slug from database
            category_dto = await category_service.get_category_by_slug(session, slug)
            if not category_dto:
                return None

            # Get guides for this category
            guides_dto = await guide_service.list_guides_by_category(session, category_dto.id)

            # Convert guides to GraphQL types
            guides = []
            for guide_dto in guides_dto:
                guides.append(
                    GuideType(
                        id=guide_dto.id,
                        title=guide_dto.title,
                        slug=guide_dto.slug,
                        estimatedReadTime=guide_dto.estimated_read_time,
                        body=guide_dto.body,
                        createdAt=guide_dto.created_at,
                        updatedAt=guide_dto.updated_at,
                        categories=[],  # Avoid circular reference
                        media=[],
                    )
                )

            # Convert category to GraphQL type
            return CategoryType(
                id=category_dto.id,
                name=category_dto.name,
                description=category_dto.description,
                slug=category_dto.slug,
                createdAt=category_dto.created_at,
                updatedAt=category_dto.updated_at,
                guides=guides,
            )
