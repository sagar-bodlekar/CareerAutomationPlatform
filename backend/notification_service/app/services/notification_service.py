"""Notification service for managing in-app notifications."""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as redis

from shared.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing user notifications.

    Supports in-app notifications via Redis pub-sub and stores
    notification history for retrieval.
    """

    NOTIFICATION_CHANNEL = "notifications"

    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def _get_redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.from_url(settings.redis_url, decode_responses=True)
        return self._redis

    async def send_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[dict] = None,
    ) -> dict:
        """Send a notification to a user.

        Publishes to Redis pub-sub and stores in history.

        Args:
            user_id: Target user ID.
            notification_type: Type (application_status, job_match, etc.).
            title: Notification title.
            message: Notification body.
            data: Optional metadata payload.

        Returns:
            Dict with notification data.
        """
        notification = {
            "id": abs(hash(f"{user_id}-{datetime.now(timezone.utc).isoformat()}")),
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            r = await self._get_redis()

            # Store in user's notification list (keep last 100)
            key = f"user:{user_id}:notifications"
            await r.lpush(key, json.dumps(notification))
            await r.ltrim(key, 0, 99)

            # Publish for real-time delivery
            await r.publish(
                f"{self.NOTIFICATION_CHANNEL}:{user_id}",
                json.dumps(notification),
            )

            logger.info("Notification sent", user_id=user_id, type=notification_type)
        except Exception as e:
            logger.error("Failed to send notification", error=str(e))

        return notification

    async def get_notifications(
        self,
        user_id: int,
        limit: int = 20,
        unread_only: bool = False,
    ) -> list[dict]:
        """Get notifications for a user.

        Args:
            user_id: User ID.
            limit: Max notifications to return.
            unread_only: Only return unread notifications.

        Returns:
            List of notification dicts.
        """
        try:
            r = await self._get_redis()
            key = f"user:{user_id}:notifications"
            notifications = await r.lrange(key, 0, limit - 1)
            results = []
            for n in notifications:
                notif = json.loads(n)
                if unread_only and notif.get("read"):
                    continue
                results.append(notif)
            return results
        except Exception as e:
            logger.error("Failed to get notifications", error=str(e))
            return []

    async def mark_as_read(self, user_id: int, notification_id: int) -> bool:
        """Mark a notification as read.

        Args:
            user_id: User ID.
            notification_id: Notification ID.

        Returns:
            True if found and marked.
        """
        try:
            r = await self._get_redis()
            key = f"user:{user_id}:notifications"
            notifications = await r.lrange(key, 0, -1)
            for i, n in enumerate(notifications):
                notif = json.loads(n)
                if notif.get("id") == notification_id:
                    notif["read"] = True
                    await r.lset(key, i, json.dumps(notif))
                    return True
            return False
        except Exception as e:
            logger.error("Failed to mark notification as read", error=str(e))
            return False

    async def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read.

        Returns:
            Number of notifications marked.
        """
        try:
            r = await self._get_redis()
            key = f"user:{user_id}:notifications"
            notifications = await r.lrange(key, 0, -1)
            count = 0
            for i, n in enumerate(notifications):
                notif = json.loads(n)
                if not notif.get("read"):
                    notif["read"] = True
                    await r.lset(key, i, json.dumps(notif))
                    count += 1
            return count
        except Exception as e:
            logger.error("Failed to mark all as read", error=str(e))
            return 0

    async def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications."""
        notifications = await self.get_notifications(user_id, unread_only=True)
        return len(notifications)

    async def send_application_status_notification(
        self,
        user_id: int,
        application_id: int,
        company: str,
        role: str,
        new_status: str,
    ) -> dict:
        """Send a notification about application status change."""
        status_labels = {
            "sent": "Application Sent",
            "delivered": "Application Delivered",
            "opened": "Application Opened",
            "replied": "Recipient Replied",
            "interview_scheduled": "Interview Scheduled",
            "offer_received": "Offer Received",
            "rejected": "Application Rejected",
        }
        label = status_labels.get(new_status, new_status.replace("_", " ").title())
        return await self.send_notification(
            user_id=user_id,
            notification_type="application_status",
            title=label,
            message=f"Update on your application for {role} at {company}: {label}",
            data={"application_id": application_id, "status": new_status},
        )

    async def send_job_match_notification(
        self,
        user_id: int,
        job_title: str,
        company: str,
        match_score: float,
        job_id: int,
    ) -> dict:
        """Send a notification about a new job match."""
        return await self.send_notification(
            user_id=user_id,
            notification_type="job_match",
            title="New Job Match",
            message=f"New match: {job_title} at {company} ({match_score:.0f}% match)",
            data={"job_id": job_id, "match_score": match_score},
        )
