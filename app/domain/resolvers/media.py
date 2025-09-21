from typing import List
import strawberry
from sqlmodel import select
from app.core.db import get_session_cm
from app.domain.models import Media as MediaModel
from app.domain.schema import Media as MediaType


def to_media(model: MediaModel) -> MediaType:
    return MediaType(
        id=str(model.id),
        alt=model.alt,
        url=model.url,
        createdAt=model.created_at,
        updatedAt=model.updated_at,
    )


@strawberry.type
class MediaQuery:
    @strawberry.field
    async def media(self) -> List[MediaType]:
        async with get_session_cm() as session:
            rows = (await session.exec(select(MediaModel))).all()
            return [to_media(r) for r in rows]