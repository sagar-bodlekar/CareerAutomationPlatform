"""Resume schemas — CRUD and response."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ResumeCreate(BaseModel):
    """Request body to create a master resume from a profile."""

    user_id: UUID
    profile_id: UUID
    template_id: UUID | None = None
    title: str = "Master Resume"
    target_role: str | None = None
    target_job_id: UUID | None = None
    content: dict = Field(default_factory=dict)


class ResumeUpdate(BaseModel):
    """Request body to update resume metadata or content."""

    title: str | None = None
    content: dict | None = None
    target_role: str | None = None
    target_job_id: UUID | None = None
    template_id: UUID | None = None


class ResumeFileResponse(BaseModel):
    """PDF file metadata for a resume."""

    id: UUID
    resume_id: UUID
    filename: str
    file_size_bytes: int | None = None
    content_type: str = "application/pdf"
    minio_bucket: str
    minio_object_key: str
    page_count: int | None = None
    is_optimized: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeResponse(BaseModel):
    """Full resume response."""

    id: UUID
    user_id: UUID
    profile_id: UUID
    template_id: UUID | None = None
    title: str = "Master Resume"
    target_role: str | None = None
    target_job_id: UUID | None = None
    content: dict = Field(default_factory=dict)
    is_master: bool = True
    version: int = 1
    ats_score: float | None = None
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime | None = None
    files: list[ResumeFileResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ResumeSummary(BaseModel):
    """Lightweight resume summary for list views."""

    id: UUID
    user_id: UUID
    profile_id: UUID
    title: str = "Master Resume"
    target_role: str | None = None
    is_master: bool = True
    version: int = 1
    ats_score: float | None = None
    file_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
