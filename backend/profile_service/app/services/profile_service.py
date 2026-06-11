"""Profile service — core business logic for profile CRUD and management."""

from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import SkillProficiency
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
from app.schemas.profile import (
    ProfileAnalyticsResponse,
    ProfileCreate,
    ProfileSummary,
    ProfileUpdate,
)


class ProfileService:
    """Service for managing user profiles."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ─── Load helpers ───────────────────────────────────────

    LOAD_OPTIONS = [
        selectinload(UserProfile.personal_info),
        selectinload(UserProfile.skills),
        selectinload(UserProfile.work_experiences),
        selectinload(UserProfile.education),
        selectinload(UserProfile.projects),
        selectinload(UserProfile.certifications),
        selectinload(UserProfile.social_links),
    ]

    async def _get_by_id(self, profile_id: UUID) -> UserProfile | None:
        """Get profile by ID with all relationships loaded."""
        result = await self.session.execute(
            select(UserProfile)
            .options(*self.LOAD_OPTIONS)
            .where(UserProfile.id == profile_id)
        )
        return result.scalar_one_or_none()

    async def _get_by_user_id(self, user_id: UUID) -> UserProfile | None:
        """Get profile by user ID with all relationships loaded."""
        result = await self.session.execute(
            select(UserProfile)
            .options(*self.LOAD_OPTIONS)
            .where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    # ─── CRUD ───────────────────────────────────────────────

    async def create_profile(
        self, user_id: UUID, data: ProfileCreate
    ) -> UserProfile:
        """Create a new profile with optional nested data."""
        profile = UserProfile(
            user_id=user_id,
            headline=data.headline,
            summary=data.summary,
            location_city=data.location_city,
            location_state=data.location_state,
            location_country=data.location_country,
            location_type=data.location_type,
            preferred_roles=data.preferred_roles or [],
            target_salary_min=data.target_salary_min,
            target_salary_max=data.target_salary_max,
            target_salary_currency=data.target_salary_currency,
            open_to_work=data.open_to_work,
            open_to_relocation=data.open_to_relocation,
            years_of_experience=data.years_of_experience or 0.0,
        )

        # Personal info
        if data.personal_info:
            profile.personal_info = PersonalInfo(
                profile=profile,
                **data.personal_info.model_dump(exclude_none=True),
            )

        # Skills
        if data.skills:
            for skill_data in data.skills:
                profile.skills.append(
                    Skill(profile=profile, **skill_data.model_dump(exclude_none=True))
                )

        # Social links
        if data.social_links:
            for link_data in data.social_links:
                profile.social_links.append(
                    SocialLink(profile=profile, **link_data.model_dump(exclude_none=True))
                )

        self.session.add(profile)
        await self.session.flush()
        return profile

    async def get_profile(self, profile_id: UUID) -> UserProfile | None:
        """Get a profile by ID."""
        return await self._get_by_id(profile_id)

    async def get_profile_by_user(self, user_id: UUID) -> UserProfile | None:
        """Get a profile by user ID."""
        return await self._get_by_user_id(user_id)

    async def update_profile(
        self, profile_id: UUID, data: ProfileUpdate
    ) -> UserProfile | None:
        """Update profile fields. Returns None if not found."""
        profile = await self._get_by_id(profile_id)
        if profile is None:
            return None

        update_data = data.model_dump(exclude_none=True, exclude={"personal_info", "skills"})
        for field, value in update_data.items():
            setattr(profile, field, value)

        # Update personal info
        if data.personal_info:
            if profile.personal_info:
                for field, value in data.personal_info.model_dump(exclude_none=True).items():
                    setattr(profile.personal_info, field, value)
            else:
                profile.personal_info = PersonalInfo(
                    profile=profile, **data.personal_info.model_dump(exclude_none=True)
                )

        await self.session.flush()
        return profile

    async def delete_profile(self, profile_id: UUID) -> bool:
        """Delete a profile. Returns True if deleted, False if not found."""
        profile = await self.session.get(UserProfile, profile_id)
        if profile is None:
            return False
        await self.session.delete(profile)
        await self.session.flush()
        return True

    async def list_profiles(
        self,
        page: int = 1,
        page_size: int = 20,
        open_to_work: bool | None = None,
    ) -> tuple[list[UserProfile], int]:
        """List profiles with pagination."""
        query = select(UserProfile).options(
            selectinload(UserProfile.skills),
            selectinload(UserProfile.work_experiences),
        )

        if open_to_work is not None:
            query = query.where(UserProfile.open_to_work == open_to_work)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(UserProfile.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(query)
        profiles = result.scalars().all()

        return list(profiles), total

    def to_summary(self, profile: UserProfile) -> ProfileSummary:
        """Convert a UserProfile to a ProfileSummary."""
        return ProfileSummary(
            id=profile.id,
            user_id=profile.user_id,
            headline=profile.headline,
            location_city=profile.location_city,
            location_country=profile.location_country,
            location_type=profile.location_type.value if profile.location_type else None,
            open_to_work=profile.open_to_work,
            years_of_experience=profile.years_of_experience,
            skill_count=len(profile.skills) if profile.skills else 0,
            total_experiences=len(profile.work_experiences) if profile.work_experiences else 0,
            created_at=profile.created_at,
        )

    # ─── Sub-entity management ──────────────────────────────

    async def add_skill(self, profile_id: UUID, skill_data) -> Skill | None:
        """Add a single skill to a profile."""
        profile = await self.session.get(UserProfile, profile_id)
        if profile is None:
            return None
        skill = Skill(profile_id=profile_id, **skill_data.model_dump(exclude_none=True))
        self.session.add(skill)
        await self.session.flush()
        return skill

    async def bulk_add_skills(self, profile_id: UUID, skills_data: list) -> list[Skill]:
        """Add multiple skills to a profile in bulk."""
        skills = []
        for skill_data in skills_data:
            skill = Skill(profile_id=profile_id, **skill_data.model_dump(exclude_none=True))
            self.session.add(skill)
            skills.append(skill)
        await self.session.flush()
        return skills

    async def update_skill(self, skill_id: UUID, skill_data) -> Skill | None:
        """Update a skill."""
        result = await self.session.execute(
            select(Skill).where(Skill.id == skill_id)
        )
        skill = result.scalar_one_or_none()
        if skill is None:
            return None
        for field, value in skill_data.model_dump(exclude_none=True).items():
            setattr(skill, field, value)
        await self.session.flush()
        return skill

    async def delete_skill(self, skill_id: UUID) -> bool:
        """Delete a skill."""
        result = await self.session.execute(
            select(Skill).where(Skill.id == skill_id)
        )
        skill = result.scalar_one_or_none()
        if skill is None:
            return False
        await self.session.delete(skill)
        await self.session.flush()
        return True

    async def add_work_experience(self, profile_id: UUID, experience_data) -> WorkExperience | None:
        """Add a work experience entry."""
        profile = await self.session.get(UserProfile, profile_id)
        if profile is None:
            return None
        exp = WorkExperience(
            profile_id=profile_id, **experience_data.model_dump(exclude_none=True)
        )
        self.session.add(exp)
        await self.session.flush()
        return exp

    async def update_work_experience(self, exp_id: UUID, exp_data) -> WorkExperience | None:
        """Update a work experience entry."""
        result = await self.session.execute(
            select(WorkExperience).where(WorkExperience.id == exp_id)
        )
        exp = result.scalar_one_or_none()
        if exp is None:
            return None
        for field, value in exp_data.model_dump(exclude_none=True).items():
            setattr(exp, field, value)
        await self.session.flush()
        return exp

    async def delete_work_experience(self, exp_id: UUID) -> bool:
        """Delete a work experience entry."""
        result = await self.session.execute(
            select(WorkExperience).where(WorkExperience.id == exp_id)
        )
        exp = result.scalar_one_or_none()
        if exp is None:
            return False
        await self.session.delete(exp)
        await self.session.flush()
        return True

    # ─── Analytics ──────────────────────────────────────────

    async def get_analytics(self, profile_id: UUID) -> ProfileAnalyticsResponse | None:
        """Compute analytics for a profile."""
        profile = await self._get_by_id(profile_id)
        if profile is None:
            return None

        skills = profile.skills or []
        experiences = profile.work_experiences or []
        education = profile.education or []
        projects = profile.projects or []
        certifications = profile.certifications or []

        # Skill categories
        skill_categories: dict[str, int] = {}
        for s in skills:
            cat = s.category or "Uncategorized"
            skill_categories[cat] = skill_categories.get(cat, 0) + 1

        # Top skills (expert/advanced)
        top_skills = [
            s.name for s in skills
            if s.proficiency in (SkillProficiency.EXPERT, SkillProficiency.ADVANCED)
        ]

        # Experience timeline years
        timeline_years = sorted(
            set(
                e.start_date.year for e in experiences if e.start_date
            ),
            reverse=True,
        )

        # Top industries (from company names — simple heuristic)
        # In a real app this would use industry classification
        top_industries = list(
            dict.fromkeys(
                e.company_name for e in experiences[:5] if e.company_name
            )
        )

        return ProfileAnalyticsResponse(
            profile_id=profile_id,
            total_skills=len(skills),
            top_skills=top_skills,
            total_experiences=len(experiences),
            total_education=len(education),
            total_projects=len(projects),
            total_certifications=len(certifications),
            years_of_experience=profile.years_of_experience or 0.0,
            skill_categories=skill_categories,
            experience_timeline_years=timeline_years,
            top_industries=top_industries,
        )
