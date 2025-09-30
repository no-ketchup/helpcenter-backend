from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated, List

import strawberry

if TYPE_CHECKING:
    from .category import Category
    from .media import Media


@strawberry.type
class UserGuide:
    id: str
    title: str
    slug: str
    estimatedReadTime: int
    body: strawberry.scalars.JSON
    createdAt: datetime
    updatedAt: datetime | None

    categories: List[Annotated["Category", strawberry.lazy(".category")]]
    media: list[Annotated["Media", strawberry.lazy(".media")]]
