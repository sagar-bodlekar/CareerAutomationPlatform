"""Test fixtures for job service."""

from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from shared.database import Base, get_session


@pytest.fixture
def mock_db_session():
    """Create a mock async database session."""
    session = AsyncMock(spec=AsyncSession)
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def sample_job_data():
    """Sample normalized job data for testing."""
    return {
        "external_id": "remoteok_test123",
        "title": "Senior Python Developer",
        "company_name": "TestCorp",
        "location": "Remote",
        "location_type": "remote",
        "is_remote": True,
        "description": "We are looking for a Senior Python Developer...",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "salary_min": 120000,
        "salary_max": 180000,
        "salary_currency": "USD",
        "employment_type": "full_time",
        "job_url": "https://example.com/jobs/senior-python-dev",
        "status": "active",
    }


@pytest.fixture
def sample_job_data_2():
    """Another sample job for dedup testing."""
    return {
        "external_id": "remoteok_test456",
        "title": "Junior React Developer",
        "company_name": "StartupXYZ",
        "location": "Remote",
        "location_type": "remote",
        "is_remote": True,
        "description": "Looking for a React developer...",
        "required_skills": ["React", "TypeScript", "CSS"],
        "salary_min": 70000,
        "salary_max": 100000,
        "salary_currency": "USD",
        "employment_type": "full_time",
        "job_url": "https://example.com/jobs/junior-react-dev",
        "status": "active",
    }


@pytest.fixture
def sample_source_data():
    """Sample job source data."""
    return {
        "name": "remoteok",
        "source_type": "api",
        "display_name": "RemoteOK",
        "base_url": "https://remoteok.com/api",
        "is_active": True,
        "scrape_interval_minutes": 60,
        "priority": 10,
    }


@pytest.fixture
def mock_remoteok_response():
    """Mock RemoteOK API response."""
    return [
        {
            "id": "12345",
            "slug": "senior-python-developer",
            "position": "Senior Python Developer",
            "company": "TestCorp",
            "description": "Looking for a Python expert...",
            "tags": ["python", "fastapi", "postgresql", "docker"],
            "salary": "$120k-$180k",
            "date": "2026-06-10T00:00:00Z",
            "url": "https://remoteok.com/remote-jobs/senior-python-developer",
        }
    ]


@pytest.fixture
def mock_httpx_response():
    """Create a mock httpx response."""
    def _create(status_code=200, json_data=None, text=""):
        mock = MagicMock()
        mock.status_code = status_code
        mock.json.return_value = json_data or []
        mock.text = text
        mock.raise_for_status = MagicMock()
        if status_code >= 400:
            mock.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
        return mock
    return _create
