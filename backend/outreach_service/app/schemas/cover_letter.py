"""Cover letter schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CoverLetterRequest(BaseModel):
    """Request to generate a cover letter."""

    profile_id: int = Field(..., description="User profile ID")
    job_id: int = Field(..., description="Job ID")
    company_name: str = Field(..., min_length=1, max_length=255)
    job_title: str = Field(..., min_length=1, max_length=255)
    candidate_name: str = Field(..., min_length=1, max_length=255)
    current_role: Optional[str] = None
    skills: Optional[list[str]] = None
    achievements: Optional[list[str]] = None
    industry: Optional[str] = None
    company_description: Optional[str] = None
    job_description: Optional[str] = None
    required_skills: Optional[list[str]] = None
    tone: str = Field("professional", pattern="^(professional|enthusiastic|concise)$")
    use_ai: bool = True
    application_id: Optional[int] = None


class CoverLetterUpdate(BaseModel):
    """Update an existing cover letter."""

    body: Optional[str] = None
    tone: Optional[str] = Field(None, pattern="^(professional|enthusiastic|concise)$")
    status: Optional[str] = Field(None, pattern="^(draft|finalized|sent)$")


class CoverLetterResponse(BaseModel):
    """Generated cover letter response."""

    id: int
    content_type: str = "cover_letter"
    subject: Optional[str] = None
    body: str
    tone: str = "professional"
    profile_id: Optional[int] = None
    job_id: Optional[int] = None
    company_name: Optional[str] = None
    target_role: Optional[str] = None
    version: int = 1
    status: str = "draft"
    ai_agent_used: Optional[str] = None
    tokens_used: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
