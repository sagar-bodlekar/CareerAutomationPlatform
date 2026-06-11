"""Personalization service for extracting hooks from company data."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PersonalizationService:
    """Extracts personalization hooks and talking points from company data."""

    async def extract_hooks(
        self,
        company_name: str,
        industry: Optional[str] = None,
        company_description: Optional[str] = None,
        recent_news: Optional[str] = None,
        skills: Optional[list[str]] = None,
    ) -> dict:
        """Extract personalization hooks for cover letters/emails."""
        hooks = []
        key_points = []

        if company_description:
            key_points.append(f"Knowledge of {company_name}'s mission and work")
            sentences = [s.strip() for s in company_description.split(".") if s.strip()]
            if sentences:
                hooks.append({
                    "hook": f"Mention specific knowledge of {sentences[0][:100]}",
                    "where_to_use": "cover_letter",
                })

        if skills:
            hooks.append({
                "hook": f"Highlight relevant skills: {', '.join(skills[:5])}",
                "where_to_use": "all",
            })

        return {
            "personalization_hooks": hooks,
            "key_talking_points": key_points,
            "recommended_tone": "professional",
            "hooks_found": len(hooks),
        }

    async def extract_from_job(
        self,
        job_title: str,
        job_description: Optional[str] = None,
        required_skills: Optional[list[str]] = None,
    ) -> dict:
        """Extract personalization hooks from job data."""
        hooks = []
        if job_description:
            hooks.append({
                "hook": f"Reference specific requirements from the job description",
                "where_to_use": "cover_letter",
            })
        if required_skills:
            hooks.append({
                "hook": f"Address specific skills: {', '.join(required_skills[:5])}",
                "where_to_use": "all",
            })
        return {"hooks": hooks, "count": len(hooks)}
