"""Delivery logging service for tracking email delivery attempts."""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class DeliveryLogger:
    """Logs and queries delivery attempts for audit and tracking."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_attempt(
        self,
        application_id: int,
        provider: str,
        to_address: str,
        subject: str,
        success: bool,
        message_id: Optional[str] = None,
        status_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> dict:
        """Log a delivery attempt to the database.

        Args:
            application_id: Application ID.
            provider: Provider name (smtp, postal).
            to_address: Recipient email.
            subject: Email subject.
            success: Whether delivery succeeded.
            message_id: Provider message ID.
            status_code: Provider status code.
            error_message: Error message if failed.

        Returns:
            Dict with log entry data.
        """
        # In production, this would store to an email_delivery_logs table.
        # For now, return structured log data for event tracking.
        log_entry = {
            "application_id": application_id,
            "provider": provider,
            "to_address": to_address,
            "subject": subject,
            "success": success,
            "message_id": message_id,
            "status_code": status_code,
            "error_message": error_message,
            "attempted_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.info("Delivery attempt logged", **log_entry)
        return log_entry

    async def get_delivery_history(self, application_id: int) -> list[dict]:
        """Get delivery history for an application.

        Args:
            application_id: Application ID.

        Returns:
            List of delivery log entries.
        """
        # In production, query from email_delivery_logs table.
        # For now, return application events.
        from sqlalchemy import select, desc
        from ..models.models import ApplicationEvent

        result = await self.db.execute(
            select(ApplicationEvent)
            .where(
                ApplicationEvent.application_id == application_id,
                ApplicationEvent.event_type.in_(["email_sent", "delivery_failed", "email_delivered", "email_opened"]),
            )
            .order_by(desc(ApplicationEvent.created_at))
            .limit(50)
        )
        events = list(result.scalars().all())
        return [
            {
                "event_type": e.event_type,
                "description": e.description,
                "actor": e.actor,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in events
        ]
