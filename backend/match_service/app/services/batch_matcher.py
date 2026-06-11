"""Batch matcher - processes batch matching operations."""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.match import (
    BatchMatchRequest,
    BatchMatchResponse,
    MatchScoreRequest,
    MatchScoreResponse,
)
from .ai_match_integrator import AIMatchIntegrator
from .match_service import MatchService

logger = logging.getLogger(__name__)


class BatchMatcher:
    """Handles batch matching of profiles against jobs (or vice versa).

    Processes matches efficiently with configurable limits and
    optional AI enhancement.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.match_service = MatchService(db)
        self.ai_integrator = AIMatchIntegrator()

    async def process_batch(
        self,
        request: BatchMatchRequest,
    ) -> BatchMatchResponse:
        """Process a batch match request.

        Can match:
        - One profile against all active jobs
        - One job against all active profiles
        """
        matches = []
        total_processed = 0

        if request.profile_id and not request.job_id:
            # Match profile against all jobs
            matches, total_processed = await self._match_profile_to_jobs(
                profile_id=request.profile_id,
                limit=request.limit,
                use_ai=request.use_ai_enhancement,
            )
        elif request.job_id and not request.profile_id:
            # Match job against all profiles
            matches, total_processed = await self._match_job_to_profiles(
                job_id=request.job_id,
                limit=request.limit,
                use_ai=request.use_ai_enhancement,
            )
        else:
            logger.warning(
                "Batch match requires either profile_id or job_id (not both/none)"
            )

        return BatchMatchResponse(
            matches=matches,
            total_matched=len(matches),
            total_processed=total_processed,
            ai_enhanced=request.use_ai_enhancement,
        )

    async def _match_profile_to_jobs(
        self,
        profile_id: int,
        limit: int = 20,
        use_ai: bool = False,
    ) -> tuple[list[MatchScoreResponse], int]:
        """Match a single profile against active jobs.

        Fetches jobs from the Job Service and scores each one.
        """
        # In production, this would call the Job Service API
        # For now, we score based on available matches
        matches = []

        # Query existing matches for this profile, ordered by score
        from ..models.models import JobMatch
        result = await self.db.execute(
            select(JobMatch)
            .where(JobMatch.profile_id == profile_id, JobMatch.status == "active")
            .order_by(JobMatch.overall_score.desc())
            .limit(limit)
        )
        existing = result.scalars().all()

        for match in existing:
            score_response = MatchScoreResponse(
                match_id=match.id,
                profile_id=match.profile_id,
                job_id=match.job_id,
                overall_score=match.overall_score,
                skills_score=match.skills_score,
                experience_score=match.experience_score,
                education_score=match.education_score,
                location_score=match.location_score,
                title_score=match.title_score,
                matched_skills=match.matched_skills,
                missing_skills=match.missing_skills,
                extra_skills=match.extra_skills,
                match_summary=match.match_summary,
            )

            if use_ai:
                score_response = await self.ai_integrator.enhance_score(
                    score_response, {}
                )

            matches.append(score_response)

        return matches, len(existing)

    async def _match_job_to_profiles(
        self,
        job_id: int,
        limit: int = 20,
        use_ai: bool = False,
    ) -> tuple[list[MatchScoreResponse], int]:
        """Match a single job against all active profiles."""
        from ..models.models import JobMatch

        result = await self.db.execute(
            select(JobMatch)
            .where(JobMatch.job_id == job_id, JobMatch.status == "active")
            .order_by(JobMatch.overall_score.desc())
            .limit(limit)
        )
        existing = result.scalars().all()

        matches = []
        for match in existing:
            score_response = MatchScoreResponse(
                match_id=match.id,
                profile_id=match.profile_id,
                job_id=match.job_id,
                overall_score=match.overall_score,
                skills_score=match.skills_score,
                experience_score=match.experience_score,
                education_score=match.education_score,
                location_score=match.location_score,
                title_score=match.title_score,
                matched_skills=match.matched_skills,
                missing_skills=match.missing_skills,
                extra_skills=match.extra_skills,
                match_summary=match.match_summary,
            )

            if use_ai:
                score_response = await self.ai_integrator.enhance_score(
                    score_response, {}
                )

            matches.append(score_response)

        return matches, len(existing)

    async def compute_and_save_match(
        self,
        profile_id: int,
        job_id: int,
        profile_data: Optional[dict] = None,
        job_data: Optional[dict] = None,
        use_ai: bool = False,
    ) -> MatchScoreResponse:
        """Compute a match score and save it to the database."""
        request = MatchScoreRequest(
            profile_id=profile_id,
            job_id=job_id,
            profile_data=profile_data,
            job_data=job_data,
            use_ai_enhancement=use_ai,
        )

        score = await self.match_service.compute_score(request)

        if use_ai:
            score = await self.ai_integrator.enhance_score(
                score,
                {"profile_data": profile_data, "job_data": job_data},
            )

        await self.match_service.save_match(score)
        return score
