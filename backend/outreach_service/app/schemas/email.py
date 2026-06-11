"""Email generation schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EmailRequest(BaseModel):
    """Request to generate an outreach email."""

    profile_id: int = Field(..., description="User profile ID")
    job_id: int = Field(..., description="Job ID")
    company_name: str = Field(..., min_length=1, max_length=255)
    job_title: str = Field(..., min_length=1, max_length=255)
    candidate_name: str = Field(..., min_length=1, max_length=255)
    current_role: Optional[str] = None
    recipient_name: Optional[str] = Field(None, description="Hiring manager or recruiter name")
    recipient_role: Optional[str] = None
    linkedin_url: Optional[str] = None
    mutual_connections: Optional[str] = None
    outreach_reason: Optional[str] = None
    tone: str = Field("professional", pattern="^(professional|enthusiastic|concise)$")
    use_ai: bool = True
    application_id: Optional[int] = None


class EmailUpdate(BaseModel):
    """Update an existing email."""

    subject: Optional[str] = None
    body: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|finalized|sent)$")


class EmailResponse(BaseModel):
    """Generated email response."""

    id: int
    content_type: str = "email"
    subject: Optional[str] = None
    body: str
    tone: str = "professional"
    profile_id: Optional[int] = None
    job_id: Optional[int] = None
    company_name: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_role: Optional[str] = None
    version: int = 1
    status: str = "draft"
    ai_agent_used: Optional[str] = None
    tokens_used: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
