"""Profile Service API endpoints — all CRUD, export, import, analytics."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from shared.schemas.common import APIResponse
from shared.schemas.pagination import PaginatedResponse, PaginationMeta

from app.schemas import (
    CertificationCreate,
    CertificationUpdate,
    EducationCreate,
    EducationUpdate,
    ProfileAnalyticsResponse,
    ProfileCreate,
    ProfileCreateRequest,
    ProfileImportRequest,
    ProfileListResponse,
    ProfileResponse,
    ProfileSummary,
    ProfileUpdate,
    ProjectCreate,
    ProjectUpdate,
    SkillBulkCreateRequest,
    SkillCreate,
    SkillUpdate,
    SocialLinkCreate,
    SocialLinkUpdate,
    WorkExperienceCreate,
    WorkExperienceResponse,
    WorkExperienceUpdate,
)
from app.schemas.skill import SkillResponse
from app.services.profile_service import ProfileService
from app.api.v1.dependencies import get_profile_service

router = APIRouter(tags=["profiles"])


# ─── Profile CRUD ────────────────────────────────────────────


@router.post("/profiles", status_code=201, response_model=APIResponse)
async def create_profile(
    request: ProfileCreateRequest,
    service: ProfileService = Depends(get_profile_service),
):
    """Create a new user profile with optional nested data."""
    profile = await service.create_profile(request.user_id, request.profile)
    return APIResponse(
        data=ProfileResponse.model_validate(profile),
        message="Profile created",
    )


@router.get("/profiles/{profile_id}", response_model=APIResponse)
async def get_profile(
    profile_id: UUID,
    service: ProfileService = Depends(get_profile_service),
):
    """Get a full profile by ID with all nested data."""
    profile = await service.get_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return APIResponse(data=ProfileResponse.model_validate(profile))


@router.get("/profiles/user/{user_id}", response_model=APIResponse)
async def get_profile_by_user(
    user_id: UUID,
    service: ProfileService = Depends(get_profile_service),
):
    """Get a profile by user ID."""
    profile = await service.get_profile_by_user(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found for this user")
    return APIResponse(data=ProfileResponse.model_validate(profile))


@router.put("/profiles/{profile_id}", response_model=APIResponse)
async def update_profile(
    profile_id: UUID,
    data: ProfileUpdate,
    service: ProfileService = Depends(get_profile_service),
):
    """Update profile fields and nested personal info."""
    profile = await service.update_profile(profile_id, data)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return APIResponse(
        data=ProfileResponse.model_validate(profile),
        message="Profile updated",
    )


@router.delete("/profiles/{profile_id}", response_model=APIResponse)
async def delete_profile(
    profile_id: UUID,
    service: ProfileService = Depends(get_profile_service),
):
    """Delete a profile."""
    deleted = await service.delete_profile(profile_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")
    return APIResponse(message="Profile deleted")


@router.get("/profiles", response_model=PaginatedResponse)
async def list_profiles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    open_to_work: bool | None = None,
    service: ProfileService = Depends(get_profile_service),
):
    """List profiles with pagination and optional filters."""
    profiles, total = await service.list_profiles(
        page=page, page_size=page_size, open_to_work=open_to_work
    )
    summaries = [service.to_summary(p) for p in profiles]
    return PaginatedResponse(
        data=[s.model_dump() for s in summaries],
        meta=PaginationMeta.compute(
            page=page, per_page=page_size, total=total
        ),
    )


# ─── Skills ──────────────────────────────────────────────────


@router.post("/profiles/{profile_id}/skills", status_code=201, response_model=APIResponse)
async def add_skill(
    profile_id: UUID,
    skill_data: SkillCreate,
    service: ProfileService = Depends(get_profile_service),
):
    """Add a single skill to a profile."""
    skill = await service.add_skill(profile_id, skill_data)
    if skill is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return APIResponse(
        data=SkillResponse.model_validate(skill),
        message="Skill added",
    )


@router.post("/profiles/{profile_id}/skills/bulk", status_code=201, response_model=APIResponse)
async def bulk_add_skills(
    profile_id: UUID,
    request: SkillBulkCreateRequest,
    service: ProfileService = Depends(get_profile_service),
):
    """Add multiple skills to a profile at once."""
    skills = await service.bulk_add_skills(profile_id, request.skills)
    return APIResponse(
        data=[SkillResponse.model_validate(s) for s in skills],
        message=f"{len(skills)} skills added",
    )


@router.put("/skills/{skill_id}", response_model=APIResponse)
async def update_skill(
    skill_id: UUID,
    skill_data: SkillUpdate,
    service: ProfileService = Depends(get_profile_service),
):
    """Update a skill."""
    skill = await service.update_skill(skill_id, skill_data)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return APIResponse(
        data=SkillResponse.model_validate(skill),
        message="Skill updated",
    )


@router.delete("/skills/{skill_id}", response_model=APIResponse)
async def delete_skill(
    skill_id: UUID,
    service: ProfileService = Depends(get_profile_service),
):
    """Delete a skill."""
    deleted = await service.delete_skill(skill_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Skill not found")
    return APIResponse(message="Skill deleted")


# ─── Work Experience ─────────────────────────────────────────


@router.post("/profiles/{profile_id}/experiences", status_code=201, response_model=APIResponse)
async def add_work_experience(
    profile_id: UUID,
    exp_data: WorkExperienceCreate,
    service: ProfileService = Depends(get_profile_service),
):
    """Add a work experience entry."""
    exp = await service.add_work_experience(profile_id, exp_data)
    if exp is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return APIResponse(
        data=WorkExperienceResponse.model_validate(exp),
        message="Work experience added",
    )


@router.put("/experiences/{exp_id}", response_model=APIResponse)
async def update_work_experience(
    exp_id: UUID,
    exp_data: WorkExperienceUpdate,
    service: ProfileService = Depends(get_profile_service),
):
    """Update a work experience entry."""
    exp = await service.update_work_experience(exp_id, exp_data)
    if exp is None:
        raise HTTPException(status_code=404, detail="Work experience not found")
    return APIResponse(
        data=WorkExperienceResponse.model_validate(exp),
        message="Work experience updated",
    )


@router.delete("/experiences/{exp_id}", response_model=APIResponse)
async def delete_work_experience(
    exp_id: UUID,
    service: ProfileService = Depends(get_profile_service),
):
    """Delete a work experience entry."""
    deleted = await service.delete_work_experience(exp_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Work experience not found")
    return APIResponse(message="Work experience deleted")


# ─── Education ───────────────────────────────────────────────


@router.post("/profiles/{profile_id}/education", status_code=201, response_model=APIResponse)
async def add_education(
    profile_id: UUID,
    edu_data: EducationCreate,
    service: ProfileService = Depends(get_profile_service),
):
    """Add an education entry to a profile."""
    edu = await service.add_education(profile_id, edu_data)
    if edu is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return APIResponse(
        data=EducationResponse.model_validate(edu),
        message="Education added",
    )


@router.put("/education/{edu_id}", response_model=APIResponse)
async def update_education(
    edu_id: UUID,
    edu_data: EducationUpdate,
    service: ProfileService = Depends(get_profile_service),
):
    """Update an education entry."""
    edu = await service.update_education(edu_id, edu_data)
    if edu is None:
        raise HTTPException(status_code=404, detail="Education entry not found")
    return APIResponse(
        data=EducationResponse.model_validate(edu),
        message="Education updated",
    )


@router.delete("/education/{edu_id}", response_model=APIResponse)
async def delete_education(
    edu_id: UUID,
    service: ProfileService = Depends(get_profile_service),
):
    """Delete an education entry."""
    deleted = await service.delete_education(edu_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Education entry not found")
    return APIResponse(message="Education deleted")


# ─── Projects ─────────────────────────────────────────────────


@router.post("/profiles/{profile_id}/projects", status_code=201, response_model=APIResponse)
async def add_project(
    profile_id: UUID,
    project_data: ProjectCreate,
    service: ProfileService = Depends(get_profile_service),
):
    """Add a project to a profile."""
    proj = await service.add_project(profile_id, project_data)
    if proj is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return APIResponse(
        data=ProjectResponse.model_validate(proj),
        message="Project added",
    )


@router.put("/projects/{proj_id}", response_model=APIResponse)
async def update_project(
    proj_id: UUID,
    project_data: ProjectUpdate,
    service: ProfileService = Depends(get_profile_service),
):
    """Update a project."""
    proj = await service.update_project(proj_id, project_data)
    if proj is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return APIResponse(
        data=ProjectResponse.model_validate(proj),
        message="Project updated",
    )


@router.delete("/projects/{proj_id}", response_model=APIResponse)
async def delete_project(
    proj_id: UUID,
    service: ProfileService = Depends(get_profile_service),
):
    """Delete a project."""
    deleted = await service.delete_project(proj_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return APIResponse(message="Project deleted")


# ─── Export / Import ─────────────────────────────────────────


@router.get("/profiles/{profile_id}/export", response_model=APIResponse)
async def export_profile(
    profile_id: UUID,
    service: ProfileService = Depends(get_profile_service),
):
    """Export a profile as JSON."""
    profile = await service.get_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    from app.services.import_service import ImportService
    from app.api.v1.dependencies import get_db_session

    import_service = ImportService(service.session)
    export_data = await import_service.export_profile(profile)
    return APIResponse(data=export_data, message="Profile exported")


@router.post("/profiles/{user_id}/import", status_code=201, response_model=APIResponse)
async def import_profile(
    user_id: UUID,
    import_data: ProfileImportRequest,
    service: ProfileService = Depends(get_profile_service),
):
    """Import a profile from JSON."""
    from app.services.import_service import ImportService

    import_service = ImportService(service.session)
    profile = await import_service.import_profile(
        user_id, import_data.model_dump(exclude_none=True)
    )
    return APIResponse(
        data=ProfileResponse.model_validate(profile),
        message="Profile imported",
    )


# ─── Analytics ───────────────────────────────────────────────


@router.get("/profiles/{profile_id}/analytics", response_model=APIResponse)
async def get_profile_analytics(
    profile_id: UUID,
    service: ProfileService = Depends(get_profile_service),
):
    """Get profile analytics: skill coverage, experience summary, etc."""
    analytics = await service.get_analytics(profile_id)
    if analytics is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return APIResponse(data=analytics.model_dump(), message="Profile analytics")
