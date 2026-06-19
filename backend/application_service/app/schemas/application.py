"""Application schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    """Create a new application draft."""

    profile_id: str
    job_id: int
    user_id: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    job_location: Optional[str] = None
    job_url: Optional[str] = None
    match_score: Optional[float] = None
    match_id: Optional[int] = None
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    """Update application fields."""

    status: Optional[str] = None
    notes: Optional[str] = None
    resume_id: Optional[int] = None
    cover_letter_id: Optional[int] = None
    email_id: Optional[int] = None


class ApplicationResponse(BaseModel):
    """Full application response."""

    id: int
    profile_id: str
    job_id: int
    user_id: Optional[str] = None
    status: str = "draft"
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    job_location: Optional[str] = None
    match_score: Optional[float] = None
    resume_id: Optional[int] = None
    cover_letter_id: Optional[int] = None
    email_id: Optional[int] = None
    delivery_status: Optional[str] = None
    sent_at: Optional[datetime] = None
    retry_count: int = 0
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    allowed_transitions: list[str] = Field(default_factory=list)
    progress_percentage: int = 0

    model_config = {"from_attributes": True}


class ApplicationListResponse(BaseModel):
    """Paginated application list."""

    applications: list[ApplicationResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20
