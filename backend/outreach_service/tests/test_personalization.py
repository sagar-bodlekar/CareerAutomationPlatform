"""Tests for personalization service."""

import pytest

from app.services.personalization_service import PersonalizationService


@pytest.mark.asyncio
async def test_extract_hooks_with_company_data():
    """Test extracting hooks from company data."""
    svc = PersonalizationService()
    result = await svc.extract_hooks(
        company_name="Tech Corp",
        industry="Software",
        company_description="Tech Corp builds cloud infrastructure for enterprise customers. We help companies scale their applications.",
        skills=["Python", "AWS", "Kubernetes"],
    )

    assert result["hooks_found"] > 0
    assert len(result["personalization_hooks"]) > 0
    assert any("Python" in str(h) for h in result["personalization_hooks"])
    assert len(result["key_talking_points"]) > 0


@pytest.mark.asyncio
async def test_extract_hooks_minimal():
    """Test extracting hooks with minimal data."""
    svc = PersonalizationService()
    result = await svc.extract_hooks(
        company_name="Startup Inc",
    )

    assert result["hooks_found"] == 0
    assert len(result["personalization_hooks"]) == 0


@pytest.mark.asyncio
async def test_extract_from_job():
    """Test extracting hooks from job data."""
    svc = PersonalizationService()
    result = await svc.extract_from_job(
        job_title="Senior Engineer",
        job_description="We need a senior engineer with 5+ years experience",
        required_skills=["Go", "Docker", "PostgreSQL"],
    )

    assert result["count"] > 0
    assert len(result["hooks"]) > 0


@pytest.mark.asyncio
async def test_recommended_tone_default():
    """Test default recommended tone."""
    svc = PersonalizationService()
    result = await svc.extract_hooks(company_name="Test Corp")
    assert result["recommended_tone"] == "professional"


@pytest.mark.asyncio
async def test_extract_from_job_no_description():
    """Test extracting from job with no description."""
    svc = PersonalizationService()
    result = await svc.extract_from_job(job_title="Engineer")
    assert result["count"] == 0
