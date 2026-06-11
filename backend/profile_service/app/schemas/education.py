"""Education schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EducationCreate(BaseModel):
    """Schema for creating an education entry."""

    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    grade: str | None = None
    start_date: date
    start_date_precision: str = "year"
    end_date: date | None = None
    end_date_precision: str = "year"
    is_current: bool = False
    description: str | None = None
    activities: list[str] = Field(default_factory=list)
    order: int = 0


class EducationUpdate(BaseModel):
    """Schema for updating an education entry."""

    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    grade: str | None = None
    start_date: date | None = None
    start_date_precision: str | None = None
    end_date: date | None = None
    end_date_precision: str | None = None
    is_current: bool | None = None
    description: str | None = None
    activities: list[str] | None = None
    order: int | None = None


class EducationResponse(BaseModel):
    """Schema for education response."""

    id: UUID
    profile_id: UUID
    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    grade: str | None = None
    start_date: date
    start_date_precision: str = "year"
    end_date: date | None = None
    end_date_precision: str = "year"
    is_current: bool = False
    description: str | None = None
    activities: list[str] = Field(default_factory=list)
    order: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
