"""Event service for application audit trail."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import ApplicationEvent


class EventService:
    """Service for creating and querying application events."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_event(
        self,
        application_id: int,
        to_status: str,
        from_status: Optional[str] = None,
        event_type: str = "status_change",
        description: Optional[str] = None,
        actor: str = "system",
        metadata_json: Optional[dict] = None,
    ) -> ApplicationEvent:
        """Create a new application event."""
        event = ApplicationEvent(
            application_id=application_id,
            from_status=from_status,
            to_status=to_status,
            event_type=event_type,
            description=description,
            actor=actor,
            metadata_json=metadata_json,
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def get_events(
        self,
        application_id: int,
        limit: int = 50,
    ) -> list[ApplicationEvent]:
        """Get events for an application."""
        result = await self.db.execute(
            select(ApplicationEvent)
            .where(ApplicationEvent.application_id == application_id)
            .order_by(ApplicationEvent.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
