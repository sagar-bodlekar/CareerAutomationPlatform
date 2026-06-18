"""Test fixtures for notification service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_redis():
    """Create a mock Redis client for testing."""
    redis = AsyncMock()
    redis.lpush = AsyncMock(return_value=1)
    redis.ltrim = AsyncMock(return_value=True)
    redis.lrange = AsyncMock(return_value=[])
    redis.lset = AsyncMock(return_value=True)
    redis.publish = AsyncMock(return_value=1)
    redis.delete = AsyncMock(return_value=1)
    return redis


@pytest.fixture
def notification_service(mock_redis):
    """Create a NotificationService instance with mocked Redis."""
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        from app.services.notification_service import NotificationService
        service = NotificationService()
        service._redis = mock_redis
        return service


@pytest.fixture
def sample_notification():
    """Sample notification data for testing."""
    return {
        "id": 12345,
        "user_id": 1,
        "type": "application_status",
        "title": "Application Sent",
        "message": "Your application for Senior Engineer at Tech Corp has been sent.",
        "data": {"application_id": 42, "status": "sent"},
        "read": False,
        "created_at": "2026-06-19T00:00:00",
    }


@pytest.fixture
def sample_notifications_list(sample_notification):
    """A list of sample notifications as JSON strings (as Redis would return)."""
    import json

    notif2 = {**sample_notification, "id": 12346, "title": "New Job Match", "type": "job_match", "read": True}
    notif3 = {**sample_notification, "id": 12347, "title": "Application Delivered", "read": False}

    return [
        json.dumps(sample_notification),
        json.dumps(notif2),
        json.dumps(notif3),
    ]
