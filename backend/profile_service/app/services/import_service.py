"""Import/export service — JSON profile import and export."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Certification,
    Education,
    PersonalInfo,
    Project,
    Skill,
    SocialLink,
    UserProfile,
    WorkExperience,
)
from app.schemas.profile import ProfileCreate


class ImportService:
    """Service for importing and exporting profiles as JSON."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def export_profile(self, profile: UserProfile) -> dict:
        """Export a full profile as a JSON-serializable dict."""
        data = {
            "profile": {
                "headline": profile.headline,
                "summary": profile.summary,
                "location_city": profile.location_city,
                "location_state": profile.location_state,
                "location_country": profile.location_country,
                "location_type": profile.location_type.value if profile.location_type else None,
                "preferred_roles": profile.preferred_roles or [],
                "target_salary_min": profile.target_salary_min,
                "target_salary_max": profile.target_salary_max,
                "target_salary_currency": profile.target_salary_currency,
                "open_to_work": profile.open_to_work,
                "open_to_relocation": profile.open_to_relocation,
                "years_of_experience": profile.years_of_experience,
            },
            "personal_info": None,
            "skills": [],
            "work_experiences": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "social_links": [],
        }

        if profile.personal_info:
            data["personal_info"] = {
                "full_name": profile.personal_info.full_name,
                "first_name": profile.personal_info.first_name,
                "last_name": profile.personal_info.last_name,
                "email": profile.personal_info.email,
                "phone": profile.personal_info.phone,
                "city": profile.personal_info.city,
                "state": profile.personal_info.state,
                "country": profile.personal_info.country,
                "pronouns": profile.personal_info.pronouns,
            }

        for skill in profile.skills or []:
            data["skills"].append({
                "name": skill.name,
                "category": skill.category,
                "proficiency": skill.proficiency.value if skill.proficiency else "intermediate",
                "years_used": skill.years_used,
                "is_top_skill": skill.is_top_skill,
            })

        for exp in profile.work_experiences or []:
            data["work_experiences"].append({
                "company_name": exp.company_name,
                "job_title": exp.job_title,
                "employment_type": exp.employment_type.value if exp.employment_type else None,
                "start_date": exp.start_date.isoformat() if exp.start_date else None,
                "end_date": exp.end_date.isoformat() if exp.end_date else None,
                "is_current": exp.is_current,
                "description": exp.description,
                "achievements": exp.achievements or [],
                "skills_used": exp.skills_used or [],
            })

        for edu in profile.education or []:
            data["education"].append({
                "institution": edu.institution,
                "degree": edu.degree,
                "field_of_study": edu.field_of_study,
                "start_date": edu.start_date.isoformat() if edu.start_date else None,
                "end_date": edu.end_date.isoformat() if edu.end_date else None,
                "is_current": edu.is_current,
                "description": edu.description,
            })

        for proj in profile.projects or []:
            data["projects"].append({
                "name": proj.name,
                "description": proj.description,
                "technologies": proj.technologies or [],
                "url": proj.url,
                "highlights": proj.highlights or [],
            })

        for cert in profile.certifications or []:
            data["certifications"].append({
                "name": cert.name,
                "issuer": cert.issuer,
                "issue_date": cert.issue_date.isoformat() if cert.issue_date else None,
                "credential_id": cert.credential_id,
            })

        for link in profile.social_links or []:
            data["social_links"].append({
                "platform": link.platform.value if link.platform else None,
                "url": link.url,
                "label": link.label,
                "is_primary": link.is_primary,
            })

        return data

    async def import_profile(
        self, user_id: UUID, import_data: dict
    ) -> UserProfile | None:
        """Import a profile from a JSON dict.

        Creates or updates the profile with imported data.
        """
        profile_data = import_data.get("profile", {})

        # Check if profile already exists
        from sqlalchemy import select
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            profile = existing
            # Update scalar fields
            for key, value in profile_data.items():
                if value is not None and hasattr(profile, key):
                    setattr(profile, key, value)
        else:
            profile = UserProfile(user_id=user_id, **profile_data)
            self.session.add(profile)

        # Personal info
        pi_data = import_data.get("personal_info")
        if pi_data:
            if profile.personal_info:
                for key, value in pi_data.items():
                    if value is not None:
                        setattr(profile.personal_info, key, value)
            else:
                profile.personal_info = PersonalInfo(profile=profile, **pi_data)

        # Skills
        if "skills" in import_data:
            profile.skills = []
            for s in import_data["skills"]:
                profile.skills.append(Skill(profile=profile, **s))

        # Work experiences
        if "work_experiences" in import_data:
            profile.work_experiences = []
            for e in import_data["work_experiences"]:
                profile.work_experiences.append(
                    WorkExperience(profile=profile, **e)
                )

        await self.session.flush()
        return profile
