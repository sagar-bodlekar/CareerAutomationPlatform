"""Test fixtures for Tracking Service tests."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock

from shared.database import get_session

from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def mock_dependencies():
    """Override FastAPI dependencies with mocks for all tests."""
    mock_session = AsyncMock()

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
    mock_session.refresh = AsyncMock()

    async def override_get_session():
        return mock_session

    overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = override_get_session
    yield mock_session
    app.dependency_overrides = overrides
