"""API tests for job service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints import router
from app.api.v1.health import router as health_router
from app.services.job_service import JobService
from app.services.scraper_service import ScraperService


@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI()
    app.include_router(health_router)
    app.include_router(router)
    return app


@pytest.fixture
def mock_job_service():
    """Create mock JobService."""
    service = AsyncMock(spec=JobService)
    return service


@pytest.fixture
def mock_scraper_service():
    """Create mock ScraperService."""
    service = AsyncMock(spec=ScraperService)
    return service


def _override_deps(app, mock_job_service, mock_scraper_service):
    """Override service dependencies in test app."""
    from app.api.v1 import dependencies as deps

    async def get_mock_job_service():
        return mock_job_service

    async def get_mock_scraper_service():
        return mock_scraper_service

    async def get_mock_user():
        return 1  # Mock user_id

    app.dependency_overrides[deps.get_job_service] = get_mock_job_service
    app.dependency_overrides[deps.get_scraper_service] = get_mock_scraper_service
    app.dependency_overrides[deps.get_current_user_id] = get_mock_user


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, app):
        """Health endpoint should return ok status."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["service"] == "job-service"


class TestJobEndpoints:
    """Tests for job CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_list_jobs(self, app, mock_job_service, mock_scraper_service):
        """GET /jobs should return paginated jobs."""
        _override_deps(app, mock_job_service, mock_scraper_service)

        from app.models.models import Job
        mock_job = MagicMock(spec=Job)
        mock_job.id = 1
        mock_job.title = "Python Developer"
        mock_job.company_name = "TestCorp"
        mock_job.location = "Remote"
        mock_job.is_remote = True
        mock_job.location_type = "remote"
        mock_job.description = "Job description"
        mock_job.required_skills = ["Python"]
        mock_job.salary_min = 100000
        mock_job.salary_max = 150000
        mock_job.salary_currency = "USD"
        mock_job.salary_visible = True
        mock_job.employment_type = "full_time"
        mock_job.status = "active"
        mock_job.job_url = "https://example.com/job"
        mock_job.apply_url = None
        mock_job.company_description = None
        mock_job.company_url = None
        mock_job.company_logo = None
        mock_job.nice_to_have_skills = None
        mock_job.experience_min_years = None
        mock_job.experience_max_years = None
        mock_job.experience_level = None
        mock_job.education_required = None
        mock_job.degree_preferred = None
        mock_job.salary_period = None
        mock_job.remote_type = None
        mock_job.industry = None
        mock_job.function = None
        mock_job.department = None
        mock_job.application_deadline = None
        mock_job.posted_at = None
        mock_job.scraped_at = None
        mock_job.normalized_title = None
        mock_job.company_id_normalized = None
        mock_job.created_at = None
        mock_job.updated_at = None
        mock_job.external_id = None
        mock_job.source_id = None
        mock_job.requirements = None
        mock_job.responsibilities = None
        mock_job.__tablename__ = "jobs"

        mock_job_service.list_jobs = AsyncMock(return_value=([mock_job], 1))

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/jobs")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 1
            assert data["meta"]["total"] == 1

    @pytest.mark.asyncio
    async def test_get_job_found(self, app, mock_job_service, mock_scraper_service):
        """GET /jobs/{id} should return job if found."""
        _override_deps(app, mock_job_service, mock_scraper_service)

        from app.models.models import Job
        mock_job = MagicMock(spec=Job)
        mock_job.id = 1
        mock_job.title = "Python Developer"
        mock_job.company_name = "TestCorp"
        mock_job.location = "Remote"
        mock_job.is_remote = True
        mock_job.location_type = "remote"
        mock_job.description = "Job description"
        mock_job.required_skills = ["Python"]
        mock_job.salary_min = 100000
        mock_job.salary_max = 150000
        mock_job.salary_currency = "USD"
        mock_job.salary_visible = True
        mock_job.employment_type = "full_time"
        mock_job.status = "active"
        mock_job.job_url = "https://example.com/job"
        mock_job.apply_url = None
        mock_job.company_description = None
        mock_job.company_url = None
        mock_job.company_logo = None
        mock_job.nice_to_have_skills = None
        mock_job.experience_min_years = None
        mock_job.experience_max_years = None
        mock_job.experience_level = None
        mock_job.education_required = None
        mock_job.degree_preferred = None
        mock_job.salary_period = None
        mock_job.remote_type = None
        mock_job.industry = None
        mock_job.function = None
        mock_job.department = None
        mock_job.application_deadline = None
        mock_job.posted_at = None
        mock_job.scraped_at = None
        mock_job.normalized_title = None
        mock_job.company_id_normalized = None
        mock_job.created_at = None
        mock_job.updated_at = None
        mock_job.external_id = None
        mock_job.source_id = None
        mock_job.requirements = None
        mock_job.responsibilities = None
        mock_job.__tablename__ = "jobs"

        mock_job_service.get_job = AsyncMock(return_value=mock_job)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/jobs/1")
            assert response.status_code == 200
            assert response.json()["data"]["title"] == "Python Developer"

    @pytest.mark.asyncio
    async def test_get_job_not_found(self, app, mock_job_service, mock_scraper_service):
        """GET /jobs/{id} should return 404 if not found."""
        _override_deps(app, mock_job_service, mock_scraper_service)
        mock_job_service.get_job = AsyncMock(return_value=None)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/jobs/999")
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_job(self, app, mock_job_service, mock_scraper_service):
        """POST /jobs should create and return job."""
        _override_deps(app, mock_job_service, mock_scraper_service)

        from app.models.models import Job
        mock_job = MagicMock(spec=Job)
        mock_job.id = 1
        mock_job.title = "New Job"
        mock_job.company_name = "NewCorp"
        mock_job.location = "Remote"
        mock_job.is_remote = True
        mock_job.location_type = "remote"
        mock_job.description = None
        mock_job.required_skills = None
        mock_job.salary_min = None
        mock_job.salary_max = None
        mock_job.salary_currency = "USD"
        mock_job.salary_visible = False
        mock_job.employment_type = "full_time"
        mock_job.status = "active"
        mock_job.job_url = None
        mock_job.apply_url = None
        mock_job.company_description = None
        mock_job.company_url = None
        mock_job.company_logo = None
        mock_job.nice_to_have_skills = None
        mock_job.experience_min_years = None
        mock_job.experience_max_years = None
        mock_job.experience_level = None
        mock_job.education_required = None
        mock_job.degree_preferred = None
        mock_job.salary_period = None
        mock_job.remote_type = None
        mock_job.industry = None
        mock_job.function = None
        mock_job.department = None
        mock_job.application_deadline = None
        mock_job.posted_at = None
        mock_job.scraped_at = None
        mock_job.normalized_title = None
        mock_job.company_id_normalized = None
        mock_job.created_at = None
        mock_job.updated_at = None
        mock_job.external_id = None
        mock_job.source_id = None
        mock_job.requirements = None
        mock_job.responsibilities = None
        mock_job.__tablename__ = "jobs"

        mock_job_service.create_job = AsyncMock(return_value=mock_job)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/jobs",
                json={"title": "New Job", "company_name": "NewCorp"},
            )
            assert response.status_code == 201
            data = response.json()
            assert data["data"]["title"] == "New Job"

    @pytest.mark.asyncio
    async def test_update_job(self, app, mock_job_service, mock_scraper_service):
        """PUT /jobs/{id} should update and return job."""
        _override_deps(app, mock_job_service, mock_scraper_service)

        mock_job_service.update_job = AsyncMock(return_value=MagicMock(
            id=1, title="Updated", company_name="C", location="Remote",
            is_remote=True, location_type="remote", description=None,
            required_skills=None, salary_min=None, salary_max=None,
            salary_currency="USD", salary_visible=False, employment_type="full_time",
            status="active", job_url=None, apply_url=None,
            company_description=None, company_url=None, company_logo=None,
            nice_to_have_skills=None, experience_min_years=None, experience_max_years=None,
            experience_level=None, education_required=None, degree_preferred=None,
            salary_period=None, remote_type=None, industry=None, function=None,
            department=None, application_deadline=None, posted_at=None,
            scraped_at=None, normalized_title=None, company_id_normalized=None,
            created_at=None, updated_at=None, external_id=None, source_id=None,
            requirements=None, responsibilities=None,
            __tablename__="jobs",
        ))

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.put(
                "/jobs/1",
                json={"title": "Updated"},
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_job(self, app, mock_job_service, mock_scraper_service):
        """DELETE /jobs/{id} should soft-delete the job."""
        _override_deps(app, mock_job_service, mock_scraper_service)
        mock_job_service.delete_job = AsyncMock(return_value=True)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.delete("/jobs/1")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_job_not_found(self, app, mock_job_service, mock_scraper_service):
        """DELETE /jobs/{id} should return 404 if not found."""
        _override_deps(app, mock_job_service, mock_scraper_service)
        mock_job_service.delete_job = AsyncMock(return_value=False)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.delete("/jobs/999")
            assert response.status_code == 404


class TestRefreshEndpoint:
    """Tests for job refresh/scraping endpoints."""

    @pytest.mark.asyncio
    async def test_refresh_single_source(self, app, mock_job_service, mock_scraper_service):
        """POST /jobs/refresh?source=remoteok should scrape one source."""
        _override_deps(app, mock_job_service, mock_scraper_service)

        from app.scrapers.base import ScrapeResult
        mock_scraper_service.scrape_source = AsyncMock(return_value=ScrapeResult(
            source_name="remoteok",
            total_found=10,
            total_new=5,
            total_duplicates=4,
            total_errors=1,
            success=True,
        ))

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post("/jobs/refresh?source=remoteok")
            assert response.status_code == 200
            data = response.json()["data"]
            assert data["source"] == "remoteok"
            assert data["new"] == 5

    @pytest.mark.asyncio
    async def test_refresh_all_sources(self, app, mock_job_service, mock_scraper_service):
        """POST /jobs/refresh without source should scrape all."""
        _override_deps(app, mock_job_service, mock_scraper_service)

        from app.scrapers.base import ScrapeResult
        mock_scraper_service.scrape_all_active = AsyncMock(return_value={
            "remoteok": ScrapeResult(source_name="remoteok", total_new=5, success=True),
            "naukri": ScrapeResult(source_name="naukri", total_new=3, success=True),
        })

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post("/jobs/refresh")
            assert response.status_code == 200
            data = response.json()["data"]
            assert data["total_new"] == 8
            assert len(data["sources"]) == 2


class TestSourceEndpoints:
    """Tests for job source CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_list_sources(self, app, mock_job_service, mock_scraper_service):
        """GET /jobs/sources should return sources list."""
        _override_deps(app, mock_job_service, mock_scraper_service)
        mock_job_service.list_sources = AsyncMock(return_value=[])

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/jobs/sources")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_source(self, app, mock_job_service, mock_scraper_service):
        """POST /jobs/sources should create source."""
        _override_deps(app, mock_job_service, mock_scraper_service)

        from app.models.models import JobSource
        mock_source = MagicMock(spec=JobSource)
        mock_source.id = 1
        mock_source.name = "test_source"
        mock_source.source_type = "api"
        mock_source.display_name = "Test Source"
        mock_source.base_url = "https://example.com/api"
        mock_source.api_url = None
        mock_source.api_key_required = False
        mock_source.is_active = True
        mock_source.scrape_interval_minutes = 60
        mock_source.config = None
        mock_source.last_scraped_at = None
        mock_source.last_scrape_status = None
        mock_source.last_scrape_count = None
        mock_source.error_count = 0
        mock_source.priority = 100
        mock_source.created_at = None
        mock_source.updated_at = None
        mock_source.__tablename__ = "job_sources"

        mock_job_service.create_source = AsyncMock(return_value=mock_source)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/jobs/sources",
                json={
                    "name": "test_source",
                    "source_type": "api",
                    "display_name": "Test Source",
                    "base_url": "https://example.com/api",
                },
            )
            assert response.status_code == 201
            assert response.json()["data"]["name"] == "test_source"

    @pytest.mark.asyncio
    async def test_test_source(self, app, mock_job_service, mock_scraper_service):
        """POST /jobs/sources/{id}/test should test scraper connection."""
        _override_deps(app, mock_job_service, mock_scraper_service)

        from app.models.models import JobSource
        mock_source = MagicMock(spec=JobSource)
        mock_source.id = 1
        mock_source.name = "remoteok"
        mock_source.source_type = "api"
        mock_source.display_name = "RemoteOK"
        mock_source.base_url = "https://remoteok.com/api"
        mock_source.config = {}
        mock_source.__tablename__ = "job_sources"

        mock_job_service.get_source = AsyncMock(return_value=mock_source)

        from app.scrapers.base import ScrapeResult
        mock_scraper_service.scrape_source = AsyncMock(return_value=ScrapeResult(
            source_name="remoteok",
            total_found=3,
            success=True,
        ))

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post("/jobs/sources/1/test")
            assert response.status_code == 200
            assert response.json()["data"]["source"] == "remoteok"
