"""FastAPI dependencies for job service."""

from typing import Optional

from fastapi import Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_session

from ...services.dedup_service import DeduplicationService
from ...services.job_service import JobService
from ...services.scraper_service import ScraperService


async def get_job_service(db: AsyncSession = Depends(get_session)) -> JobService:
    """Dependency: Get JobService instance."""
    return JobService(db)


async def get_scraper_service(db: AsyncSession = Depends(get_session)) -> ScraperService:
    """Dependency: Get ScraperService instance."""
    return ScraperService(db)


async def get_dedup_service() -> DeduplicationService:
    """Dependency: Get DeduplicationService instance."""
    return DeduplicationService()


async def get_current_user_id(request: Request) -> Optional[int]:
    """Extract user_id from JWT token in request (placeholder for Phase 3 integration).

    In Phase 3 Auth Service integration, this will use the verify_token dependency.
    For now, returns None (unauthenticated).
    """
    # TODO: Phase 6 - integrate with Auth Service JWT middleware
    return None


async def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
) -> dict:
    """Get pagination query parameters."""
    return {"page": page, "per_page": per_page}
