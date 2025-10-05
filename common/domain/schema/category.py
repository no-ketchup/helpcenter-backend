from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated, List, Optional

import strawberry

if TYPE_CHECKING:
    from .guide import UserGuide


@strawberry.type
class Category:
    id: str
    name: str
    description: Optional[str]
    slug: str
    createdAt: datetime
    updatedAt: Optional[datetime]

    guides: List[Annotated["UserGuide", strawberry.lazy(".guide")]]
