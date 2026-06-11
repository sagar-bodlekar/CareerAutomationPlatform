"""Social link schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SocialLinkCreate(BaseModel):
    """Schema for creating a social link."""

    platform: str
    url: str
    label: str | None = None
    is_primary: bool = False
    order: int = 0


class SocialLinkUpdate(BaseModel):
    """Schema for updating a social link."""

    platform: str | None = None
    url: str | None = None
    label: str | None = None
    is_primary: bool | None = None
    order: int | None = None


class SocialLinkResponse(BaseModel):
    """Schema for social link response."""

    id: UUID
    profile_id: UUID
    platform: str
    url: str
    label: str | None = None
    is_primary: bool = False
    order: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
