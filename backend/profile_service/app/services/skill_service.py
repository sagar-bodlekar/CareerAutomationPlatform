"""Skill service — category management and bulk operations."""

from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Skill, UserProfile


class SkillService:
    """Service for advanced skill management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_skills_by_category(
        self, profile_id: UUID
    ) -> dict[str, list[dict]]:
        """Get skills grouped by category."""
        result = await self.session.execute(
            select(Skill)
            .where(Skill.profile_id == profile_id)
            .order_by(Skill.category, Skill.order)
        )
        skills = result.scalars().all()

        grouped: dict[str, list[dict]] = {}
        for skill in skills:
            cat = skill.category or "Uncategorized"
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append({
                "id": str(skill.id),
                "name": skill.name,
                "proficiency": skill.proficiency.value if skill.proficiency else "intermediate",
                "years_used": skill.years_used,
                "is_top_skill": skill.is_top_skill,
                "order": skill.order,
            })
        return grouped

    async def get_categories(self, profile_id: UUID) -> list[str]:
        """Get distinct skill categories for a profile."""
        result = await self.session.execute(
            select(Skill.category)
            .where(Skill.profile_id == profile_id)
            .distinct()
            .order_by(Skill.category)
        )
        return [row[0] for row in result if row[0]]

    async def reorder_skills(
        self, profile_id: UUID, skill_ids: list[UUID]
    ) -> bool:
        """Reorder skills by providing an ordered list of skill IDs."""
        profile = await self.session.get(UserProfile, profile_id)
        if profile is None:
            return False

        for order, skill_id in enumerate(skill_ids):
            result = await self.session.execute(
                select(Skill).where(
                    Skill.id == skill_id,
                    Skill.profile_id == profile_id,
                )
            )
            skill = result.scalar_one_or_none()
            if skill:
                skill.order = order

        await self.session.flush()
        return True
