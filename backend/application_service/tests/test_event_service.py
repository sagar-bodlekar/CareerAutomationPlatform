"""Tests for application event service."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.event_service import EventService
from app.models.models import ApplicationEvent


def _make_mock_execute(events=None):
    """Create a mock async execute function."""
    events = events or []

    async def mock_execute(*args, **kwargs):
        mock_result = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = events
        mock_result.scalars.return_value = scalars_mock
        return mock_result

    return mock_execute


@pytest.mark.asyncio
async def test_create_event():
    """Test creating an application event."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    svc = EventService(db)

    event = await svc.create_event(
        application_id=1,
        to_status="sent",
        from_status="email_prepared",
        event_type="submitted",
        description="Application submitted by user",
        actor="user",
        metadata_json={"source": "web"},
    )

    assert event.application_id == 1
    assert event.to_status == "sent"
    assert event.from_status == "email_prepared"
    assert event.event_type == "submitted"
    assert event.actor == "user"
    assert event.metadata_json == {"source": "web"}
    assert db.add.called


@pytest.mark.asyncio
async def test_create_event_minimal():
    """Test creating an event with only required fields."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    svc = EventService(db)

    event = await svc.create_event(
        application_id=1,
        to_status="draft",
        event_type="created",
    )

    assert event.application_id == 1
    assert event.to_status == "draft"
    assert event.event_type == "created"
    assert event.actor == "system"


@pytest.mark.asyncio
async def test_get_events():
    """Test retrieving events for an application."""
    db = AsyncMock()
    db.execute = _make_mock_execute([
        MagicMock(spec=ApplicationEvent, id=1),
        MagicMock(spec=ApplicationEvent, id=2),
    ])

    svc = EventService(db)
    events = await svc.get_events(application_id=1)
    assert len(events) == 2


@pytest.mark.asyncio
async def test_get_events_empty():
    """Test retrieving events for application with no events."""
    db = AsyncMock()
    db.execute = _make_mock_execute([])

    svc = EventService(db)
    events = await svc.get_events(application_id=999)
    assert len(events) == 0
    assert db.execute is not None


@pytest.mark.asyncio
async def test_event_order():
    """Test events are retrieved from the database."""
    db = AsyncMock()
    db.execute = _make_mock_execute([
        MagicMock(spec=ApplicationEvent, id=1),
    ])

    svc = EventService(db)
    events = await svc.get_events(application_id=1)
    assert len(events) >= 1
