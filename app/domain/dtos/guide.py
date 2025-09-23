from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID

from app.core.validation import CommonValidators


class GuideCreateDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Guide title")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly slug")
    body: Dict[str, Any] = Field(..., description="Rich text content with blocks structure")
    estimated_read_time: int = Field(..., ge=1, le=300, description="Estimated read time in minutes")
    category_ids: Optional[List[UUID]] = Field(default=[], description="Category IDs to associate with this guide")
    
    @validator('title')
    def validate_title(cls, v):
        return CommonValidators.validate_non_empty_string(v)
    
    @validator('slug')
    def validate_slug(cls, v):
        return CommonValidators.validate_slug(v)
    
    @validator('body')
    def validate_body(cls, v):
        return CommonValidators.validate_rich_text_body(v)
    
    @validator('estimated_read_time')
    def validate_read_time(cls, v):
        return CommonValidators.validate_positive_int(v)
    
    @validator('category_ids')
    def validate_category_ids(cls, v):
        if v is None:
            return []
        if len(v) > 10:  # Reasonable limit
            raise ValueError("Cannot associate more than 10 categories with a guide")
        return v


class GuideUpdateDTO(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Guide title")
    slug: Optional[str] = Field(None, min_length=1, max_length=100, description="URL-friendly slug")
    body: Optional[Dict[str, Any]] = Field(None, description="Rich text content with blocks structure")
    estimated_read_time: Optional[int] = Field(None, ge=1, le=300, description="Estimated read time in minutes")
    category_ids: Optional[List[UUID]] = Field(None, description="Category IDs to associate with this guide")
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            return CommonValidators.validate_non_empty_string(v)
        return v
    
    @validator('slug')
    def validate_slug(cls, v):
        if v is not None:
            return CommonValidators.validate_slug(v)
        return v
    
    @validator('body')
    def validate_body(cls, v):
        if v is not None:
            return CommonValidators.validate_rich_text_body(v)
        return v
    
    @validator('estimated_read_time')
    def validate_read_time(cls, v):
        if v is not None:
            return CommonValidators.validate_positive_int(v)
        return v
    
    @validator('category_ids')
    def validate_category_ids(cls, v):
        if v is not None and len(v) > 10:
            raise ValueError("Cannot associate more than 10 categories with a guide")
        return v


class GuideReadDTO(BaseModel):
    id: UUID
    title: str
    slug: str
    body: Dict[str, Any]
    estimated_read_time: int
    created_at: datetime
    updated_at: Optional[datetime]
    category_ids: List[UUID] = Field(default=[], description="Associated category IDs")
    
    class Config:
        from_attributes = True
