"""Tests for outreach template service."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.template_service import TemplateService


@pytest.mark.asyncio
async def test_list_templates():
    """Test listing templates."""
    db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        result = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [
            MagicMock(id=1, template_name="Professional Cover Letter", content_type="cover_letter", tone="professional"),
            MagicMock(id=2, template_name="Cold Outreach Email", content_type="email", tone="professional"),
        ]
        result.scalars.return_value = scalars_mock
        return result

    db.execute = mock_execute

    svc = TemplateService(db)
    templates = await svc.list_templates()
    assert len(templates) == 2


@pytest.mark.asyncio
async def test_list_templates_filtered():
    """Test listing templates filtered by content type."""
    db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        result = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [
            MagicMock(id=1, template_name="Professional Cover Letter", content_type="cover_letter", tone="professional"),
        ]
        result.scalars.return_value = scalars_mock
        return result

    db.execute = mock_execute

    svc = TemplateService(db)
    templates = await svc.list_templates(content_type="cover_letter")
    assert len(templates) == 1
    assert templates[0].content_type == "cover_letter"


@pytest.mark.asyncio
async def test_get_template_found():
    """Test getting a template by ID."""
    db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        result = MagicMock()
        result.scalar_one_or_none.return_value = MagicMock(
            id=1,
            template_name="Professional Cover Letter",
            content_type="cover_letter",
            tone="professional",
            body="Dear {{recipient}}...",
            is_template=1,
        )
        return result

    db.execute = mock_execute

    svc = TemplateService(db)
    template = await svc.get_template(1)
    assert template is not None
    assert template.template_name == "Professional Cover Letter"


@pytest.mark.asyncio
async def test_get_template_not_found():
    """Test getting a non-existent template."""
    db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        return result

    db.execute = mock_execute

    svc = TemplateService(db)
    template = await svc.get_template(999)
    assert template is None


@pytest.mark.asyncio
async def test_create_template():
    """Test creating a new template."""
    db = AsyncMock()

    async def mock_refresh(obj):
        obj.id = 1

    db.add = MagicMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock(side_effect=mock_refresh)

    svc = TemplateService(db)
    template = await svc.create_template(
        name="My Template",
        content_type="cover_letter",
        body="Dear {{recipient}}...",
        tone="professional",
        tags=["standard", "formal"],
    )

    assert template.is_template == 1
    assert template.template_name == "My Template"
    assert template.content_type == "cover_letter"
    assert template.tone == "professional"
    assert db.add.called
