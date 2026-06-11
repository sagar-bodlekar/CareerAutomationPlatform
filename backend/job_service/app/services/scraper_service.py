"""Scraper service - orchestrates scraping, normalization, and deduplication."""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..scrapers import SCRAPER_REGISTRY, JobScraper, ScrapeResult
from ..scrapers.base import ScrapeError
from .dedup_service import DeduplicationService
from .job_service import JobService
from .normalizer import JobNormalizer

logger = logging.getLogger(__name__)


class ScraperService:
    """Orchestrates job scraping from configured sources.

    Coordinates: scraper selection -> fetch -> normalize -> dedup -> store.
    """

    def __init__(
        self,
        db: AsyncSession,
        dedup_service: Optional[DeduplicationService] = None,
    ):
        self.db = db
        self.job_service = JobService(db)
        self.normalizer = JobNormalizer()
        self.dedup = dedup_service or DeduplicationService()

    def get_scraper(self, source_name: str, config: Optional[dict] = None) -> Optional[JobScraper]:
        """Get a scraper instance by source name."""
        scraper_cls = SCRAPER_REGISTRY.get(source_name.lower())
        if not scraper_cls:
            return None
        return scraper_cls(config=config or {})

    async def scrape_source(
        self,
        source_name: str,
        config: Optional[dict] = None,
        save: bool = True,
    ) -> ScrapeResult:
        """Scrape a single source and optionally save results.

        Args:
            source_name: Name of the scraper to use.
            config: Optional config dict passed to scraper.
            save: Whether to save jobs to database.

        Returns:
            ScrapeResult with scrape stats.
        """
        scraper = self.get_scraper(source_name, config)
        if not scraper:
            raise ValueError(f"Unknown scraper source: {source_name}")

        try:
            result = await scraper.scrape()
        finally:
            await scraper.close()

        if not result.success or not result.jobs:
            return result

        # Normalize
        normalized = self.normalizer.normalize_batch(result.jobs)

        # Deduplicate
        new_jobs, dup_count = await self.dedup.filter_new(normalized, source=source_name)
        result.total_duplicates = dup_count
        result.total_new = len(new_jobs)

        if save and new_jobs:
            # Store jobs
            for job_data in new_jobs:
                try:
                    from ..schemas.job import JobCreate
                    data = JobCreate(**job_data)
                    await self.job_service.upsert_job(data)
                except Exception as e:
                    logger.warning(f"Failed to save job from {source_name}: {e}")
                    result.total_errors += 1
                    result.errors.append(str(e))
                    continue

            # Mark as seen
            await self.dedup.mark_batch_seen(new_jobs, source=source_name)
            result.total_new = len(new_jobs)

        return result

    async def scrape_all_active(self, db_session_factory=None) -> dict[str, ScrapeResult]:
        """Scrape all active sources.

        Returns:
            Dict mapping source_name -> ScrapeResult.
        """
        from sqlalchemy.ext.asyncio import AsyncSession

        sources = await self.job_service.list_sources(active_only=True)
        results = {}

        for source in sources:
            config = source.config or {}
            config.update({
                "name": source.name,
                "base_url": source.base_url,
                "api_url": source.api_url,
            })

            try:
                result = await self.scrape_source(source.name, config=config, save=True)
                results[source.name] = result
                logger.info(
                    "Scrape complete for %s: found=%d new=%d dup=%d errors=%d",
                    source.name,
                    result.total_found,
                    result.total_new,
                    result.total_duplicates,
                    result.total_errors,
                )
            except Exception as e:
                logger.error(f"Scrape failed for {source.name}: {e}")
                results[source.name] = ScrapeResult(
                    source_name=source.name,
                    success=False,
                    errors=[str(e)],
                )

        return results

    async def close(self) -> None:
        """Clean up resources."""
        await self.dedup.close()
