"""Test fixtures for Resume Service tests."""

import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import async_session_factory

from app.main import app
from app.services.resume_service import ResumeService
from app.services.template_service import TemplateService


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
async def resume_service(db_session: AsyncSession) -> ResumeService:
    """Create a ResumeService instance for testing."""
    return ResumeService(db_session)


@pytest_asyncio.fixture
async def template_service(db_session: AsyncSession) -> TemplateService:
    """Create a TemplateService instance for testing."""
    return TemplateService(db_session)


@pytest.fixture
def sample_user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def sample_profile_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def sample_resume_data(sample_user_id, sample_profile_id):
    return {
        "user_id": str(sample_user_id),
        "profile_id": str(sample_profile_id),
        "title": "Test Master Resume",
        "content": {
            "summary": "Experienced software engineer.",
            "skills": {"Language": [{"name": "Python", "proficient": True}]},
            "work_experiences": [],
            "education": [],
        },
    }
