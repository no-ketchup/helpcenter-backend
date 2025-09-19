from __future__ import annotations
from datetime import datetime
import strawberry
from typing import List, Optional


@strawberry.type
class Category:
    id: str
    name: str
    description: Optional[str]
    slug: str
    createdAt: datetime
    updatedAt: Optional[datetime]

    # no infinite recursion – guides trimmed
    guides: List["UserGuide"]


@strawberry.type
class Media:
    id: str
    alt: Optional[str]
    url: str
    createdAt: datetime
    updatedAt: Optional[datetime]


@strawberry.type
class UserGuide:
    id: str
    title: str
    slug: str
    estimatedReadTime: int
    body: strawberry.scalars.JSON
    createdAt: datetime
    updatedAt: Optional[datetime]

    categories: List[Category]
    media: List[Media]


@strawberry.type
class Feedback:
    id: str
    name: str
    email: str
    message: str
    expectReply: bool
    createdAt: datetime