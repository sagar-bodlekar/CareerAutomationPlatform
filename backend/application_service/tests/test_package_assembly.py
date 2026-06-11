"""Tests for application package assembly."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.package_assembler import PackageAssembler
from app.services.attachment_service import AttachmentService


class TestPackageAssembler:
    """Tests for the package assembler service."""

    @pytest.mark.asyncio
    async def test_assemble_basic(self):
        """Test basic package assembly."""
        db = AsyncMock()
        svc = PackageAssembler(db)

        app_mock = MagicMock()
        app_mock.id = 1
        app_mock.job_id = 100
        app_mock.profile_id = 1
        app_mock.company_name = "Tech Corp"
        app_mock.job_title = "Software Engineer"
        app_mock.resume_id = 10
        app_mock.cover_letter_id = 20
        app_mock.email_id = 30

        package = await svc.assemble(app_mock)
        assert package["application_id"] == 1
        assert package["company_name"] == "Tech Corp"
        assert package["job_title"] == "Software Engineer"
        assert "resume" in package["components"]
        assert package["components"]["cover_letter"]["id"] == 20
        assert package["components"]["email"]["id"] == 30

    @pytest.mark.asyncio
    async def test_assemble_without_resume(self):
        """Test package assembly without a resume."""
        db = AsyncMock()
        svc = PackageAssembler(db)

        app_mock = MagicMock()
        app_mock.resume_id = None

        package = await svc.assemble(app_mock)
        assert package["components"].get("resume") is None

    @pytest.mark.asyncio
    async def test_assemble_contains_required_keys(self):
        """Test package contains all required keys."""
        db = AsyncMock()
        svc = PackageAssembler(db)

        app_mock = MagicMock()
        app_mock.resume_id = 10
        app_mock.cover_letter_id = 20
        app_mock.email_id = 30

        package = await svc.assemble(app_mock)
        assert "components" in package
        assert "status" in package
        assert "application_id" in package


class TestAttachmentService:
    """Tests for the attachment service."""

    @pytest.mark.asyncio
    async def test_download_resume_pdf_not_implemented(self):
        """Test resume download returns None (not yet implemented)."""
        svc = AttachmentService()
        result = await svc.download_resume_pdf(1)
        assert result is None

    @pytest.mark.asyncio
    async def test_attach_to_email(self):
        """Test creating a MIME attachment from PDF bytes."""
        svc = AttachmentService()
        pdf_bytes = b"%PDF-1.4 mock pdf content"
        result = await svc.attach_to_email(pdf_bytes, "resume.pdf")

        assert result["filename"] == "resume.pdf"
        assert result["content_type"] == "application/pdf"
        assert result["encoding"] == "base64"
        assert isinstance(result["content"], str)
        assert len(result["content"]) > 0
