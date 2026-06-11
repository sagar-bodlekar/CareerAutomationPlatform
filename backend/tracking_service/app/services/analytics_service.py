"""Analytics service for computing detailed stats, source breakdown, and response times."""

import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.analytics import AnalyticsResponse, SourceBreakdown

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for computing detailed application analytics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_analytics(self, profile_id: int) -> AnalyticsResponse:
        """Get comprehensive analytics for a profile."""
        from ..models.models import Application

        # Total applications
        total_result = await self.db.execute(
            select(func.count()).select_from(
                select(Application).where(Application.profile_id == profile_id).subquery()
            )
        )
        total = total_result.scalar() or 0

        # Source breakdown (job_id -> count)
        result = await self.db.execute(
            select(Application.job_id, func.count())
            .where(Application.profile_id == profile_id)
            .group_by(Application.job_id)
            .limit(10)
        )
        source_data = result.all()

        # Funnel data
        funnel = []
        statuses = ["draft", "sent", "delivered", "opened", "replied", "interview_scheduled", "offer_received", "rejected"]
        for status in statuses:
            count_result = await self.db.execute(
                select(func.count()).select_from(
                    select(Application).where(
                        Application.profile_id == profile_id,
                        Application.status == status,
                    ).subquery()
                )
            )
            count = count_result.scalar() or 0
            if count > 0:
                funnel.append({
                    "status": status,
                    "label": status.replace("_", " ").title(),
                    "count": count,
                    "percentage": round(count / total * 100, 1) if total > 0 else 0,
                })

        # Daily trends (last 30 days)
        from datetime import datetime, timedelta, timezone
        daily_trends = []
        cutoff = datetime.now(timezone.utc)
        for i in range(29, -1, -1):
            day = cutoff - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            day_count = (await self.db.execute(
                select(func.count()).select_from(
                    select(Application).where(
                        Application.profile_id == profile_id,
                        Application.created_at >= day_start,
                        Application.created_at < day_end,
                    ).subquery()
                )
            )).scalar() or 0

            sent_count = (await self.db.execute(
                select(func.count()).select_from(
                    select(Application).where(
                        Application.profile_id == profile_id,
                        Application.sent_at >= day_start,
                        Application.sent_at < day_end,
                    ).subquery()
                )
            )).scalar() or 0

            daily_trends.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "count": day_count,
                "sent_count": sent_count,
            })

        # Response rate
        sent_total = (await self.db.execute(
            select(func.count()).select_from(
                select(Application).where(
                    Application.profile_id == profile_id,
                    Application.status.in_(["replied", "interview_scheduled", "offer_received"]),
                ).subquery()
            )
        )).scalar() or 0

        all_sent = (await self.db.execute(
            select(func.count()).select_from(
                select(Application).where(
                    Application.profile_id == profile_id,
                    Application.sent_at.isnot(None),
                ).subquery()
            )
        )).scalar() or 0

        response_rate = round(sent_total / all_sent * 100, 1) if all_sent > 0 else None

        return AnalyticsResponse(
            total_applications=total,
            funnel=funnel,
            daily_trends=daily_trends,
            source_breakdown=[],
            response_rate=response_rate,
        )
