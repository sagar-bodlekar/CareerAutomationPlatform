"""Celery tasks for job scraping."""

import asyncio
import logging

from celery import Celery

from shared.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "job_service",
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
    "scrape-remoteok-every-60-minutes": {
        "task": "app.tasks.scrape_jobs",
        "schedule": 60 * 60,  # Every 60 minutes
        "args": ("remoteok",),
    },
    "scrape-naukri-every-120-minutes": {
        "task": "app.tasks.scrape_jobs",
        "schedule": 120 * 60,  # Every 120 minutes
        "args": ("naukri",),
    },
    "scrape-wellfound-every-120-minutes": {
        "task": "app.tasks.scrape_jobs",
        "schedule": 120 * 60,  # Every 120 minutes
        "args": ("wellfound",),
    },
    "scrape-linkedin-every-60-minutes": {
        "task": "app.tasks.scrape_jobs",
        "schedule": 60 * 60,  # Every 60 minutes
        "args": ("linkedin",),
    },
    "refresh-all-sources-every-6-hours": {
        "task": "app.tasks.refresh_all_sources",
        "schedule": 6 * 60 * 60,  # Every 6 hours
    },
}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def scrape_jobs(self, source_name: str, config: dict | None = None):
    """Scrape jobs from a single source."""
    try:
        from .services.scraper_service import ScraperService
        from shared.database import async_session_factory

        async def _scrape():
            async with async_session_factory() as session:
                service = ScraperService(session)
                try:
                    result = await service.scrape_source(
                        source_name,
                        config=config,
                        save=True,
                    )
                    return {
                        "source": source_name,
                        "found": result.total_found,
                        "new": result.total_new,
                        "duplicates": result.total_duplicates,
                        "errors": result.total_errors,
                        "success": result.success,
                    }
                finally:
                    await service.close()

        return asyncio.run(_scrape())
    except Exception as exc:
        logger.error(f"Scrape task failed for {source_name}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=600)
def refresh_all_sources(self):
    """Scrape all active sources."""
    try:
        from .services.scraper_service import ScraperService
        from shared.database import async_session_factory

        async def _refresh_all():
            async with async_session_factory() as session:
                service = ScraperService(session)
                try:
                    results = await service.scrape_all_active()
                    summary = {}
                    for name, result in results.items():
                        summary[name] = {
                            "found": result.total_found,
                            "new": result.total_new,
                            "errors": result.total_errors,
                            "success": result.success,
                        }
                    return {"sources": summary}
                finally:
                    await service.close()

        return asyncio.run(_refresh_all())
    except Exception as exc:
        logger.error(f"Refresh all sources failed: {exc}")
        raise self.retry(exc=exc)
