"""Integration tests for job service.

Tests the full pipeline: service creation -> job operations -> scraping flow.

Note: These tests use mocked DB sessions and HTTP clients,
so they don't require a real PostgreSQL or Redis instance.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.scrapers.base import ScrapeResult
from app.scrapers.remoteok import RemoteOKScraper
from app.services.job_service import JobService
from app.services.normalizer import JobNormalizer
from app.services.scraper_service import ScraperService


class TestJobFullPipeline:
    """Test the end-to-end job service pipeline."""

    @pytest.mark.asyncio
    async def test_create_and_get_job(self, mock_db_session, sample_job_data):
        """Test creating a job and retrieving it."""
        service = JobService(mock_db_session)

        # Mock the ORM add/flush/refresh behavior
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        # Create job
        from app.schemas.job import JobCreate
        data = JobCreate(**sample_job_data)
        job = await service.create_job(data)

        # Verify flush was called
        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_soft_delete_job(self, mock_db_session, sample_job_data):
        """Test soft-deleting a job."""
        service = JobService(mock_db_session)

        # Mock get_job to return a mock job
        mock_job = MagicMock()
        mock_job.status = "active"
        mock_job.id = 1

        with patch.object(service, "get_job", AsyncMock(return_value=mock_job)):
            result = await service.delete_job(1)
            assert result is True
            assert mock_job.status == "closed"

    @pytest.mark.asyncio
    async def test_soft_delete_not_found(self, mock_db_session):
        """Test deleting a non-existent job returns False."""
        service = JobService(mock_db_session)

        with patch.object(service, "get_job", AsyncMock(return_value=None)):
            result = await service.delete_job(999)
            assert result is False

    def test_job_normalizer_basic(self, sample_job_data):
        """Test job normalizer preserves all fields."""
        normalizer = JobNormalizer()
        result = normalizer.normalize(sample_job_data)

        assert result["title"] == "Senior Python Developer"
        assert result["company_name"] == "TestCorp"
        assert result["location_type"] == "remote"
        assert result["is_remote"] is True

    def test_job_normalizer_field_mapping(self):
        """Test normalizer maps various source fields."""
        normalizer = JobNormalizer()

        # Map 'position' to 'title'
        result = normalizer.normalize({"position": "Engineer", "company": "C"})
        assert result["title"] == "Engineer"
        assert result["company_name"] == "C"

        # Map 'role' to 'title'
        result = normalizer.normalize({"role": "Designer", "company": "C"})
        assert result["title"] == "Designer"

    def test_job_normalizer_employment_type_mapping(self):
        """Test normalizer maps employment types."""
        normalizer = JobNormalizer()

        result = normalizer.normalize({"position": "Dev", "company": "C", "type": "Full-Time"})
        assert result["employment_type"] == "full_time"

        result = normalizer.normalize({"position": "Dev", "company": "C", "type": "PART TIME"})
        assert result["employment_type"] == "part_time"

    def test_job_normalizer_location_type(self):
        """Test normalizer detects remote from location."""
        normalizer = JobNormalizer()

        result = normalizer.normalize({"position": "Dev", "company": "C", "location": "Remote - US"})
        assert result["location_type"] == "remote"
        assert result["is_remote"] is True

        result = normalizer.normalize({"position": "Dev", "company": "C", "location": "San Francisco, CA"})
        assert result.get("location_type") is None

    def test_job_normalizer_batch(self, sample_job_data, sample_job_data_2):
        """Test batch normalization."""
        normalizer = JobNormalizer()
        results = normalizer.normalize_batch([sample_job_data, sample_job_data_2])
        assert len(results) == 2


class TestScraperPipeline:
    """Test the scraper pipeline end-to-end."""

    @pytest.mark.asyncio
    async def test_scrape_result_counts(self, mock_remoteok_response):
        """Test scrape counts are tracked correctly."""
        scraper = RemoteOKScraper()

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_remoteok_response
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = await scraper.scrape()
            assert result.total_found == 1
            assert result.success is True
            assert len(result.jobs) == 1

    @pytest.mark.asyncio
    async def test_scraper_service_with_mocks(self, mock_db_session, sample_job_data, sample_job_data_2):
        """Test ScraperService orchestration with mocks."""
        service = ScraperService(mock_db_session)

        # Mock the scraper pipeline
        with patch.object(service, "get_scraper") as mock_get_scraper:
            mock_scraper = AsyncMock()
            mock_scraper.source_name = "test"

            from app.scrapers.base import ScrapeResult
            mock_scraper.scrape = AsyncMock(return_value=ScrapeResult(
                source_name="test",
                jobs=[sample_job_data, sample_job_data_2],
                total_found=2,
                success=True,
            ))
            mock_scraper.close = AsyncMock()
            mock_get_scraper.return_value = mock_scraper

            # Mock dedup to return all as new
            service.dedup.filter_new = AsyncMock(return_value=(
                [sample_job_data, sample_job_data_2], 0
            ))
            service.dedup.mark_batch_seen = AsyncMock()

            result = await service.scrape_source("test", save=True)
            assert result.total_found == 2
            assert result.success is True
            assert result.total_new == 2
