"""Resume generation and optimization schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class ResumeGenerationRequest(BaseModel):
    """Request body to generate a role-specific resume PDF."""

    resume_id: UUID
    template_id: UUID | None = None
    target_role: str = Field(min_length=1, max_length=200)
    target_job_id: UUID | None = None
    optimize_ats: bool = False


class ResumeOptimizeRequest(BaseModel):
    """Request body to trigger ATS optimization."""

    job_description: str = Field(min_length=50)
    job_title: str | None = None
    company_name: str | None = None


class ATSOptimizeResponse(BaseModel):
    """Response body after ATS optimization."""

    resume_id: UUID
    ats_score: float
    score_breakdown: dict = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
    optimized_content: dict | None = None


class ATSScoreResponse(BaseModel):
    """ATS score response."""

    resume_id: UUID
    overall_score: float
    keyword_score: float
    format_score: float
    section_score: float
    experience_score: float
    recommendations: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
