"""Integration tests for Application Service."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.application_service import ApplicationService
from app.services.event_service import EventService
from app.services.state_machine import StateMachineService
from app.schemas.application import ApplicationCreate, ApplicationUpdate


@pytest.mark.asyncio
async def test_create_and_submit_flow():
    """Test full flow: create draft -> update status -> submit."""
    db = AsyncMock()
    svc = ApplicationService(db)

    # Mock the DB to return a mock application
    mock_app = MagicMock()
    mock_app.id = 1
    mock_app.profile_id = 1
    mock_app.job_id = 100
    mock_app.user_id = 1
    mock_app.status = "draft"
    mock_app.company_name = "Tech Corp"
    mock_app.job_title = "Software Engineer"
    mock_app.job_location = "Remote"
    mock_app.match_score = 85.0
    mock_app.notes = None
    mock_app.resume_id = None
    mock_app.cover_letter_id = None
    mock_app.email_id = None
    mock_app.delivery_status = None
    mock_app.sent_at = None
    mock_app.retry_count = 0
    mock_app.created_at = None
    mock_app.updated_at = None
    mock_app.package_data = None
    mock_app.previous_status = None

    def refresh_side_effect(obj):
        obj.id = 1

    db.refresh.side_effect = refresh_side_effect
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.execute = AsyncMock()

    # Test: Create application
    create_data = ApplicationCreate(
        profile_id=1,
        job_id=100,
        company_name="Tech Corp",
        job_title="Software Engineer",
        job_location="Remote",
        match_score=85.0,
    )

    # Set up event mocks
    svc.event_service.create_event = AsyncMock()

    app = await svc.create(create_data)
    assert app.status == "draft"

    # Test: State machine transitions
    state_svc = StateMachineService(db)
    valid, error = state_svc.validate_transition("draft", "matched")
    assert valid
    assert error is None

    valid, error = state_svc.validate_transition("matched", "resume_generated")
    assert valid

    valid, error = state_svc.validate_transition("resume_generated", "cover_letter_generated")
    assert valid

    valid, error = state_svc.validate_transition("cover_letter_generated", "email_prepared")
    assert valid

    valid, error = state_svc.validate_transition("email_prepared", "sent")
    assert valid


@pytest.mark.asyncio
async def test_event_creation():
    """Test event creation during application lifecycle."""
    db = AsyncMock()
    event_svc = EventService(db)
    db.add = MagicMock()
    db.flush = AsyncMock()

    event = await event_svc.create_event(
        application_id=1,
        to_status="sent",
        from_status="email_prepared",
        event_type="submitted",
        description="Application submitted",
        actor="user",
    )

    assert event.application_id == 1
    assert event.to_status == "sent"
    assert event.from_status == "email_prepared"
    assert event.event_type == "submitted"
    assert event.actor == "user"
    assert db.add.called
