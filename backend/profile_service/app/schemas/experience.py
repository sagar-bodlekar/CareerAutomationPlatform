"""Work experience schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WorkExperienceCreate(BaseModel):
    """Schema for creating a work experience entry."""

    company_name: str
    company_url: str | None = None
    company_logo_url: str | None = None
    job_title: str
    employment_type: str = "full_time"
    location: str | None = None
    location_type: str | None = None
    start_date: date
    start_date_precision: str = "month"
    end_date: date | None = None
    end_date_precision: str = "month"
    is_current: bool = False
    description: str | None = None
    achievements: list[str] = Field(default_factory=list)
    skills_used: list[str] = Field(default_factory=list)
    order: int = 0


class WorkExperienceUpdate(BaseModel):
    """Schema for updating a work experience entry."""

    company_name: str | None = None
    company_url: str | None = None
    company_logo_url: str | None = None
    job_title: str | None = None
    employment_type: str | None = None
    location: str | None = None
    location_type: str | None = None
    start_date: date | None = None
    start_date_precision: str | None = None
    end_date: date | None = None
    end_date_precision: str | None = None
    is_current: bool | None = None
    description: str | None = None
    achievements: list[str] | None = None
    skills_used: list[str] | None = None
    order: int | None = None


class WorkExperienceResponse(BaseModel):
    """Schema for work experience response."""

    id: UUID
    profile_id: UUID
    company_name: str
    company_url: str | None = None
    company_logo_url: str | None = None
    job_title: str
    employment_type: str = "full_time"
    location: str | None = None
    location_type: str | None = None
    start_date: date
    start_date_precision: str = "month"
    end_date: date | None = None
    end_date_precision: str = "month"
    is_current: bool = False
    description: str | None = None
    achievements: list[str] = Field(default_factory=list)
    skills_used: list[str] = Field(default_factory=list)
    order: int = 0
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
