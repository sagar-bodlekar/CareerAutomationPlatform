"""Match service dependencies."""

from typing import Optional

from fastapi import Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_session

from ...services.batch_matcher import BatchMatcher
from ...services.match_service import MatchService


async def get_match_service(db: AsyncSession = Depends(get_session)) -> MatchService:
    return MatchService(db)


async def get_batch_matcher(db: AsyncSession = Depends(get_session)) -> BatchMatcher:
    return BatchMatcher(db)


async def get_current_user_id(request: Request) -> Optional[int]:
    # TODO: Phase 6 - integrate with Auth Service JWT middleware
    return None


async def get_pagination(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict:
    return {"page": page, "per_page": per_page}
