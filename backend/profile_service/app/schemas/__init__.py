"""Profile Service Pydantic schemas."""

from app.schemas.certification import CertificationCreate, CertificationResponse, CertificationUpdate
from app.schemas.education import EducationCreate, EducationResponse, EducationUpdate
from app.schemas.experience import WorkExperienceCreate, WorkExperienceResponse, WorkExperienceUpdate
from app.schemas.personal_info import PersonalInfoCreate, PersonalInfoResponse, PersonalInfoUpdate
from app.schemas.profile import (
    ProfileAnalyticsResponse,
    ProfileCreate,
    ProfileCreateRequest,
    ProfileImportRequest,
    ProfileListResponse,
    ProfileResponse,
    ProfileSummary,
    ProfileUpdate,
)
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.skill import SkillBulkCreateRequest, SkillCreate, SkillResponse, SkillUpdate
from app.schemas.language import LanguageCreate, LanguageResponse, LanguageUpdate
from app.schemas.social_link import SocialLinkCreate, SocialLinkResponse, SocialLinkUpdate

__all__ = [
    # Profile
    "ProfileCreate",
    "ProfileCreateRequest",
    "ProfileResponse",
    "ProfileSummary",
    "ProfileListResponse",
    "ProfileUpdate",
    "ProfileImportRequest",
    "ProfileAnalyticsResponse",
    # PersonalInfo
    "PersonalInfoCreate",
    "PersonalInfoUpdate",
    "PersonalInfoResponse",
    # Skill
    "SkillCreate",
    "SkillUpdate",
    "SkillResponse",
    "SkillBulkCreateRequest",
    # WorkExperience
    "WorkExperienceCreate",
    "WorkExperienceUpdate",
    "WorkExperienceResponse",
    # Education
    "EducationCreate",
    "EducationUpdate",
    "EducationResponse",
    # Project
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    # Certification
    "CertificationCreate",
    "CertificationUpdate",
    "CertificationResponse",
    # Language
    "LanguageCreate",
    "LanguageUpdate",
    "LanguageResponse",
    # SocialLink
    "SocialLinkCreate",
    "SocialLinkUpdate",
    "SocialLinkResponse",
]
