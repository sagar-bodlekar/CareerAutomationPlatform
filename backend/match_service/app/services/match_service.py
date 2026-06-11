"""Match service - orchestrates matchers and stores results."""

import logging
from typing import Any, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import JobMatch
from ..schemas.match import MatchScoreRequest, MatchScoreResponse
from .education_matcher import EducationMatcher
from .experience_matcher import ExperienceMatcher
from .location_matcher import LocationMatcher
from .skills_matcher import SkillsMatcher
from .title_matcher import TitleMatcher

logger = logging.getLogger(__name__)


class MatchService:
    """Orchestrates match scoring across all dimensions.

    Coordinates SkillsMatcher, ExperienceMatcher, EducationMatcher,
    LocationMatcher, and TitleMatcher to produce a composite score.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.skills_matcher = SkillsMatcher()
        self.experience_matcher = ExperienceMatcher()
        self.education_matcher = EducationMatcher()
        self.location_matcher = LocationMatcher()
        self.title_matcher = TitleMatcher()

    # ─── Scoring Weights ─────────────────────────────────

    # Default weights for each dimension
    WEIGHTS: dict[str, float] = {
        "skills": 0.35,
        "experience": 0.25,
        "education": 0.10,
        "location": 0.10,
        "title": 0.20,
    }

    # ─── Score Computation ────────────────────────────────

    async def compute_score(
        self,
        request: MatchScoreRequest,
    ) -> MatchScoreResponse:
        """Compute match score for a profile against a job.

        Uses profile data and job data from the request, or
        fetches from respective services if not provided.
        """
        profile_data = request.profile_data or {}
        job_data = request.job_data or {}

        # Extract profile fields
        profile_skills = profile_data.get("skills", [])
        profile_locations = profile_data.get("locations", [profile_data.get("location", "")])
        profile_experience_years = profile_data.get("experience_years")
        profile_experience_level = profile_data.get("experience_level")
        profile_education = profile_data.get("education", [])
        profile_titles = profile_data.get("titles", [profile_data.get("current_title", "")])
        profile_location = profile_data.get("location", "")

        # Extract job fields
        job_required_skills = job_data.get("required_skills", [])
        job_nice_to_have = job_data.get("nice_to_have_skills", [])
        job_location = job_data.get("location", "")
        job_is_remote = job_data.get("is_remote", False)
        job_experience_min = job_data.get("experience_min_years")
        job_experience_max = job_data.get("experience_max_years")
        job_experience_level = job_data.get("experience_level")
        job_education = job_data.get("education_required")
        job_preferred_degree = job_data.get("degree_preferred")
        job_title = job_data.get("title", "")

        # Compute individual scores
        skills_result = self.skills_matcher.compute(
            profile_skills=profile_skills,
            required_skills=job_required_skills,
            nice_to_have=job_nice_to_have,
        )
        experience_result = self.experience_matcher.compute(
            profile_years=profile_experience_years,
            required_min=job_experience_min,
            required_max=job_experience_max,
            profile_level=profile_experience_level,
            job_level=job_experience_level,
        )
        education_result = self.education_matcher.compute(
            profile_education=profile_education,
            required_education=job_education,
            preferred_degree=job_preferred_degree,
        )
        location_result = self.location_matcher.compute(
            profile_location=profile_location,
            job_location=job_location,
            is_remote_job=job_is_remote,
        )
        title_result = self.title_matcher.compute(
            profile_titles=profile_titles,
            job_title=job_title,
        )

        # Composite score
        weights = self.WEIGHTS
        overall = (
            skills_result["score"] * weights["skills"]
            + experience_result["score"] * weights["experience"]
            + education_result["score"] * weights["education"]
            + location_result["score"] * weights["location"]
            + title_result["score"] * weights["title"]
        )

        return MatchScoreResponse(
            profile_id=request.profile_id,
            job_id=request.job_id,
            overall_score=round(overall, 1),
            skills_score=round(skills_result["score"], 1),
            experience_score=round(experience_result["score"], 1),
            education_score=round(education_result["score"], 1),
            location_score=round(location_result["score"], 1),
            title_score=round(title_result["score"], 1),
            matched_skills=skills_result.get("matched_skills", []),
            missing_skills=skills_result.get("missing_skills", []),
            extra_skills=skills_result.get("extra_skills", []),
            match_summary=self._generate_summary(
                overall, skills_result, title_result
            ),
        )

    async def save_match(
        self,
        score_response: MatchScoreResponse,
    ) -> JobMatch:
        """Save a match result to the database.

        Creates or updates the match record.
        """
        # Check for existing match
        result = await self.db.execute(
            select(JobMatch).where(
                JobMatch.profile_id == score_response.profile_id,
                JobMatch.job_id == score_response.job_id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.overall_score = score_response.overall_score
            existing.skills_score = score_response.skills_score
            existing.experience_score = score_response.experience_score
            existing.education_score = score_response.education_score
            existing.location_score = score_response.location_score
            existing.title_score = score_response.title_score
            existing.matched_skills = score_response.matched_skills
            existing.missing_skills = score_response.missing_skills
            existing.extra_skills = score_response.extra_skills
            existing.match_summary = score_response.match_summary
            match = existing
        else:
            # Create new
            match = JobMatch(
                profile_id=score_response.profile_id,
                job_id=score_response.job_id,
                overall_score=score_response.overall_score,
                skills_score=score_response.skills_score,
                experience_score=score_response.experience_score,
                education_score=score_response.education_score,
                location_score=score_response.location_score,
                title_score=score_response.title_score,
                matched_skills=score_response.matched_skills,
                missing_skills=score_response.missing_skills,
                extra_skills=score_response.extra_skills,
                match_summary=score_response.match_summary,
            )
            self.db.add(match)

        await self.db.flush()
        await self.db.refresh(match)

        # Update response with match ID
        score_response.match_id = match.id
        return match

    # ─── Retrieval ───────────────────────────────────────

    async def get_match(self, match_id: int) -> Optional[JobMatch]:
        """Get a match by ID."""
        result = await self.db.execute(
            select(JobMatch).where(JobMatch.id == match_id)
        )
        return result.scalar_one_or_none()

    async def get_profile_matches(
        self,
        profile_id: int,
        limit: int = 20,
        offset: int = 0,
        min_score: float = 0,
    ) -> tuple[list[JobMatch], int]:
        """Get top matches for a profile."""
        query = (
            select(JobMatch)
            .where(
                JobMatch.profile_id == profile_id,
                JobMatch.overall_score >= min_score,
                JobMatch.status == "active",
            )
            .order_by(desc(JobMatch.overall_score))
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        matches = list(result.scalars().all())

        # Count total
        count_query = select(JobMatch).where(
            JobMatch.profile_id == profile_id,
            JobMatch.overall_score >= min_score,
            JobMatch.status == "active",
        )
        count_result = await self.db.execute(count_query)
        total = len(count_result.scalars().all())

        return matches, total

    async def get_skill_gaps(
        self,
        profile_id: int,
        job_id: int,
    ) -> Optional[dict[str, Any]]:
        """Get skill gap analysis for a profile+job combination."""
        result = await self.db.execute(
            select(JobMatch).where(
                JobMatch.profile_id == profile_id,
                JobMatch.job_id == job_id,
            )
        )
        match = result.scalar_one_or_none()
        if not match:
            return None

        return {
            "matched_skills": match.matched_skills or [],
            "missing_skills": match.missing_skills or [],
            "extra_skills": match.extra_skills or [],
            "match_percentage": match.overall_score,
        }

    # ─── Helpers ─────────────────────────────────────────

    def _generate_summary(
        self,
        overall_score: float,
        skills_result: dict,
        title_result: dict,
    ) -> str:
        """Generate a human-readable match summary."""
        if overall_score >= 85:
            level = "Excellent"
        elif overall_score >= 70:
            level = "Strong"
        elif overall_score >= 50:
            level = "Moderate"
        elif overall_score >= 30:
            level = "Weak"
        else:
            level = "Poor"

        matched_count = len(skills_result.get("matched_skills", []))
        missing_count = len(skills_result.get("missing_skills", []))

        return (
            f"{level} match ({overall_score:.0f}/100). "
            f"{matched_count} skills matched, {missing_count} missing. "
            f"Best title match: {title_result.get('best_match_title', 'N/A')}."
        )
