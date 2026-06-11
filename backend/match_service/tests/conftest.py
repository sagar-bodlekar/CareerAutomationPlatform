"""Test fixtures for match service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_db_session():
    """Create a mock async database session."""
    session = AsyncMock(spec=AsyncMock)
    session.flush = AsyncMock()
    return session


@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing."""
    return {
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "React", "TypeScript"],
        "location": "Remote",
        "experience_years": 5,
        "experience_level": "senior",
        "education": ["BS Computer Science"],
        "titles": ["Senior Software Engineer", "Full Stack Developer"],
        "current_title": "Senior Software Engineer",
    }


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        "title": "Senior Python Backend Developer",
        "company_name": "TechCorp",
        "location": "Remote",
        "is_remote": True,
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        "nice_to_have_skills": ["Kubernetes", "Redis"],
        "experience_min_years": 3,
        "experience_max_years": 7,
        "experience_level": "senior",
        "education_required": "BS Computer Science",
        "degree_preferred": "MS Computer Science",
        "employment_type": "full_time",
    }
