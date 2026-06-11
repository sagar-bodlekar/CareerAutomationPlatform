"""Application event schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ApplicationEventResponse(BaseModel):
    """Application event/audit trail response."""

    id: int
    application_id: int
    from_status: Optional[str] = None
    to_status: str
    event_type: str
    description: Optional[str] = None
    actor: str = "system"
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
