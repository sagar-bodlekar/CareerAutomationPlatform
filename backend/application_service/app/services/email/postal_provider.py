"""Postal (self-hosted) email provider."""

import logging
from typing import Optional

import httpx

from .base_provider import EmailProvider, DeliveryResult

logger = logging.getLogger(__name__)


class PostalProvider(EmailProvider):
    """Self-hosted Postal transactional email server provider.

    Requires a running Postal server with API access.
    See: https://docs.postalserver.io/
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        self.api_url = (api_url or "").rstrip("/")
        self.api_key = api_key or ""
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.api_url,
                timeout=self.timeout,
                headers={
                    "X-Server-API-Key": self.api_key,
                    "Content-Type": "application/json",
                },
            )
        return self._client

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
        """Send email via Postal API."""
        try:
            client = await self._get_client()

            payload = {
                "to": [to_address],
                "subject": subject,
                "plain_body": body,
                "from": from_address or "noreply@career-platform.local",
            }

            if from_name:
                payload["sender"] = f"{from_name} <{payload['from']}>"

            if html_body:
                payload["html_body"] = html_body

            if attachments:
                payload["attachments"] = [
                    {
                        "filename": a["filename"],
                        "content": a["content"],
                        "content_type": a.get("content_type", "application/octet-stream"),
                    }
                    for a in attachments
                ]

            response = await client.post("/api/v1/send/email", json=payload)
            data = response.json()

            if response.status_code == 200 and data.get("status") == "ok":
                message_id = data.get("id") or data.get("message_id", "")
                logger.info("Email sent via Postal", to=to_address, message_id=message_id)
                return DeliveryResult(
                    success=True,
                    provider="postal",
                    message_id=str(message_id),
                    status_code="sent",
                )
            else:
                error = data.get("error", {}).get("message", str(response.text))
                logger.error("Postal delivery failed", error=error, status=response.status_code)
                return DeliveryResult(
                    success=False,
                    provider="postal",
                    error_message=error,
                    status_code=str(response.status_code),
                )

        except Exception as e:
            logger.error("Postal provider error", error=str(e))
            return DeliveryResult(
                success=False,
                provider="postal",
                error_message=str(e),
            )

    async def check_delivery_status(self, message_id: str) -> DeliveryResult:
        """Check delivery status via Postal API."""
        try:
            client = await self._get_client()
            response = await client.get(f"/api/v1/send/status/{message_id}")
            data = response.json()

            if response.status_code == 200:
                status = data.get("status", "unknown")
                return DeliveryResult(
                    success=status in ("sent", "delivered"),
                    provider="postal",
                    message_id=message_id,
                    status_code=status,
                )
            return DeliveryResult(
                success=False,
                provider="postal",
                message_id=message_id,
                error_message="Failed to check status",
            )

        except Exception as e:
            return DeliveryResult(
                success=False,
                provider="postal",
                error_message=str(e),
            )
