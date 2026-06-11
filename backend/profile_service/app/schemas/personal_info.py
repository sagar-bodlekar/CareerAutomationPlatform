"""Personal info schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class PersonalInfoCreate(BaseModel):
    """Schema for creating personal info."""

    full_name: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    date_of_birth: date | None = None
    nationality: str | None = None
    pronouns: str | None = None
    avatar_url: str | None = None


class PersonalInfoUpdate(BaseModel):
    """Schema for updating personal info."""

    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    date_of_birth: date | None = None
    nationality: str | None = None
    pronouns: str | None = None
    avatar_url: str | None = None


class PersonalInfoResponse(BaseModel):
    """Schema for personal info response."""

    id: UUID
    profile_id: UUID
    full_name: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    date_of_birth: date | None = None
    nationality: str | None = None
    pronouns: str | None = None
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
