from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ...core.validation import CommonValidators


class CategoryCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly slug")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return CommonValidators.validate_non_empty_string(v)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        return CommonValidators.validate_slug(v)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v is not None:
            return CommonValidators.validate_non_empty_string(v)
        return v


class CategoryUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    slug: Optional[str] = Field(None, min_length=1, max_length=100, description="URL-friendly slug")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            return CommonValidators.validate_non_empty_string(v)
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        if v is not None:
            return CommonValidators.validate_slug(v)
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v is not None:
            return CommonValidators.validate_non_empty_string(v)
        return v


class CategoryReadDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str]
    slug: str
    created_at: datetime
    updated_at: Optional[datetime]
