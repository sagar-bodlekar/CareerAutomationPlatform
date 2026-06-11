"""Unit tests for job scrapers."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.scrapers.base import JobScraper, ScrapeError, ScrapeResult
from app.scrapers.remoteok import RemoteOKScraper
from app.scrapers.naukri import NaukriScraper
from app.scrapers.linkedin import LinkedInScraper
from app.scrapers.generic import GenericCareerPageScraper


class TestScraperBase:
    """Tests for the abstract JobScraper base class."""

    def test_scrape_result_defaults(self):
        """ScrapeResult should have sensible defaults."""
        result = ScrapeResult(source_name="test")
        assert result.source_name == "test"
        assert result.jobs == []
        assert result.total_found == 0
        assert result.total_new == 0
        assert result.total_duplicates == 0
        assert result.total_errors == 0
        assert result.errors == []
        assert result.success is True

    def test_scrape_error(self):
        """ScrapeError should format message correctly."""
        error = ScrapeError("Something went wrong", "testsource", recoverable=True)
        assert str(error) == "[testsource] Something went wrong"
        assert error.recoverable is True
        assert error.source == "testsource"


class TestRemoteOKScraper:
    """Tests for RemoteOK scraper."""

    @pytest.mark.asyncio
    async def test_source_name(self):
        scraper = RemoteOKScraper()
        assert scraper.source_name == "remoteok"

    @pytest.mark.asyncio
    async def test_fetch_success(self, mock_remoteok_response, mock_httpx_response):
        """Fetch should return parsed job list on success."""
        scraper = RemoteOKScraper()

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = mock_httpx_response(
                status_code=200,
                json_data=mock_remoteok_response,
            )
            mock_get.return_value = mock_response

            jobs = await scraper.fetch()
            assert len(jobs) == 1
            assert jobs[0]["position"] == "Senior Python Developer"
            assert jobs[0]["company"] == "TestCorp"

    @pytest.mark.asyncio
    async def test_fetch_with_metadata_element(self, mock_httpx_response):
        """Fetch should skip metadata element (slug starting with '_')."""
        scraper = RemoteOKScraper()
        raw_data = [
            {"slug": "_metadata", "count": 100},
            {"slug": "job-1", "position": "Dev 1", "company": "C1"},
            {"slug": "job-2", "position": "Dev 2", "company": "C2"},
        ]

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_httpx_response(
                status_code=200, json_data=raw_data
            )
            jobs = await scraper.fetch()
            assert len(jobs) == 2

    @pytest.mark.asyncio
    async def test_fetch_http_error(self, mock_httpx_response):
        """Fetch should raise ScrapeError on HTTP error."""
        scraper = RemoteOKScraper()

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_httpx_response(
                status_code=500, json_data=None
            )
            mock_get.return_value.raise_for_status.side_effect = (
                httpx.HTTPStatusError("500", request=MagicMock(), response=MagicMock())
            )

            with pytest.raises(ScrapeError):
                await scraper.fetch()

    @pytest.mark.asyncio
    async def test_fetch_timeout(self):
        """Fetch should raise ScrapeError on timeout."""
        scraper = RemoteOKScraper()

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.TimeoutException("timeout")

            with pytest.raises(ScrapeError, match="timed out"):
                await scraper.fetch()

    def test_parse(self, mock_remoteok_response):
        """Parse should convert raw data to normalized format."""
        scraper = RemoteOKScraper()
        parsed = scraper.parse(mock_remoteok_response)

        assert len(parsed) == 1
        job = parsed[0]
        assert job["title"] == "Senior Python Developer"
        assert job["company_name"] == "TestCorp"
        assert job["is_remote"] is True
        assert job["location_type"] == "remote"
        assert job["salary_min"] == 120000
        assert job["salary_max"] == 180000
        assert "Python" in str(job["required_skills"])
        assert job["external_id"] == "remoteok_senior-python-developer"

    def test_parse_empty(self):
        """Parse should handle empty input."""
        scraper = RemoteOKScraper()
        assert scraper.parse([]) == []

    def test_parse_salary_range(self):
        """Parse should handle various salary formats."""
        scraper = RemoteOKScraper()

        # No salary
        job = scraper.parse([{"slug": "test", "position": "Dev", "company": "C"}])
        assert job[0]["salary_min"] is None

        # With salary
        job = scraper.parse([{
            "slug": "test", "position": "Dev", "company": "C",
            "salary": "$100k-$150k",
        }])
        assert job[0]["salary_min"] == 100000
        assert job[0]["salary_max"] == 150000


class TestNaukriScraper:
    """Tests for Naukri scraper."""

    @pytest.mark.asyncio
    async def test_source_name(self):
        scraper = NaukriScraper()
        assert scraper.source_name == "naukri"

    def test_extract_skills(self):
        """Should extract skill keywords from job description."""
        scraper = NaukriScraper()
        text = "We need Python, React, and PostgreSQL experts with AWS experience"
        skills = scraper._extract_skills(text)
        assert "Python" in skills
        assert "React" in skills
        assert "PostgreSQL" in skills
        assert "AWS" in skills

    def test_parse_salary_inr(self):
        """Should parse Indian salary format."""
        scraper = NaukriScraper()
        assert scraper._parse_salary("6-12 Lacs PA") == (600000, 1200000)
        assert scraper._parse_salary("10L") == (1000000, None)
        assert scraper._parse_salary("1.5 Cr") == (15000000, None)
        assert scraper._parse_salary(None) == (None, None)

    def test_parse_experience(self):
        """Should parse experience strings."""
        scraper = NaukriScraper()
        assert scraper._parse_experience("3-5 yrs") == (3, 5)
        assert scraper._parse_experience("7+ yrs") == (7, None)
        assert scraper._parse_experience(None) == (None, None)

    def test_parse(self):
        """Parse should convert Naukri format to normalized."""
        scraper = NaukriScraper()
        raw = [{
            "jobId": "123",
            "title": "Python Developer",
            "companyName": "TechCorp",
            "location": "Bangalore",
            "salary": "12-20 Lacs PA",
            "minExperience": 3,
            "maxExperience": 5,
        }]
        parsed = scraper.parse(raw)
        assert len(parsed) == 1
        assert parsed[0]["title"] == "Python Developer"
        assert parsed[0]["company_name"] == "TechCorp"
        assert parsed[0]["salary_min"] == 1200000
        assert parsed[0]["salary_max"] == 2000000
        assert parsed[0]["salary_currency"] == "INR"


class TestGenericScraper:
    """Tests for Generic career page scraper."""

    @pytest.mark.asyncio
    async def test_source_name(self):
        scraper = GenericCareerPageScraper(config={"name": "testcorp"})
        assert scraper.source_name == "testcorp"

    def test_parse(self):
        """Parse should create normalized output."""
        scraper = GenericCareerPageScraper(config={
            "name": "testcorp",
            "company_name": "Testcorp Inc",
        })
        raw = [{
            "title": "Engineer",
            "url": "https://testcorp.com/jobs/engineer",
            "location": "Remote",
        }]
        parsed = scraper.parse(raw)
        assert len(parsed) == 1
        assert parsed[0]["title"] == "Engineer"
        assert parsed[0]["company_name"] == "Testcorp Inc"
        assert parsed[0]["is_remote"] is True
