"""Match schemas for scoring requests and responses."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class MatchScoreRequest(BaseModel):
    """Request to score a profile against a job."""

    profile_id: int = Field(..., description="User profile ID")
    job_id: int = Field(..., description="Job ID from Job Service")
    profile_data: Optional[dict[str, Any]] = Field(None, description="Profile data (skills, experience, etc.)")
    job_data: Optional[dict[str, Any]] = Field(None, description="Job data (requirements, description, etc.)")
    use_ai_enhancement: bool = Field(False, description="Whether to use AI for enhanced scoring")


class MatchScoreResponse(BaseModel):
    """Response from a match score computation."""

    match_id: Optional[int] = None
    profile_id: int
    job_id: int
    overall_score: float
    skills_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None
    location_score: Optional[float] = None
    title_score: Optional[float] = None
    matched_skills: Optional[list[str]] = None
    missing_skills: Optional[list[str]] = None
    extra_skills: Optional[list[str]] = None
    match_summary: Optional[str] = None
    ai_enhanced: bool = False
    ai_recommendation: Optional[str] = None
    rank: Optional[int] = None

    model_config = {"from_attributes": True}


class MatchDetailResponse(BaseModel):
    """Detailed match with all fields."""

    id: int
    profile_id: int
    job_id: int
    overall_score: float
    skills_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None
    location_score: Optional[float] = None
    title_score: Optional[float] = None
    matched_skills: Optional[list[str]] = None
    missing_skills: Optional[list[str]] = None
    extra_skills: Optional[list[str]] = None
    skill_gaps: Optional[dict] = None
    match_summary: Optional[str] = None
    ai_enhanced: bool = False
    ai_recommendation: Optional[str] = None
    rank: Optional[int] = None
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SkillGapResponse(BaseModel):
    """Skill gap analysis between profile and job."""

    profile_id: int
    job_id: int
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    extra_skills: list[str] = Field(default_factory=list)
    match_percentage: float = Field(..., ge=0, le=100)
    critical_gaps: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class BatchMatchRequest(BaseModel):
    """Request to batch match profiles against a job (or vice versa)."""

    job_id: Optional[int] = Field(None, description="Job ID (if matching all profiles to one job)")
    profile_id: Optional[int] = Field(None, description="Profile ID (if matching one profile to all jobs)")
    limit: int = Field(20, ge=1, le=100, description="Maximum matches to return")
    use_ai_enhancement: bool = False


class BatchMatchResponse(BaseModel):
    """Response from a batch match operation."""

    matches: list[MatchScoreResponse] = Field(default_factory=list)
    total_matched: int = 0
    total_processed: int = 0
    ai_enhanced: bool = False
