"""Job filter parameters for search and list endpoints."""

from typing import Optional

from pydantic import BaseModel, Field


class JobFilterParams(BaseModel):
    """Query parameters for filtering job listings."""

    query: Optional[str] = Field(None, description="Full-text search query")
    title: Optional[str] = Field(None, description="Filter by job title")
    company_name: Optional[str] = Field(None, description="Filter by company name")
    skills: Optional[str] = Field(None, description="Comma-separated skill keywords to filter by")
    location: Optional[str] = Field(None, description="Filter by location")
    location_type: Optional[str] = Field(None, description="remote, onsite, hybrid")
    is_remote: Optional[bool] = Field(None, description="Filter remote jobs")
    experience_min: Optional[int] = Field(None, ge=0, description="Minimum years of experience")
    experience_max: Optional[int] = Field(None, ge=0, description="Maximum years of experience")
    experience_level: Optional[str] = Field(None, description="Entry, Mid, Senior, Lead")
    salary_min: Optional[float] = Field(None, ge=0, description="Minimum salary")
    salary_max: Optional[float] = Field(None, ge=0, description="Maximum salary")
    salary_currency: Optional[str] = Field(None, description="USD, EUR, etc.")
    employment_type: Optional[str] = Field(None, description="full_time, part_time, contract")
    industry: Optional[str] = Field(None, description="Filter by industry")
    remote_type: Optional[str] = Field(None, description="fully_remote, hybrid, onsite")
    status: Optional[str] = Field("active", description="Job status filter")
    sort_by: Optional[str] = Field("posted_at", description="Sort field")
    sort_order: Optional[str] = Field("desc", description="asc or desc")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class JobSearchResult(BaseModel):
    """Search result with relevance score."""

    id: int
    title: str
    company_name: str
    location: Optional[str] = None
    is_remote: bool = False
    required_skills: Optional[list[str]] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    employment_type: Optional[str] = None
    posted_at: Optional[str] = None
    match_score: Optional[float] = Field(None, ge=0, le=100, description="Relevance score 0-100")
