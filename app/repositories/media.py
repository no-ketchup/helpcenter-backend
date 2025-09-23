from typing import List, Optional
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import delete as sa_delete

from app.repositories.base import BaseRepository
from app.domain.models import Media as MediaModel
from app.domain.dtos.media import MediaCreateDTO, MediaUpdateDTO, MediaReadDTO


class MediaRepository(BaseRepository[MediaModel]):
    def __init__(self):
        super().__init__(MediaModel)

    async def create_from_dto(self, session: AsyncSession, dto: MediaCreateDTO) -> MediaModel:
        """Create media from DTO."""
        media = MediaModel(url=dto.url, alt=dto.alt)
        session.add(media)
        return media

    async def update_from_dto(
        self, session: AsyncSession, id: UUID, dto: MediaUpdateDTO
    ) -> MediaModel:
        """Update media from DTO."""
        media = await session.get(MediaModel, id)
        if not media:
            return None

        if dto.url is not None:
            media.url = dto.url
        if dto.alt is not None:
            media.alt = dto.alt

        return media

    async def get_read(self, session: AsyncSession, id: UUID) -> Optional[MediaReadDTO]:
        """Get media as DTO."""
        media = await session.get(MediaModel, id)
        if not media:
            return None

        return MediaReadDTO(
            id=media.id,
            url=media.url,
            alt=media.alt,
            created_at=media.created_at,
            updated_at=media.updated_at,
        )

    async def list_read(self, session: AsyncSession) -> List[MediaReadDTO]:
        """List media as DTOs."""
        from sqlalchemy import select as sa_select

        stmt = sa_select(MediaModel)
        result = await session.execute(stmt)
        media_list = result.scalars().all()

        return [
            MediaReadDTO(
                id=media.id,
                url=media.url,
                alt=media.alt,
                created_at=media.created_at,
                updated_at=media.updated_at,
            )
            for media in media_list
        ]

    async def delete(self, session: AsyncSession, id: UUID) -> bool:
        """Delete media by ID and its relationships."""
        # Check if media exists
        obj = await session.get(MediaModel, id)
        if not obj:
            return False

        # Delete guide-media relationships
        from app.domain.models import GuideMediaLink

        stmt = sa_delete(GuideMediaLink).where(GuideMediaLink.media_id == id)
        await session.execute(stmt)

        # Delete the media directly with SQL
        stmt = sa_delete(MediaModel).where(MediaModel.id == id)
        result = await session.execute(stmt)

        return result.rowcount > 0
