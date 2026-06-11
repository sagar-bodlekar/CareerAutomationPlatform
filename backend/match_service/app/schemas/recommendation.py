"""Recommendation response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JobBasicInfo(BaseModel):
    """Basic job info for recommendation display."""

    id: int
    title: str
    company_name: str
    location: Optional[str] = None
    is_remote: bool = False
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    employment_type: Optional[str] = None
    posted_at: Optional[datetime] = None


class RecommendationResponse(BaseModel):
    """A single match recommendation with job info."""

    match_id: int
    job: JobBasicInfo
    overall_score: float
    skills_score: Optional[float] = None
    experience_score: Optional[float] = None
    matched_skills: Optional[list[str]] = None
    missing_skills: Optional[list[str]] = None
    match_summary: Optional[str] = None
    ai_recommendation: Optional[str] = None
    rank: Optional[int] = None
    status: str = "active"


class MatchListResponse(BaseModel):
    """Paginated list of match recommendations."""

    recommendations: list[RecommendationResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20
