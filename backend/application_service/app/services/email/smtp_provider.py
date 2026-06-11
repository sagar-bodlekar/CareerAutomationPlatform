"""SMTP email provider using smtplib."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import formataddr
from typing import Optional

from shared.config import settings

from .base_provider import EmailProvider, DeliveryResult

logger = logging.getLogger(__name__)


class SMTPProvider(EmailProvider):
    """Direct SMTP email delivery."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
    ):
        self.host = host or settings.smtp_host
        self.port = port or settings.smtp_port
        self.username = username or settings.smtp_user
        self.password = password or settings.smtp_password
        self.use_tls = use_tls

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
        """Send email via SMTP."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = formataddr(
                (from_name or settings.smtp_from_name, from_address or settings.smtp_from_email)
            )
            msg["To"] = to_address

            # Plain text part
            msg.attach(MIMEText(body, "plain"))

            # HTML part
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            # Attachments
            if attachments:
                for att in attachments:
                    part = MIMEBase("application", "octet-stream")
                    import base64
                    part.set_payload(base64.b64decode(att["content"]))
                    from email import encoders
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f'attachment; filename="{att["filename"]}"',
                    )
                    msg.attach(part)

            # Send
            import asyncio

            def _send():
                with smtplib.SMTP(self.host, self.port) as server:
                    if self.use_tls:
                        server.starttls()
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    server.send_message(msg)

            await asyncio.to_thread(_send)

            logger.info("Email sent via SMTP", to=to_address, subject=subject)
            return DeliveryResult(
                success=True,
                provider="smtp",
                message_id=f"smtp-{abs(hash(subject + to_address))}",
            )

        except Exception as e:
            logger.error("SMTP delivery failed", error=str(e), to=to_address)
            return DeliveryResult(
                success=False,
                provider="smtp",
                error_message=str(e),
            )

    async def check_delivery_status(self, message_id: str) -> DeliveryResult:
        """SMTP doesn't support delivery status checks natively."""
        return DeliveryResult(
            success=True,
            provider="smtp",
            message_id=message_id,
            status_code="unknown",
        )
