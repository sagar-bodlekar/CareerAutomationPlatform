"""Tests for email generation service."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.email_service import EmailService
from app.schemas.email import EmailRequest


@pytest.mark.asyncio
async def test_generate_draft():
    """Test generating a draft email without AI."""
    db = AsyncMock()

    async def mock_refresh(obj):
        obj.id = 1
        obj.version = 1
        obj.edit_count = 0

    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.add = MagicMock()
    db.refresh = AsyncMock(side_effect=mock_refresh)

    svc = EmailService(db)

    request = EmailRequest(
        profile_id=1,
        job_id=100,
        job_title="Software Engineer",
        company_name="Tech Corp",
        candidate_name="John Doe",
        current_role="Senior Developer",
        recipient_name="Jane Smith",
        recipient_role="Hiring Manager",
        use_ai=False,
    )

    response = await svc.generate(request)
    assert response.content_type == "email"
    assert "Software Engineer" in response.body
    assert "Tech Corp" in response.body
    assert "Jane Smith" in response.body
    assert response.ai_agent_used is None
    assert response.id == 1
    assert response.version == 1
    assert db.add.called


@pytest.mark.asyncio
async def test_generate_with_ai_placeholder():
    """Test generating an email with AI (uses placeholder for now)."""
    db = AsyncMock()

    async def mock_refresh(obj):
        obj.id = 1
        obj.version = 1
        obj.edit_count = 0

    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.add = MagicMock()
    db.refresh = AsyncMock(side_effect=mock_refresh)

    svc = EmailService(db)

    request = EmailRequest(
        profile_id=1,
        job_id=100,
        job_title="Data Scientist",
        company_name="AI Corp",
        candidate_name="Alice",
        current_role="ML Engineer",
        recipient_name="Bob",
        recipient_role="Tech Lead",
        use_ai=True,
    )

    response = await svc.generate(request)
    assert response.content_type == "email"
    assert "Data Scientist" in response.body
    assert response.ai_agent_used == "outreach_agent"
    assert response.id == 1
    assert response.version == 1


@pytest.mark.asyncio
async def test_get_email():
    """Test retrieving an email by ID."""
    db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        result = MagicMock()
        record = MagicMock(spec=[])
        record.id = 1
        record.content_type = "email"
        record.subject = "Interest in Engineer position"
        record.body = "Dear Hiring Manager, ..."
        record.tone = "professional"
        record.profile_id = 1
        record.job_id = 100
        record.company_name = "Tech Corp"
        record.recipient_name = "Jane Smith"
        record.recipient_role = "Hiring Manager"
        record.version = 1
        record.status = "draft"
        record.ai_agent_used = None
        record.tokens_used = None
        record.created_at = None
        record.updated_at = None
        result.scalar_one_or_none.return_value = record
        return result

    db.execute = mock_execute

    svc = EmailService(db)
    result = await svc.get(1)
    assert result is not None
    assert result.id == 1
    assert result.content_type == "email"


@pytest.mark.asyncio
async def test_get_email_not_found():
    """Test retrieving a non-existent email."""
    db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        return result

    db.execute = mock_execute

    svc = EmailService(db)
    result = await svc.get(999)
    assert result is None


@pytest.mark.asyncio
async def test_update_email():
    """Test updating an email."""
    db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        result = MagicMock()
        record = MagicMock(spec=[])
        record.id = 1
        record.edit_count = 0
        record.version = 1
        record.subject = "Original subject"
        record.body = "Original content"
        record.status = "draft"
        record.content_type = "email"
        record.tone = "professional"
        record.ai_agent_used = None
        record.tokens_used = None
        record.profile_id = 1
        record.job_id = 100
        record.company_name = "Tech Corp"
        record.recipient_name = "Jane"
        record.recipient_role = "Manager"
        record.created_at = None
        record.updated_at = None
        result.scalar_one_or_none.return_value = record
        return result

    db.execute = mock_execute
    db.flush = AsyncMock()

    svc = EmailService(db)
    result = await svc.update(1, subject="Updated subject", body="Updated content")
    assert result is not None
    assert result.id == 1


@pytest.mark.asyncio
async def test_generate_draft_content():
    """Test draft email content quality."""
    db = AsyncMock()
    svc = EmailService(db)

    request = EmailRequest(
        profile_id=1,
        job_id=100,
        job_title="Full Stack Developer",
        company_name="Startup Inc",
        candidate_name="Jane",
        current_role="Developer",
        recipient_name="Mike",
        recipient_role="CTO",
        use_ai=False,
    )

    body = svc._generate_draft(request)
    assert "Dear Mike" in body
    assert "Full Stack Developer" in body
    assert "Startup Inc" in body
    assert body.endswith("Jane")
