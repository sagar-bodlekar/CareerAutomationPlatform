"""Test fixtures for Application Service tests."""

import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from shared.database import get_session

from app.main import app

_counter = 0


def _make_mock_session():
    """Create a properly configured mock DB session."""
    mock_session = AsyncMock()

    # Set up execute to return a result with proper chain
    async def mock_execute(*args, **kwargs):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        mock_result.scalars.return_value = scalars_mock
        mock_result.scalar.return_value = 0

        return mock_result

    mock_session.execute = mock_execute
    mock_session.flush = AsyncMock()
    mock_session.add = MagicMock()

    # Refresh: set auto-incrementing ID and default values on models
    async def mock_refresh(obj):
        global _counter
        _counter += 1
        obj.id = _counter
        # Set defaults for common model fields
        if hasattr(obj, 'retry_count') and getattr(obj, 'retry_count', None) is None:
            obj.retry_count = 0
        if hasattr(obj, 'status') and getattr(obj, 'status', None) is None:
            obj.status = 'draft'

    mock_session.refresh = AsyncMock(side_effect=mock_refresh)
    return mock_session


@pytest_asyncio.fixture(autouse=True)
async def mock_dependencies():
    """Override FastAPI dependencies with mocks for all tests."""
    mock_session = _make_mock_session()

    async def override_get_session():
        return mock_session

    overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = override_get_session
    yield mock_session
    app.dependency_overrides = overrides


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with mocked dependencies."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
