from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy.dialects.postgresql import JSON
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from .utils.time import utcnow


class GuideCategoryLink(SQLModel, table=True):
    guide_id: UUID = Field(foreign_key="userguide.id", primary_key=True)
    category_id: UUID = Field(foreign_key="category.id", primary_key=True)


class GuideMediaLink(SQLModel, table=True):
    guide_id: UUID = Field(foreign_key="userguide.id", primary_key=True)
    media_id: UUID = Field(foreign_key="media.id", primary_key=True)


class Category(SQLModel, table=True):
    __tablename__ = "category"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    name: str = Field(nullable=False, index=True)
    description: Optional[str] = Field(default=None)
    slug: str = Field(unique=True, index=True, nullable=False)

    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None)

    # relationships
    guides: List["UserGuide"] = Relationship(
        back_populates="categories", link_model=GuideCategoryLink
    )


class Media(SQLModel, table=True):
    __tablename__ = "media"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    alt: Optional[str] = Field(default=None)
    url: str = Field(nullable=False)

    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None)

    guides: List["UserGuide"] = Relationship(
        back_populates="media", link_model=GuideMediaLink
    )


class UserGuide(SQLModel, table=True):
    __tablename__ = "userguide"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    title: str = Field(nullable=False)
    slug: str = Field(unique=True, index=True, nullable=False)

    # JSON body, not nullable
    body: dict = Field(sa_column=Column(JSON, nullable=False))

    estimated_read_time: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: Optional[datetime] = None

    # relationships
    categories: List[Category] = Relationship(
        back_populates="guides", link_model=GuideCategoryLink
    )
    media: List[Media] = Relationship(
        back_populates="guides", link_model=GuideMediaLink
    )


class Feedback(SQLModel, table=True):
    __tablename__ = "feedback"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    name: str = Field(nullable=False)
    email: str = Field(nullable=False)
    message: str = Field(nullable=False)
    expect_reply: bool = Field(default=False)

    created_at: datetime = Field(default_factory=utcnow, nullable=False)