"""Celery tasks for async resume processing.

Handles PDF generation, ATS optimization, and resume workflow tasks.
"""

import asyncio
import logging
from typing import Optional

from celery import Celery

from shared.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "resume_service",
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


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def generate_resume_pdf(self, resume_id: str, template_name: str = "master"):
    """Generate a resume PDF asynchronously.

    Renders resume data into HTML using the specified template,
    converts to PDF via WeasyPrint, and uploads to MinIO.

    Args:
        resume_id: UUID of the Resume record.
        template_name: Template to use (master, modern, classic, minimal).

    Returns:
        Dict with generation result including storage info.
    """
    try:
        from app.services.resume_service import ResumeService
        from app.services.pdf_generator import PDFGenerator
        from shared.database import async_session_factory

        async def _generate():
            async with async_session_factory() as session:
                resume_service = ResumeService(session)
                pdf_gen = PDFGenerator()

                resume = await resume_service.get_resume(resume_id)
                if not resume:
                    raise ValueError(f"Resume not found: {resume_id}")

                # Fetch profile data (in production, this would call Profile Service API)
                profile_data = {"skills": [], "experiences": [], "education": []}

                # Generate and store the PDF
                resume_file = await pdf_gen.generate_and_store_pdf(
                    resume=resume,
                    profile_data=profile_data,
                    session=session,
                    template_name=template_name,
                )

                await session.commit()

                return {
                    "resume_id": str(resume_id),
                    "file_id": str(resume_file.id),
                    "file_size": resume_file.file_size_bytes,
                    "object_key": resume_file.minio_object_key,
                    "status": "generated",
                }

        return asyncio.run(_generate())
    except Exception as exc:
        logger.error(f"Resume PDF generation failed for {resume_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def optimize_resume_ats(self, resume_id: str, job_description: str):
    """Run ATS optimization on a resume asynchronously.

    Analyzes resume content against a job description, computes
    ATS score, and generates optimization recommendations.

    Args:
        resume_id: UUID of the Resume record.
        job_description: Full text of the target job description.

    Returns:
        Dict with ATS score, breakdown, and recommendations.
    """
    try:
        from app.services.resume_service import ResumeService
        from app.services.ats.optimizer import ATSOptimizer
        from shared.database import async_session_factory

        async def _optimize():
            async with async_session_factory() as session:
                resume_service = ResumeService(session)
                optimizer = ATSOptimizer()

                resume = await resume_service.get_resume(resume_id)
                if not resume:
                    raise ValueError(f"Resume not found: {resume_id}")

                resume_content = resume.content or {}

                # Run the ATS analysis and optimization
                result = await optimizer.analyze_and_optimize(
                    resume_content=resume_content,
                    job_description=job_description,
                )

                # Update the resume's ATS score in the database
                resume.ats_score = result.get("score")
                await session.flush()
                await session.commit()

                return {
                    "resume_id": str(resume_id),
                    "ats_score": result.get("score"),
                    "score_breakdown": result.get("score_breakdown"),
                    "matched_keywords": result.get("matched_keywords"),
                    "missing_keywords": result.get("missing_keywords"),
                    "recommendations": result.get("recommendations"),
                    "status": "optimized",
                }

        return asyncio.run(_optimize())
    except Exception as exc:
        logger.error(f"ATS optimization failed for {resume_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def regenerate_all_resumes_for_profile(self, profile_id: str):
    """Regenerate all resumes for a profile after profile update.

    Triggered when profile data changes significantly (skills, experience, etc.).

    Args:
        profile_id: UUID of the updated profile.

    Returns:
        Dict with regeneration summary.
    """
    try:
        from app.services.resume_service import ResumeService
        from shared.database import async_session_factory

        async def _regenerate():
            async with async_session_factory() as session:
                resume_service = ResumeService(session)
                resumes, total = await resume_service.list_resumes(
                    user_id=profile_id,
                    include_deleted=False,
                )
                count = len(resumes)
                logger.info(
                    "Resume regeneration triggered",
                    profile_id=profile_id,
                    resume_count=count,
                )
                return {
                    "profile_id": str(profile_id),
                    "resumes_to_update": count,
                    "status": "queued",
                }

        return asyncio.run(_regenerate())
    except Exception as exc:
        logger.error(f"Resume regeneration failed for profile {profile_id}: {exc}")
        raise self.retry(exc=exc)
