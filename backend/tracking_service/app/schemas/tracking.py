"""Tracking schemas for stats, funnel, and daily trends."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TrackingStats(BaseModel):
    """Aggregate tracking statistics for a user."""

    total_applications: int = 0
    total_sent: int = 0
    total_delivered: int = 0
    total_opened: int = 0
    total_replied: int = 0
    total_interviews: int = 0
    total_offers: int = 0
    total_rejected: int = 0
    avg_match_score: Optional[float] = None
    avg_response_time_hours: Optional[float] = None
    success_rate: Optional[float] = None
    last_activity_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class FunnelData(BaseModel):
    """Application funnel with status breakdown."""

    status: str
    label: str
    count: int
    percentage: float = 0.0


class DailyTrend(BaseModel):
    """Daily application count for trend charts."""

    date: str
    count: int = 0
    sent_count: int = 0
    interview_count: int = 0
    offer_count: int = 0
