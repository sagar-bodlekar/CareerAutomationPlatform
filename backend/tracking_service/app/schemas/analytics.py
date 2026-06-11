"""Analytics schemas for detailed reporting."""

from typing import Optional

from pydantic import BaseModel, Field


class SourceBreakdown(BaseModel):
    """Breakdown of applications by source/job board."""

    source: str
    count: int = 0
    interview_count: int = 0
    offer_count: int = 0
    success_rate: Optional[float] = None


class AnalyticsResponse(BaseModel):
    """Detailed analytics response."""

    total_applications: int = 0
    funnel: list[dict] = Field(default_factory=list)
    daily_trends: list[dict] = Field(default_factory=list)
    source_breakdown: list[SourceBreakdown] = Field(default_factory=list)
    avg_response_time: Optional[float] = None
    response_rate: Optional[float] = None
