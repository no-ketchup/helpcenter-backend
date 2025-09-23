from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class MediaCreateDTO(BaseModel):
    url: str = Field(..., description="Media URL")
    alt: Optional[str] = Field(None, description="Alt text for accessibility")


class MediaUpdateDTO(BaseModel):
    url: Optional[str] = Field(None, description="Media URL")
    alt: Optional[str] = Field(None, description="Alt text for accessibility")


class MediaReadDTO(BaseModel):
    id: UUID
    url: str
    alt: Optional[str]
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True
