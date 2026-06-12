"""Unit tests for auth service."""

import pytest

from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_auth_service_import():
    """Test that AuthService can be imported."""
    assert AuthService is not None
