"""Certification schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CertificationCreate(BaseModel):
    """Schema for creating a certification entry."""

    name: str
    issuer: str | None = None
    url: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    does_not_expire: bool = False
    credential_id: str | None = None
    description: str | None = None
    order: int = 0


class CertificationUpdate(BaseModel):
    """Schema for updating a certification entry."""

    name: str | None = None
    issuer: str | None = None
    url: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    does_not_expire: bool | None = None
    credential_id: str | None = None
    description: str | None = None
    order: int | None = None


class CertificationResponse(BaseModel):
    """Schema for certification response."""

    id: UUID
    profile_id: UUID
    name: str
    issuer: str | None = None
    url: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    does_not_expire: bool = False
    credential_id: str | None = None
    description: str | None = None
    order: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
