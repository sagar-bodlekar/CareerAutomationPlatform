"""Tracking service dependencies."""

from typing import Optional

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_session

from ...services.tracking_service import TrackingService
from ...services.analytics_service import AnalyticsService
from ...services.export_service import ExportService


async def get_tracking_service(db: AsyncSession = Depends(get_session)) -> TrackingService:
    return TrackingService(db)


async def get_analytics_service(db: AsyncSession = Depends(get_session)) -> AnalyticsService:
    return AnalyticsService(db)


async def get_export_service(db: AsyncSession = Depends(get_session)) -> ExportService:
    return ExportService(db)


async def get_current_user_id(request: Request) -> Optional[str]:
    return None
