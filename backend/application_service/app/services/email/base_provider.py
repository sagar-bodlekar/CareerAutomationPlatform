"""Abstract base class for email providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class DeliveryResult:
    """Result of an email delivery attempt."""

    success: bool
    message_id: Optional[str] = None
    provider: str = "unknown"
    status_code: Optional[str] = None
    error_message: Optional[str] = None


class EmailProvider(ABC):
    """Abstract interface for email delivery providers."""

    @abstractmethod
    async def send_email(
        self,
        to_address: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[list[dict]] = None,
        from_address: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> DeliveryResult:
        """Send an email.

        Args:
            to_address: Recipient email address.
            subject: Email subject line.
            body: Plain text body.
            html_body: Optional HTML body.
            attachments: Optional list of attachment dicts with keys:
                filename, content (base64), content_type.
            from_address: Optional sender address (default from config).
            from_name: Optional sender name.

        Returns:
            DeliveryResult with status and message ID.
        """
        ...

    @abstractmethod
    async def check_delivery_status(self, message_id: str) -> DeliveryResult:
        """Check the delivery status of a previously sent message.

        Args:
            message_id: Provider message ID.

        Returns:
            Updated DeliveryResult.
        """
        ...
