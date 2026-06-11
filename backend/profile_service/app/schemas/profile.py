"""Profile schemas — root profile entity."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.certification import CertificationResponse
from app.schemas.education import EducationResponse
from app.schemas.experience import WorkExperienceResponse
from app.schemas.personal_info import PersonalInfoCreate, PersonalInfoResponse, PersonalInfoUpdate
from app.schemas.project import ProjectResponse
from app.schemas.skill import SkillCreate, SkillResponse, SkillUpdate
from app.schemas.social_link import SocialLinkCreate, SocialLinkResponse


class ProfileCreate(BaseModel):
    """Fields that can be set directly on the root profile."""

    headline: str | None = None
    summary: str | None = None
    location_city: str | None = None
    location_state: str | None = None
    location_country: str | None = None
    location_type: str | None = "remote"
    preferred_roles: list[str] = Field(default_factory=list)
    target_salary_min: int | None = None
    target_salary_max: int | None = None
    target_salary_currency: str = "USD"
    open_to_work: bool = True
    open_to_relocation: bool = False
    years_of_experience: float | None = 0.0

    # Nested data
    personal_info: PersonalInfoCreate | None = None
    skills: list[SkillCreate] = Field(default_factory=list)
    social_links: list[SocialLinkCreate] = Field(default_factory=list)


class ProfileCreateRequest(BaseModel):
    """Request body for creating a full profile with nested data."""

    user_id: UUID
    profile: ProfileCreate


class ProfileUpdate(BaseModel):
    """Fields that can be updated on the root profile."""

    headline: str | None = None
    summary: str | None = None
    location_city: str | None = None
    location_state: str | None = None
    location_country: str | None = None
    location_type: str | None = None
    preferred_roles: list[str] | None = None
    target_salary_min: int | None = None
    target_salary_max: int | None = None
    target_salary_currency: str | None = None
    open_to_work: bool | None = None
    open_to_relocation: bool | None = None
    years_of_experience: float | None = None

    # Nested updates
    personal_info: PersonalInfoUpdate | None = None
    skills: list[SkillUpdate] | None = None


class ProfileResponse(BaseModel):
    """Full profile response with all nested data."""

    id: UUID
    user_id: UUID
    headline: str | None = None
    summary: str | None = None
    location_city: str | None = None
    location_state: str | None = None
    location_country: str | None = None
    location_type: str | None = None
    preferred_roles: list[str] = Field(default_factory=list)
    target_salary_min: int | None = None
    target_salary_max: int | None = None
    target_salary_currency: str = "USD"
    open_to_work: bool = True
    open_to_relocation: bool = False
    years_of_experience: float = 0.0
    created_at: datetime
    updated_at: datetime | None = None

    # Nested data
    personal_info: PersonalInfoResponse | None = None
    skills: list[SkillResponse] = Field(default_factory=list)
    work_experiences: list[WorkExperienceResponse] = Field(default_factory=list)
    education: list[EducationResponse] = Field(default_factory=list)
    projects: list[ProjectResponse] = Field(default_factory=list)
    certifications: list[CertificationResponse] = Field(default_factory=list)
    social_links: list[SocialLinkResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ProfileSummary(BaseModel):
    """Lightweight profile response for list views."""

    id: UUID
    user_id: UUID
    headline: str | None = None
    location_city: str | None = None
    location_country: str | None = None
    location_type: str | None = None
    open_to_work: bool = True
    years_of_experience: float = 0.0
    skill_count: int = 0
    total_experiences: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileListResponse(BaseModel):
    """Paginated list of profile summaries."""

    items: list[ProfileSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProfileImportRequest(BaseModel):
    """JSON payload for importing a full profile."""

    profile: ProfileCreate | None = None
    work_experiences: list | None = None
    education: list | None = None
    projects: list | None = None
    certifications: list | None = None

    class Config:
        extra = "allow"


class ProfileAnalyticsResponse(BaseModel):
    """Profile analytics summary."""

    profile_id: UUID
    total_skills: int = 0
    top_skills: list[str] = Field(default_factory=list)
    total_experiences: int = 0
    total_education: int = 0
    total_projects: int = 0
    total_certifications: int = 0
    years_of_experience: float = 0.0
    skill_categories: dict[str, int] = Field(default_factory=dict)
    experience_timeline_years: list[int] = Field(default_factory=list)
    top_industries: list[str] = Field(default_factory=list)
