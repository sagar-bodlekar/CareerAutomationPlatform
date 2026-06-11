"""Test fixtures for Auth Service tests."""

import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import async_session_factory

from app.main import app
from app.services.api_key_service import ApiKeyService
from app.services.auth_service import AuthService
from app.services.oauth_service import OAuthService


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
async def auth_service(db_session: AsyncSession) -> AuthService:
    """Create an AuthService instance for testing."""
    return AuthService(db_session)


@pytest_asyncio.fixture
async def api_key_service(db_session: AsyncSession) -> ApiKeyService:
    """Create an ApiKeyService instance for testing."""
    return ApiKeyService(db_session)


@pytest_asyncio.fixture
async def oauth_service(db_session: AsyncSession) -> OAuthService:
    """Create an OAuthService instance for testing."""
    return OAuthService(db_session)


@pytest.fixture
def sample_register_data():
    """Sample registration data."""
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "display_name": "Test User",
    }
