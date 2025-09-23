from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated, List

import strawberry

if TYPE_CHECKING:
    from .guide import UserGuide


@strawberry.type
class Media:
    id: str
    alt: str | None
    url: str
    createdAt: datetime
    updatedAt: datetime | None

    guides: List[Annotated["UserGuide", strawberry.lazy(".guide")]]
