"""Project schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Schema for creating a project entry."""

    name: str
    url: str | None = None
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    role: str | None = None
    start_date: date | None = None
    start_date_precision: str = "month"
    end_date: date | None = None
    end_date_precision: str = "month"
    is_current: bool = False
    highlights: list[str] = Field(default_factory=list)
    order: int = 0


class ProjectUpdate(BaseModel):
    """Schema for updating a project entry."""

    name: str | None = None
    url: str | None = None
    description: str | None = None
    technologies: list[str] | None = None
    role: str | None = None
    start_date: date | None = None
    start_date_precision: str | None = None
    end_date: date | None = None
    end_date_precision: str | None = None
    is_current: bool | None = None
    highlights: list[str] | None = None
    order: int | None = None


class ProjectResponse(BaseModel):
    """Schema for project response."""

    id: UUID
    profile_id: UUID
    name: str
    url: str | None = None
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    role: str | None = None
    start_date: date | None = None
    start_date_precision: str = "month"
    end_date: date | None = None
    end_date_precision: str = "month"
    is_current: bool = False
    highlights: list[str] = Field(default_factory=list)
    order: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
