"""Webhook endpoints for email delivery status updates."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_session
from shared.schemas.common import APIResponse

from ...services.delivery_service import DeliveryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/delivery", response_model=APIResponse)
async def handle_delivery_webhook(
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """Generic delivery webhook endpoint.

    Accepts delivery status updates from email providers.
    Expected payload:
    {
        "message_id": "provider-message-id",
        "status": "delivered|opened|bounced|replied",
        "provider": "smtp|postal",
        "metadata": { ... }
    }
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    message_id = payload.get("message_id")
    status = payload.get("status")
    provider = payload.get("provider", "unknown")
    metadata = payload.get("metadata")

    if not message_id or not status:
        raise HTTPException(status_code=400, detail="message_id and status are required")

    valid_statuses = {"delivered", "opened", "bounced", "replied", "complained"}
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(sorted(valid_statuses))}")

    svc = DeliveryService(db)
    app = await svc.handle_delivery_webhook(
        message_id=message_id,
        status=status,
        provider=provider,
        metadata=metadata,
    )

    if not app:
        logger.warning("Webhook received for unknown message", message_id=message_id)
        return APIResponse(data={"status": "ignored", "reason": "Unknown message_id"})

    logger.info("Delivery webhook processed", message_id=message_id, status=status, application_id=app.id)
    return APIResponse(data={
        "status": "processed",
        "application_id": app.id,
        "new_status": app.delivery_status,
    })


@router.post("/gmail", response_model=APIResponse)
async def handle_gmail_webhook(
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """Gmail-specific delivery webhook (placeholder)."""
    # TODO: Parse Gmail Pub/Sub push notifications
    return await handle_delivery_webhook(request, db)


@router.post("/outlook", response_model=APIResponse)
async def handle_outlook_webhook(
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """Outlook-specific delivery webhook (placeholder)."""
    # TODO: Parse Outlook webhook format
    return await handle_delivery_webhook(request, db)
