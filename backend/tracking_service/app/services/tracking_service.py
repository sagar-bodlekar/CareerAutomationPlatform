"""Tracking service for application stats and timeline."""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.tracking import TrackingStats, FunnelData, DailyTrend

logger = logging.getLogger(__name__)


class TrackingService:
    """Service for querying application tracking data."""

    STATUS_FUNNEL_ORDER = [
        "draft", "matched", "resume_generated", "cover_letter_generated",
        "email_prepared", "sent", "delivered", "opened", "replied",
        "interview_scheduled", "offer_received", "rejected", "withdrawn",
    ]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_stats(self, profile_id: str) -> TrackingStats:
        """Get aggregate tracking stats for a profile."""
        # In production, query from application_stats table.
        # For now, compute from applications and events.
        from ..models.models import Application

        result = await self.db.execute(
            select(Application).where(Application.profile_id == profile_id)
        )
        apps = list(result.scalars().all())

        total = len(apps)
        sent = sum(1 for a in apps if a.status in ("sent", "delivered", "opened", "replied", "interview_scheduled"))
        delivered = sum(1 for a in apps if a.status in ("delivered", "opened", "replied", "interview_scheduled"))
        opened = sum(1 for a in apps if a.status in ("opened", "replied", "interview_scheduled"))
        replied = sum(1 for a in apps if a.status in ("replied", "interview_scheduled"))
        interviews = sum(1 for a in apps if a.status in ("interview_scheduled", "offer_received"))
        offers = sum(1 for a in apps if a.status == "offer_received")
        rejected = sum(1 for a in apps if a.status == "rejected")

        match_scores = [a.match_score for a in apps if a.match_score is not None]
        avg_score = sum(match_scores) / len(match_scores) if match_scores else None
        success_rate = (interviews / sent * 100) if sent > 0 else None

        return TrackingStats(
            total_applications=total,
            total_sent=sent,
            total_delivered=delivered,
            total_opened=opened,
            total_replied=replied,
            total_interviews=interviews,
            total_offers=offers,
            total_rejected=rejected,
            avg_match_score=round(avg_score, 1) if avg_score else None,
            success_rate=round(success_rate, 1) if success_rate else None,
        )

    async def get_funnel(self, profile_id: str) -> list[FunnelData]:
        """Get application funnel data (status distribution)."""
        from ..models.models import Application

        funnel = []
        total = 0

        for status in self.STATUS_FUNNEL_ORDER:
            result = await self.db.execute(
                select(func.count()).select_from(
                    select(Application).where(
                        Application.profile_id == profile_id,
                        Application.status == status,
                    ).subquery()
                )
            )
            count = result.scalar() or 0
            total += count
            funnel.append(FunnelData(
                status=status,
                label=status.replace("_", " ").title(),
                count=count,
            ))

        # Calculate percentages
        if total > 0:
            for item in funnel:
                item.percentage = round(item.count / total * 100, 1)

        return funnel

    async def get_daily_trends(
        self,
        profile_id: str,
        days: int = 30,
    ) -> list[DailyTrend]:
        """Get daily application counts for trend charts."""
        from ..models.models import Application

        cutoff = datetime.now(timezone.utc)
        trends = []

        for i in range(days - 1, -1, -1):
            from datetime import timedelta
            day = cutoff - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            result = await self.db.execute(
                select(func.count()).select_from(
                    select(Application).where(
                        Application.profile_id == profile_id,
                        Application.created_at >= day_start,
                        Application.created_at < day_end,
                    ).subquery()
                )
            )
            count = result.scalar() or 0

            sent_result = await self.db.execute(
                select(func.count()).select_from(
                    select(Application).where(
                        Application.profile_id == profile_id,
                        Application.sent_at >= day_start,
                        Application.sent_at < day_end,
                    ).subquery()
                )
            )
            sent_count = sent_result.scalar() or 0

            trends.append(DailyTrend(
                date=day_start.strftime("%Y-%m-%d"),
                count=count,
                sent_count=sent_count,
            ))

        return trends

    async def get_applications_list(
        self,
        profile_id: str,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list, int]:
        """Get paginated list of applications for tracking."""
        from ..models.models import Application

        query = select(Application).where(Application.profile_id == profile_id)
        if status:
            query = query.where(Application.status == status)

        # Count
        count_q = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_q)).scalar() or 0

        # Sort
        sort_col = getattr(Application, sort_by, Application.created_at)
        if sort_order == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(desc(sort_col))

        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        result = await self.db.execute(query)
        apps = list(result.scalars().all())

        return apps, total
