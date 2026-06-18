"""Tests for the NotificationService class."""

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest


class TestNotificationService:
    """Tests for NotificationService CRUD and business logic."""

    @pytest.mark.asyncio
    async def test_send_notification(self, notification_service, mock_redis):
        """Sending a notification should store it in Redis and publish."""
        result = await notification_service.send_notification(
            user_id=1,
            notification_type="application_status",
            title="Application Sent",
            message="Your application was sent.",
            data={"application_id": 42},
        )

        assert result["user_id"] == 1
        assert result["type"] == "application_status"
        assert result["title"] == "Application Sent"
        assert result["message"] == "Your application was sent."
        assert result["data"] == {"application_id": 42}
        assert result["read"] is False
        assert "id" in result
        assert "created_at" in result

        # Verify Redis was called
        mock_redis.lpush.assert_called_once()
        mock_redis.ltrim.assert_called_once()
        mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_default_data(self, notification_service, mock_redis):
        """Sending a notification without data should use empty dict."""
        result = await notification_service.send_notification(
            user_id=2,
            notification_type="job_match",
            title="New Match",
            message="Match found!",
        )

        assert result["data"] == {}

    @pytest.mark.asyncio
    async def test_get_notifications(self, notification_service, mock_redis, sample_notifications_list):
        """Getting notifications should return deserialized list."""
        mock_redis.lrange.return_value = sample_notifications_list

        notifications = await notification_service.get_notifications(user_id=1, limit=10)

        assert len(notifications) == 3
        assert notifications[0]["title"] == "Application Sent"
        assert notifications[1]["title"] == "New Job Match"
        assert notifications[2]["title"] == "Application Delivered"
        mock_redis.lrange.assert_called_once_with("user:1:notifications", 0, 9)

    @pytest.mark.asyncio
    async def test_get_notifications_empty(self, notification_service, mock_redis):
        """Getting notifications when none exist should return empty list."""
        mock_redis.lrange.return_value = []

        notifications = await notification_service.get_notifications(user_id=999, limit=20)

        assert notifications == []

    @pytest.mark.asyncio
    async def test_get_notifications_unread_only(self, notification_service, mock_redis, sample_notifications_list):
        """Filtering by unread_only should return only unread notifications."""
        mock_redis.lrange.return_value = sample_notifications_list

        notifications = await notification_service.get_notifications(
            user_id=1, limit=10, unread_only=True
        )

        assert len(notifications) == 2  # Only the two unread ones
        for n in notifications:
            assert n["read"] is False

    @pytest.mark.asyncio
    async def test_get_unread_count(self, notification_service, mock_redis, sample_notifications_list):
        """Unread count should return correct number."""
        mock_redis.lrange.return_value = sample_notifications_list

        count = await notification_service.get_unread_count(user_id=1)

        assert count == 2

    @pytest.mark.asyncio
    async def test_mark_as_read_success(self, notification_service, mock_redis, sample_notifications_list):
        """Marking a notification as read should update its read flag."""
        mock_redis.lrange.return_value = sample_notifications_list

        result = await notification_service.mark_as_read(user_id=1, notification_id=12345)

        assert result is True
        # Verify lset was called to update the notification
        mock_redis.lset.assert_called_once()
        args, _ = mock_redis.lset.call_args
        assert args[0] == "user:1:notifications"
        updated = json.loads(args[2])
        assert updated["read"] is True

    @pytest.mark.asyncio
    async def test_mark_as_read_not_found(self, notification_service, mock_redis, sample_notifications_list):
        """Marking a nonexistent notification should return False."""
        mock_redis.lrange.return_value = sample_notifications_list

        result = await notification_service.mark_as_read(user_id=1, notification_id=99999)

        assert result is False
        mock_redis.lset.assert_not_called()

    @pytest.mark.asyncio
    async def test_mark_all_as_read(self, notification_service, mock_redis, sample_notifications_list):
        """Marking all as read should update all unread notifications."""
        mock_redis.lrange.return_value = sample_notifications_list

        count = await notification_service.mark_all_as_read(user_id=1)

        assert count == 2  # Two unread were marked
        assert mock_redis.lset.call_count == 2

    @pytest.mark.asyncio
    async def test_mark_all_as_read_all_already_read(self, notification_service, mock_redis):
        """Marking all as read when all are already read should return 0."""
        import json
        notif = {
            "id": 1, "user_id": 1, "type": "test",
            "title": "Test", "message": "Test",
            "data": {}, "read": True, "created_at": "2026-01-01T00:00:00",
        }
        mock_redis.lrange.return_value = [json.dumps(notif)]

        count = await notification_service.mark_all_as_read(user_id=1)

        assert count == 0
        mock_redis.lset.assert_not_called()

    @pytest.mark.asyncio
    async def test_redis_unavailable_graceful_fallback(self, notification_service, mock_redis):
        """When Redis is unavailable, methods should fail gracefully."""
        mock_redis.lpush.side_effect = Exception("Connection refused")

        # Should not raise, should log error and return notification anyway
        result = await notification_service.send_notification(
            user_id=1,
            notification_type="application_status",
            title="Test",
            message="Test",
        )

        assert result["title"] == "Test"  # Notification is still returned

    @pytest.mark.asyncio
    async def test_redis_get_failure_returns_empty(self, notification_service, mock_redis):
        """When Redis fails during get, should return empty list."""
        mock_redis.lrange.side_effect = Exception("Connection refused")

        notifications = await notification_service.get_notifications(user_id=1)

        assert notifications == []


