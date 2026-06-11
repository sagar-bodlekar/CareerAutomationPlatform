"""API key management schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ApiKeyCreateRequest(BaseModel):
    """Request body to create a new API key."""

    name: str = Field(min_length=1, max_length=100)
    scopes: str | None = None
    expires_at: datetime | None = None


class ApiKeyCreateResponse(BaseModel):
    """Response body after creating an API key.

    The ``key`` value is only shown once at creation time.
    """

    id: UUID
    name: str
    key_prefix: str
    key: str  # Full key — only shown once
    scopes: str | None = None
    expires_at: datetime | None = None
    created_at: datetime


class ApiKeyResponse(BaseModel):
    """API key metadata (safe for listing)."""

    id: UUID
    name: str
    key_prefix: str
    scopes: str | None = None
    is_active: bool = True
    last_used_at: datetime | None = None
    expires_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
