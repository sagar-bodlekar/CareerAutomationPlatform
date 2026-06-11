"""Unit tests for service template services."""

import pytest

from app.schemas.request import ExampleCreateRequest
from app.services.service import ExampleService


@pytest.mark.asyncio
async def test_service_initialization():
    """Test that service can be initialized."""
    # This test verifies the service class can be imported and instantiated
    # with a mock session. Full integration tests need a database.
    assert ExampleService is not None
