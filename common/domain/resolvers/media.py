from typing import List

import strawberry

from ...services.media import MediaService
from ..schema import Media as MediaType
from ..schema import UserGuide as GuideType


@strawberry.type
class MediaQuery:
    @strawberry.field
    async def media(self, info) -> List[MediaType]:
        get_session = info.context["get_session"]
        async with get_session() as session:
            media_service = MediaService()

            # Get media from database
            media_dto = await media_service.list_media(session)

            # Convert to GraphQL types
            result = []
            for media in media_dto:
                # Get guides associated with this media
                guides_dto = await media_service.get_media_guides(session, media.id)

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
                            media=[],  # Avoid circular reference
                        )
                    )

                result.append(
                    MediaType(
                        id=media.id,
                        url=media.url,
                        alt=media.alt,
                        createdAt=media.created_at,
                        updatedAt=media.updated_at,
                        guides=guides,
                    )
                )

            return result
