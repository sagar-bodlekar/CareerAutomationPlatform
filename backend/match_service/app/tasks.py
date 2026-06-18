"""Celery tasks for match service."""

import asyncio
import logging

from celery import Celery

from shared.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "match_service",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# ─── Celery Beat Schedule ──────────────────────────────────

celery_app.conf.beat_schedule = {
    "compute-matches-for-new-jobs-every-15-minutes": {
        "task": "app.tasks.compute_new_job_matches",
        "schedule": 15 * 60,  # Every 15 minutes
    },
    "compute-matches-for-new-profiles-every-30-minutes": {
        "task": "app.tasks.compute_new_profile_matches",
        "schedule": 30 * 60,  # Every 30 minutes
    },
}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def compute_match_score(self, profile_id: int, job_id: int, use_ai: bool = False):
    """Compute and save a match score for a profile+job combination.

    Args:
        profile_id: User profile ID.
        job_id: Job ID from Job Service.
        use_ai: Whether to use AI-enhanced matching.

    Returns:
        Dict with match results.
    """
    try:
        from .services.batch_matcher import BatchMatcher
        from shared.database import async_session_factory

        async def _compute():
            async with async_session_factory() as session:
                matcher = BatchMatcher(session)
                result = await matcher.compute_and_save_match(
                    profile_id=profile_id,
                    job_id=job_id,
                    use_ai=use_ai,
                )
                return {
                    "match_id": result.match_id,
                    "profile_id": result.profile_id,
                    "job_id": result.job_id,
                    "overall_score": result.overall_score,
                    "matched_skills": result.matched_skills,
                    "missing_skills": result.missing_skills,
                    "ai_enhanced": result.ai_enhanced,
                }

        return asyncio.run(_compute())
    except Exception as exc:
        logger.error(
            "Match score computation failed",
            profile_id=profile_id,
            job_id=job_id,
            error=str(exc),
        )
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def compute_batch_matches(self, profile_id: int | None = None, job_id: int | None = None, limit: int = 20, use_ai: bool = False):
    """Compute matches in batch for a profile or job.

    Args:
        profile_id: If set, matches this profile against all active jobs.
        job_id: If set, matches this job against all active profiles.
        limit: Maximum matches to compute.
        use_ai: Whether to use AI-enhanced matching.

    Returns:
        Dict with batch match summary.
    """
    try:
        from .schemas.match import BatchMatchRequest
        from .services.batch_matcher import BatchMatcher
        from shared.database import async_session_factory

        async def _compute_batch():
            async with async_session_factory() as session:
                matcher = BatchMatcher(session)
                request = BatchMatchRequest(
                    profile_id=profile_id,
                    job_id=job_id,
                    limit=limit,
                    use_ai_enhancement=use_ai,
                )
                result = await matcher.process_batch(request)
                return {
                    "total_matched": result.total_matched,
                    "total_processed": result.total_processed,
                    "ai_enhanced": result.ai_enhanced,
                }

        return asyncio.run(_compute_batch())
    except Exception as exc:
        logger.error(
            "Batch match computation failed",
            profile_id=profile_id,
            job_id=job_id,
            error=str(exc),
        )
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def compute_new_job_matches(self):
    """Find and match all active profiles against newly scraped jobs.

    Orchestration task triggered periodically by Celery Beat.
    When cross-service wiring is complete, this will:
    1. Query for jobs scraped since last match run
    2. Iterate active profiles and call `compute_match_score` for each
    3. Trigger notifications for high-score matches

    Currently logs the heartbeat. Real matching is handled by
    the compute_match_score and compute_batch_matches tasks.
    """
    logger.info("New job match computation triggered (heartbeat)")
    return {"status": "completed", "message": "Heartbeat — ready for cross-service orchestration wiring"}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def compute_new_profile_matches(self):
    """Find and match all active jobs against a newly created profile.

    Orchestration task triggered periodically by Celery Beat.
    When cross-service wiring is complete, this will:
    1. Query for profiles created since last match run
    2. Iterate active jobs and call `compute_match_score` for each
    3. Trigger notifications for high-score matches

    Currently logs the heartbeat.
    """
    logger.info("New profile match computation triggered (heartbeat)")
    return {"status": "completed", "message": "Heartbeat — ready for cross-service orchestration wiring"}
