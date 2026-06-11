"""Resume template schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ResumeTemplateCreate(BaseModel):
    """Request body to create a resume template."""

    name: str = Field(min_length=1, max_length=100)
    display_name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    html_content: str
    css_content: str | None = None
    thumbnail_url: str | None = None
    is_default: bool = False


class ResumeTemplateUpdate(BaseModel):
    """Request body to update a resume template."""

    name: str | None = None
    display_name: str | None = None
    description: str | None = None
    html_content: str | None = None
    css_content: str | None = None
    thumbnail_url: str | None = None
    is_active: bool | None = None
    is_default: bool | None = None


class ResumeTemplateResponse(BaseModel):
    """Resume template response."""

    id: UUID
    name: str
    display_name: str
    description: str | None = None
    html_content: str
    css_content: str | None = None
    thumbnail_url: str | None = None
    is_active: bool = True
    is_default: bool = False
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
