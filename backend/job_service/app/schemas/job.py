"""Job schemas for request/response."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    """Create a new job posting."""

    external_id: Optional[str] = None
    source_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=255)
    company_name: str = Field(..., min_length=1, max_length=255)
    company_description: Optional[str] = None
    company_url: Optional[str] = None
    company_logo: Optional[str] = None
    location: Optional[str] = None
    location_type: Optional[str] = None
    is_remote: bool = False
    remote_type: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    required_skills: Optional[list[str]] = None
    nice_to_have_skills: Optional[list[str]] = None
    experience_min_years: Optional[int] = None
    experience_max_years: Optional[int] = None
    experience_level: Optional[str] = None
    education_required: Optional[str] = None
    degree_preferred: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = "USD"
    salary_period: Optional[str] = None
    salary_visible: bool = False
    employment_type: Optional[str] = None
    industry: Optional[str] = None
    function: Optional[str] = None
    department: Optional[str] = None
    job_url: Optional[str] = None
    apply_url: Optional[str] = None
    application_deadline: Optional[datetime] = None
    posted_at: Optional[datetime] = None
    status: str = "active"
    raw_data: Optional[dict] = None
    normalized_title: Optional[str] = None
    company_id_normalized: Optional[str] = None


class JobUpdate(BaseModel):
    """Update an existing job posting."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    company_description: Optional[str] = None
    company_url: Optional[str] = None
    company_logo: Optional[str] = None
    location: Optional[str] = None
    location_type: Optional[str] = None
    is_remote: Optional[bool] = None
    remote_type: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    required_skills: Optional[list[str]] = None
    nice_to_have_skills: Optional[list[str]] = None
    experience_min_years: Optional[int] = None
    experience_max_years: Optional[int] = None
    experience_level: Optional[str] = None
    education_required: Optional[str] = None
    degree_preferred: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    salary_visible: Optional[bool] = None
    employment_type: Optional[str] = None
    industry: Optional[str] = None
    function: Optional[str] = None
    department: Optional[str] = None
    job_url: Optional[str] = None
    apply_url: Optional[str] = None
    application_deadline: Optional[datetime] = None
    posted_at: Optional[datetime] = None
    status: Optional[str] = None
    normalized_title: Optional[str] = None
    company_id_normalized: Optional[str] = None


class JobResponse(BaseModel):
    """Full job response."""

    id: int
    external_id: Optional[str] = None
    source_id: Optional[int] = None
    title: str
    company_name: str
    company_description: Optional[str] = None
    company_url: Optional[str] = None
    company_logo: Optional[str] = None
    location: Optional[str] = None
    location_type: Optional[str] = None
    is_remote: bool = False
    remote_type: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    required_skills: Optional[list[str]] = None
    nice_to_have_skills: Optional[list[str]] = None
    experience_min_years: Optional[int] = None
    experience_max_years: Optional[int] = None
    experience_level: Optional[str] = None
    education_required: Optional[str] = None
    degree_preferred: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    salary_visible: bool = False
    employment_type: Optional[str] = None
    industry: Optional[str] = None
    function: Optional[str] = None
    department: Optional[str] = None
    job_url: Optional[str] = None
    apply_url: Optional[str] = None
    application_deadline: Optional[datetime] = None
    posted_at: Optional[datetime] = None
    scraped_at: Optional[datetime] = None
    status: str = "active"
    normalized_title: Optional[str] = None
    company_id_normalized: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
