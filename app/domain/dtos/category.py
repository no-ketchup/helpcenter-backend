from uuid import UUID

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class CategoryCreateDTO(BaseModel):
    name: str
    description: Optional[str] = None
    slug: str

class CategoryUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None

class CategoryReadDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str]
    slug: str
    created_at: datetime
    updated_at: Optional[datetime]