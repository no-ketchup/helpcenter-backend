from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSON
from sqlmodel import Column, Field, Relationship, SQLModel

from ...utils.time import utcnow
from .category import GuideCategoryLink
from .media import GuideMediaLink


class UserGuide(SQLModel, table=True):
    __tablename__ = "userguide"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    title: str = Field(nullable=False)
    slug: str = Field(unique=True, index=True, nullable=False)

    body: dict = Field(sa_column=Column(JSON, nullable=False))
    estimated_read_time: int = Field(nullable=False)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=utcnow, nullable=False)
    )
    updated_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True)))

    categories: List["Category"] = Relationship(
        back_populates="guides", link_model=GuideCategoryLink
    )
    media: List["Media"] = Relationship(back_populates="guides", link_model=GuideMediaLink)
