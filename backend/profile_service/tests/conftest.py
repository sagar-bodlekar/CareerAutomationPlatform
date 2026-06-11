"""Test fixtures for Profile Service tests."""

import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import async_session_factory

from app.main import app
from app.services.profile_service import ProfileService


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def profile_service(db_session: AsyncSession) -> ProfileService:
    """Create a ProfileService instance for testing."""
    return ProfileService(db_session)


@pytest.fixture
def sample_user_id() -> uuid.UUID:
    """Sample user ID for testing."""
    return uuid.uuid4()


@pytest.fixture
def sample_profile_data():
    """Sample profile create data."""
    return {
        "user_id": str(uuid.uuid4()),
        "profile": {
            "headline": "Senior Software Engineer",
            "summary": "Experienced full-stack developer with 8+ years.",
            "location_city": "San Francisco",
            "location_country": "USA",
            "location_type": "remote",
            "preferred_roles": ["Software Engineer", "Tech Lead"],
            "target_salary_min": 150000,
            "target_salary_max": 200000,
            "open_to_work": True,
            "years_of_experience": 8.0,
            "personal_info": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "+1-555-0100",
                "city": "San Francisco",
                "country": "USA",
            },
            "skills": [
                {"name": "Python", "category": "Language", "proficiency": "expert", "years_used": 8},
                {"name": "React", "category": "Framework", "proficiency": "advanced", "years_used": 5},
                {"name": "PostgreSQL", "category": "Database", "proficiency": "advanced", "years_used": 6},
            ],
            "social_links": [
                {"platform": "github", "url": "https://github.com/johndoe", "is_primary": True},
                {"platform": "linkedin", "url": "https://linkedin.com/in/johndoe"},
            ],
        },
    }
