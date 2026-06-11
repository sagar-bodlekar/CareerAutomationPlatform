"""Delivery service for sending application emails."""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.config import settings

from ..models.models import Application, ApplicationEvent
from .email.base_provider import EmailProvider, DeliveryResult
from .email.smtp_provider import SMTPProvider
from .email.postal_provider import PostalProvider
from .event_service import EventService

logger = logging.getLogger(__name__)


class DeliveryService:
    """Service for delivering application emails with retry logic."""

    MAX_RETRIES = 5
    BACKOFF_BASE = 60  # seconds

    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_service = EventService(db)
        self._provider: Optional[EmailProvider] = None

    def _get_provider(self) -> EmailProvider:
        """Get the configured email provider.

        Defaults to SMTP. If Postal API URL is configured, uses Postal.
        """
        if self._provider is None:
            if settings.smtp_host and settings.smtp_port:
                self._provider = SMTPProvider()
            if getattr(settings, "postal_api_url", None):
                self._provider = PostalProvider(
                    api_url=settings.postal_api_url,
                    api_key=settings.postal_api_key,
                )
        return self._provider

    async def send_application(
        self,
        application: Application,
        resume_attachment: Optional[dict] = None,
        cover_letter_body: Optional[str] = None,
    ) -> DeliveryResult:
        """Send an application email with optional resume attachment.

        Args:
            application: The application record.
            resume_attachment: Optional MIME attachment dict for resume PDF.
            cover_letter_body: Optional cover letter text to include.

        Returns:
            DeliveryResult from the provider.
        """
        provider = self._get_provider()

        # Build email
        to_address = getattr(application, "recipient_email", None) or "hiring@example.com"
        subject = f"Application for {application.job_title or 'position'}"

        body_parts = [f"Dear Hiring Manager,\n"]
        if cover_letter_body:
            body_parts.append(cover_letter_body)
        else:
            body_parts.append(
                f"I am writing to apply for the {application.job_title} position "
                f"at {application.company_name}. Please find my resume attached.\n"
            )
        body_parts.append(f"\nBest regards,\n{getattr(application, 'candidate_name', 'Candidate')}")
        body = "\n\n".join(body_parts)

        attachments = []
        if resume_attachment:
            attachments.append(resume_attachment)

        # Send
        result = await provider.send_email(
            to_address=to_address,
            subject=subject,
            body=body,
            attachments=attachments or None,
        )

        # Log delivery attempt
        if result.success:
            application.delivery_status = "sent"
            application.delivery_message_id = result.message_id
            application.sent_at = __import__("datetime").datetime.now()
            await self.event_service.create_event(
                application_id=application.id,
                to_status="sent",
                from_status=application.status,
                event_type="email_sent",
                description=f"Email sent via {result.provider}",
                actor="system",
                metadata_json={
                    "provider": result.provider,
                    "message_id": result.message_id,
                    "to": to_address,
                },
            )
        else:
            application.last_error = result.error_message
            application.retry_count = (application.retry_count or 0) + 1
            await self.event_service.create_event(
                application_id=application.id,
                to_status=application.status,
                event_type="delivery_failed",
                description=f"Delivery failed: {result.error_message}",
                actor="system",
                metadata_json={"provider": result.provider, "error": result.error_message},
            )

        await self.db.flush()
        return result

    async def retry_delivery(self, application: Application) -> DeliveryResult:
        """Retry a failed delivery with exponential backoff.

        Args:
            application: The application with failed delivery.

        Returns:
            DeliveryResult from the retry attempt.
        """
        if application.retry_count >= self.MAX_RETRIES:
            logger.warning("Max retries reached", application_id=application.id)
            return DeliveryResult(
                success=False,
                provider="retry",
                error_message="Max retries exceeded",
            )

        # Exponential backoff
        import asyncio
        delay = self.BACKOFF_BASE * (2 ** (application.retry_count or 0))
        logger.info("Retrying delivery", application_id=application.id, attempt=application.retry_count + 1, delay=delay)
        await asyncio.sleep(delay)

        return await self.send_application(application)

    async def handle_delivery_webhook(
        self,
        message_id: str,
        status: str,
        provider: str = "unknown",
        metadata: Optional[dict] = None,
    ) -> Optional[Application]:
        """Handle a delivery webhook from the email provider.

        Args:
            message_id: Provider message ID.
            status: Delivery status (delivered, opened, bounced, replied).
            provider: Provider name.
            metadata: Optional additional metadata.

        Returns:
            Updated Application or None if not found.
        """
        result = await self.db.execute(
            select(Application).where(Application.delivery_message_id == message_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            logger.warning("Webhook received for unknown message", message_id=message_id)
            return None

        status_map = {
            "delivered": "delivered",
            "opened": "opened",
            "bounced": "bounced",
            "replied": "replied",
            "complained": "bounced",
        }

        new_status = status_map.get(status)
        if new_status:
            app.delivery_status = new_status
            await self.event_service.create_event(
                application_id=app.id,
                to_status=new_status,
                from_status=app.status,
                event_type=f"email_{new_status}",
                description=f"Email {new_status} via {provider} webhook",
                actor="webhook",
                metadata_json={"provider": provider, "webhook_status": status, **(metadata or {})},
            )
            await self.db.flush()

        return app