class TestNotificationServiceConvenienceMethods:
    """Tests for the convenience notification methods."""

    @pytest.mark.asyncio
    async def test_send_application_status_notification(self, notification_service, mock_redis):
        """Application status notification should use correct template."""
        result = await notification_service.send_application_status_notification(
            user_id=1,
            application_id=42,
            company="Tech Corp",
            role="Senior Engineer",
            new_status="sent",
        )

        assert result["type"] == "application_status"
        assert result["title"] == "Application Sent"
        assert "Senior Engineer" in result["message"]
        assert "Tech Corp" in result["message"]
        assert result["data"]["application_id"] == 42
        assert result["data"]["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_application_status_notification_interview(self, notification_service, mock_redis):
        """Interview scheduling notification should use correct template."""
        result = await notification_service.send_application_status_notification(
            user_id=1,
            application_id=42,
            company="Startup Inc",
            role="Frontend Engineer",
            new_status="interview_scheduled",
        )

        assert result["title"] == "Interview Scheduled"

    @pytest.mark.asyncio
    async def test_send_application_status_notification_offer(self, notification_service, mock_redis):
        """Offer received notification should use correct template."""
        result = await notification_service.send_application_status_notification(
            user_id=1,
            application_id=42,
            company="Tech Corp",
            role="Engineer",
            new_status="offer_received",
        )

        assert result["title"] == "Offer Received"

    @pytest.mark.asyncio
    async def test_send_application_status_notification_rejected(self, notification_service, mock_redis):
        """Rejected notification should use correct template."""
        result = await notification_service.send_application_status_notification(
            user_id=1,
            application_id=42,
            company="Some Corp",
            role="Developer",
            new_status="rejected",
        )

        assert result["title"] == "Application Rejected"

    @pytest.mark.asyncio
    async def test_send_application_status_unknown_status(self, notification_service, mock_redis):
        """Unknown status should be title-cased gracefully."""
        result = await notification_service.send_application_status_notification(
            user_id=1,
            application_id=42,
            company="Test Co",
            role="Dev",
            new_status="custom_status",
        )

        assert result["title"] == "Custom Status"

    @pytest.mark.asyncio
    async def test_send_job_match_notification(self, notification_service, mock_redis):
        """Job match notification should include match score."""
        result = await notification_service.send_job_match_notification(
            user_id=1,
            job_title="Senior Engineer",
            company="Tech Corp",
            match_score=92.5,
            job_id=101,
        )

        assert result["type"] == "job_match"
        assert result["title"] == "New Job Match"
        assert "92%" in result["message"]
        assert result["data"]["job_id"] == 101
        assert result["data"]["match_score"] == 92.5


class TestWebSocketService:
    """Tests for the WebSocket connection manager."""

    @pytest.mark.asyncio
    async def test_connect_disconnect(self):
        """WebSocket connect and disconnect should manage connections."""
        from app.services.websocket_service import ConnectionManager

        manager = ConnectionManager()
        mock_ws = AsyncMock()

        await manager.connect(mock_ws, user_id=1)
        assert 1 in manager.active_connections
        assert len(manager.active_connections[1]) == 1

        await manager.disconnect(mock_ws, user_id=1)
        assert 1 not in manager.active_connections

    @pytest.mark.asyncio
    async def test_multiple_connections_same_user(self):
        """Multiple connections for the same user should be tracked."""
        from app.services.websocket_service import ConnectionManager

        manager = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await manager.connect(ws1, user_id=1)
        await manager.connect(ws2, user_id=1)

        assert len(manager.active_connections[1]) == 2

        await manager.disconnect(ws1, user_id=1)
        assert len(manager.active_connections[1]) == 1

    @pytest.mark.asyncio
    async def test_send_personal_message(self):
        """Sending a message should broadcast to all user connections."""
        from app.services.websocket_service import ConnectionManager

        manager = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await manager.connect(ws1, user_id=1)
        await manager.connect(ws2, user_id=1)

        message = {"type": "test", "data": "hello"}
        await manager.send_personal_message(message, user_id=1)

        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_send_message_no_connections(self):
        """Sending a message to a user with no connections should do nothing."""
        from app.services.websocket_service import ConnectionManager

        manager = ConnectionManager()
        message = {"type": "test", "data": "hello"}

        # Should not raise
        await manager.send_personal_message(message, user_id=999)

    @pytest.mark.asyncio
    async def test_send_message_failed_connection_cleaned_up(self):
        """If a WebSocket send fails, the connection should be removed."""
        from app.services.websocket_service import ConnectionManager

        manager = ConnectionManager()
        ws1 = AsyncMock()
        ws1.send_json.side_effect = Exception("Connection lost")
        ws2 = AsyncMock()

        await manager.connect(ws1, user_id=1)
        await manager.connect(ws2, user_id=1)

        await manager.send_personal_message({"test": "data"}, user_id=1)

        # ws1 should have been disconnected after failure
        assert len(manager.active_connections[1]) == 1
        ws1.send_json.assert_called_once()
        ws2.send_json.assert_called_once()
