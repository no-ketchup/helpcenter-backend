from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import DateTime
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
from app.utils.time import utcnow


class GuideMediaLink(SQLModel, table=True):
    guide_id: UUID = Field(foreign_key="userguide.id", primary_key=True)
    media_id: UUID = Field(foreign_key="media.id", primary_key=True)


class Media(SQLModel, table=True):
    __tablename__ = "media"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    alt: Optional[str] = Field(default=None)
    url: str = Field(nullable=False)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=utcnow, nullable=False)
    )
    updated_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True)))

    guides: List["UserGuide"] = Relationship(back_populates="media", link_model=GuideMediaLink)
