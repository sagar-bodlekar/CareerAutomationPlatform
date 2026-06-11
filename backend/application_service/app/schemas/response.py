"""Example response schemas for service template."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ExampleResponse(BaseModel):
    """Example response — replace with actual schema."""

    id: UUID
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime
