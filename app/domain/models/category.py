from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import DateTime
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
from app.utils.time import utcnow


class GuideCategoryLink(SQLModel, table=True):
    guide_id: UUID = Field(foreign_key="userguide.id", primary_key=True)
    category_id: UUID = Field(foreign_key="category.id", primary_key=True)


class Category(SQLModel, table=True):
    __tablename__ = "category"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    name: str = Field(nullable=False, index=True)
    description: Optional[str] = Field(default=None)
    slug: str = Field(unique=True, index=True, nullable=False)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=utcnow, nullable=False)
    )
    updated_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True)))

    guides: List["UserGuide"] = Relationship(
        back_populates="categories", link_model=GuideCategoryLink
    )
