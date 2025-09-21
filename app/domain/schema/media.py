from __future__ import annotations
from datetime import datetime
import strawberry


@strawberry.type
class Media:
    id: str
    alt: str | None
    url: str
    createdAt: datetime
    updatedAt: datetime | None

    guides: list[strawberry.lazy_type("UserGuide", module="app.domain.schema.guide")]