"""Experience service — timeline management and ordering."""

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import WorkExperience


class ExperienceService:
    """Service for work experience timeline management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_timeline(self, profile_id: UUID) -> list[dict]:
        """Get work experiences ordered as a timeline (newest first)."""
        result = await self.session.execute(
            select(WorkExperience)
            .where(WorkExperience.profile_id == profile_id)
            .order_by(WorkExperience.start_date.desc().nulls_last())
        )
        experiences = result.scalars().all()

        timeline = []
        for exp in experiences:
            timeline.append({
                "id": str(exp.id),
                "company_name": exp.company_name,
                "job_title": exp.job_title,
                "start_date": exp.start_date.isoformat() if exp.start_date else None,
                "end_date": exp.end_date.isoformat() if exp.end_date else None,
                "is_current": exp.is_current,
                "employment_type": exp.employment_type.value if exp.employment_type else None,
                "location": exp.location,
                "description": exp.description,
                "achievements": exp.achievements or [],
                "skills_used": exp.skills_used or [],
            })
        return timeline

    async def get_experience_summary(self, profile_id: UUID) -> dict:
        """Get summary stats about work history."""
        timeline = await self.get_timeline(profile_id)

        if not timeline:
            return {
                "total_experiences": 0,
                "total_years": 0,
                "current_role": None,
                "companies": [],
                "average_tenure_years": 0,
            }

        companies = list(set(e["company_name"] for e in timeline if e["company_name"]))
        current = next((e for e in timeline if e["is_current"]), None)
        total_years = self._compute_total_years(timeline)

        return {
            "total_experiences": len(timeline),
            "total_years": round(total_years, 1),
            "current_role": current,
            "companies": companies,
            "average_tenure_years": round(total_years / len(timeline), 1) if timeline else 0,
        }

    def _compute_total_years(self, timeline: list[dict]) -> float:
        """Compute total years of experience from timeline."""
        total_days = 0
        for entry in timeline:
            start = date.fromisoformat(entry["start_date"]) if entry.get("start_date") else None
            end = date.fromisoformat(entry["end_date"]) if entry.get("end_date") else date.today()
            if start and end:
                total_days += (end - start).days
        return total_days / 365.25
