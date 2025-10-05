from typing import List, Optional

import strawberry

from ...services.category import CategoryService
from ...services.guide import GuideService
from ...services.media import MediaService
from ..schema import Category as CategoryType
from ..schema import Media as MediaType
from ..schema import UserGuide as GuideType


@strawberry.type
class GuideQuery:
    @strawberry.field
    async def guides(self, info, categorySlug: Optional[str] = None) -> List[GuideType]:
        get_session = info.context["get_session"]
        async with get_session() as session:
            guide_service = GuideService()
            category_service = CategoryService()

            # Get guides from database
            if categorySlug:
                # Get guides for specific category
                category_dto = await category_service.get_category_by_slug(session, categorySlug)
                if not category_dto:
                    return []
                guides_dto = await guide_service.list_guides_by_category(session, category_dto.id)
            else:
                # Get all guides
                guides_dto = await guide_service.list_guides(session)

            # Convert to GraphQL types
            result = []
            for guide_dto in guides_dto:
                # Get categories for this guide
                categories_dto = await guide_service.get_guide_categories(session, guide_dto.id)

                # Convert categories to GraphQL types
                categories = []
                for category_dto in categories_dto:
                    categories.append(
                        CategoryType(
                            id=category_dto.id,
                            name=category_dto.name,
                            description=category_dto.description,
                            slug=category_dto.slug,
                            createdAt=category_dto.created_at,
                            updatedAt=category_dto.updated_at,
                            guides=[],  # Avoid circular reference
                        )
                    )

                # Get media for this guide
                media_service = MediaService()
                media_dto = await media_service.get_guide_media(session, guide_dto.id)

                # Convert media to GraphQL types
                media = []
                for media_item in media_dto:
                    media.append(
                        MediaType(
                            id=media_item.id,
                            url=media_item.url,
                            alt=media_item.alt,
                            createdAt=media_item.created_at,
                            updatedAt=media_item.updated_at,
                            guides=[],  # Avoid circular reference
                        )
                    )

                # Convert guide to GraphQL type
                result.append(
                    GuideType(
                        id=guide_dto.id,
                        title=guide_dto.title,
                        slug=guide_dto.slug,
                        estimatedReadTime=guide_dto.estimated_read_time,
                        body=guide_dto.body,
                        createdAt=guide_dto.created_at,
                        updatedAt=guide_dto.updated_at,
                        categories=categories,
                        media=media,
                    )
                )

            return result

    @strawberry.field
    async def guide(self, info, slug: str) -> Optional[GuideType]:
        get_session = info.context["get_session"]
        async with get_session() as session:
            guide_service = GuideService()

            # Get guide by slug from database
            guide_dto = await guide_service.get_guide_by_slug(session, slug)
            if not guide_dto:
                return None

            # Get categories for this guide
            categories_dto = await guide_service.get_guide_categories(session, guide_dto.id)

            # Convert categories to GraphQL types
            categories = []
            for category_dto in categories_dto:
                categories.append(
                    CategoryType(
                        id=category_dto.id,
                        name=category_dto.name,
                        description=category_dto.description,
                        slug=category_dto.slug,
                        createdAt=category_dto.created_at,
                        updatedAt=category_dto.updated_at,
                        guides=[],  # Avoid circular reference
                    )
                )

            # Get media for this guide
            media_service = MediaService()
            media_dto = await media_service.get_guide_media(session, guide_dto.id)

            # Convert media to GraphQL types
            media = []
            for media_item in media_dto:
                media.append(
                    MediaType(
                        id=media_item.id,
                        url=media_item.url,
                        alt=media_item.alt,
                        createdAt=media_item.created_at,
                        updatedAt=media_item.updated_at,
                        guides=[],  # Avoid circular reference
                    )
                )

            # Convert guide to GraphQL type
            return GuideType(
                id=guide_dto.id,
                title=guide_dto.title,
                slug=guide_dto.slug,
                estimatedReadTime=guide_dto.estimated_read_time,
                body=guide_dto.body,
                createdAt=guide_dto.created_at,
                updatedAt=guide_dto.updated_at,
                categories=categories,
                media=media,
            )
