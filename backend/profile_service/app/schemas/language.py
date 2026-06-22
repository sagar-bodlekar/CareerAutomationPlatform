"""Language proficiency schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LanguageCreate(BaseModel):
    """Schema for creating a language entry."""

    name: str
    proficiency: str = "intermediate"
    is_native: bool = False
    order: int = 0


class LanguageUpdate(BaseModel):
    """Schema for updating a language entry."""

    name: str | None = None
    proficiency: str | None = None
    is_native: bool | None = None
    order: int | None = None


class LanguageResponse(BaseModel):
    """Schema for language response."""

    id: UUID
    profile_id: UUID
    name: str
    proficiency: str = "intermediate"
    is_native: bool = False
    order: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
