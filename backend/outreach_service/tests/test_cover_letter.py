"""Tests for cover letter generation service."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.cover_letter_service import CoverLetterService
from app.schemas.cover_letter import CoverLetterRequest


@pytest.mark.asyncio
async def test_generate_draft():
    """Test generating a draft cover letter without AI."""
    db = AsyncMock()

    async def mock_refresh(obj):
        obj.id = 1
        obj.version = 1
        obj.edit_count = 0

    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.add = MagicMock()
    db.refresh = AsyncMock(side_effect=mock_refresh)

    svc = CoverLetterService(db)

    request = CoverLetterRequest(
        profile_id=1,
        job_id=100,
        job_title="Software Engineer",
        company_name="Tech Corp",
        candidate_name="John Doe",
        current_role="Senior Developer",
        skills=["Python", "React", "AWS"],
        achievements=["Led a team of 5 engineers", "Delivered 3 major projects"],
        use_ai=False,
    )

    response = await svc.generate(request)
    assert response.content_type == "cover_letter"
    assert "Software Engineer" in response.body
    assert "Tech Corp" in response.body
    assert "John Doe" in response.body
    assert response.ai_agent_used is None
    assert response.id == 1
    assert response.version == 1
    assert db.add.called


@pytest.mark.asyncio
async def test_get_cover_letter():
    """Test retrieving a cover letter by ID."""
    db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        result = MagicMock()
        # Create a mock record with proper types for all required CoverLetterResponse fields
        record = MagicMock(spec=[])
        record.id = 1
        record.content_type = "cover_letter"
        record.subject = "Application for Engineer position"
        record.body = "Dear Hiring Manager, ..."
        record.tone = "professional"
        record.profile_id = 1
        record.job_id = 100
        record.company_name = "Tech Corp"
        record.target_role = "Software Engineer"
        record.version = 1
        record.status = "draft"
        record.ai_agent_used = None
        record.tokens_used = None
        record.created_at = None
        record.updated_at = None
        result.scalar_one_or_none.return_value = record
        return result

    db.execute = mock_execute

    svc = CoverLetterService(db)
    result = await svc.get(1)
    assert result is not None
    assert result.id == 1
    assert result.content_type == "cover_letter"


@pytest.mark.asyncio
async def test_get_cover_letter_not_found():
    """Test retrieving a non-existent cover letter."""
    db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        return result

    db.execute = mock_execute

    svc = CoverLetterService(db)
    result = await svc.get(999)
    assert result is None


@pytest.mark.asyncio
async def test_update_cover_letter():
    """Test updating a cover letter."""
    db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        result = MagicMock()
        record = MagicMock(spec=[])
        record.id = 1
        record.edit_count = 0
        record.version = 1
        record.body = "Original content"
        record.status = "draft"
        record.content_type = "cover_letter"
        record.tone = "professional"
        record.subject = "Original subject"
        record.ai_agent_used = None
        record.tokens_used = None
        record.profile_id = 1
        record.job_id = 100
        record.company_name = "Tech Corp"
        record.target_role = "Engineer"
        record.created_at = None
        record.updated_at = None
        result.scalar_one_or_none.return_value = record
        return result

    db.execute = mock_execute
    db.flush = AsyncMock()

    svc = CoverLetterService(db)
    result = await svc.update(1, body="Updated content")
    assert result is not None
    assert result.id == 1
