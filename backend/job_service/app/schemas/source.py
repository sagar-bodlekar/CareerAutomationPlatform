"""Job source schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JobSourceCreate(BaseModel):
    """Create a new job source configuration."""

    name: str = Field(..., min_length=1, max_length=100)
    source_type: str = Field(..., description="api, rss, scrape, manual, aggregator")
    display_name: str = Field(..., min_length=1, max_length=255)
    base_url: str = Field(..., min_length=1, max_length=500)
    api_url: Optional[str] = None
    api_key_required: bool = False
    is_active: bool = True
    scrape_interval_minutes: int = Field(60, ge=1, le=1440)
    config: Optional[dict] = None
    priority: int = 100


class JobSourceUpdate(BaseModel):
    """Update an existing job source."""

    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    base_url: Optional[str] = Field(None, min_length=1, max_length=500)
    api_url: Optional[str] = None
    api_key_required: Optional[bool] = None
    is_active: Optional[bool] = None
    scrape_interval_minutes: Optional[int] = Field(None, ge=1, le=1440)
    config: Optional[dict] = None
    priority: Optional[int] = None


class JobSourceResponse(BaseModel):
    """Job source configuration response."""

    id: int
    name: str
    source_type: str
    display_name: str
    base_url: str
    api_url: Optional[str] = None
    api_key_required: bool = False
    is_active: bool = True
    scrape_interval_minutes: int = 60
    config: Optional[dict] = None
    last_scraped_at: Optional[datetime] = None
    last_scrape_status: Optional[str] = None
    last_scrape_count: Optional[int] = None
    error_count: int = 0
    priority: int = 100
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
