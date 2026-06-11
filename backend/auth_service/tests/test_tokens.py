"""Tests for token management."""

import pytest

from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.tokens import token_manager


@pytest.mark.asyncio
async def test_create_token_pair():
    """Test creating access + refresh token pair."""
    pair = await token_manager.create_token_pair("user-123")
    assert "access_token" in pair
    assert "refresh_token" in pair
    assert pair["token_type"] == "bearer"

    # Decode both tokens
    access_payload = decode_token(pair["access_token"])
    refresh_payload = decode_token(pair["refresh_token"])
    assert access_payload is not None
    assert refresh_payload is not None
    assert access_payload["sub"] == "user-123"
    assert refresh_payload["sub"] == "user-123"
    assert access_payload["type"] == "access"
    assert refresh_payload["type"] == "refresh"


@pytest.mark.asyncio
async def test_refresh_access_token():
    """Test refreshing an access token from a refresh token."""
    pair = await token_manager.create_token_pair("user-456")
    new_pair = await token_manager.refresh_access_token(pair["refresh_token"])
    assert new_pair is not None
    assert new_pair["access_token"] != pair["access_token"]

    # Verify the new tokens decode correctly
    payload = decode_token(new_pair["access_token"])
    assert payload is not None
    assert payload["sub"] == "user-456"


@pytest.mark.asyncio
async def test_refresh_with_invalid_token():
    """Test refresh with an invalid token returns None."""
    result = await token_manager.refresh_access_token("invalid.token.here")
    assert result is None


@pytest.mark.asyncio
async def test_refresh_with_access_token():
    """Test refresh with an access token (not refresh) returns None."""
    access = create_access_token({"sub": "user-789"})
    result = await token_manager.refresh_access_token(access)
    assert result is None


@pytest.mark.asyncio
async def test_blacklist_token():
    """Test blacklisting a token."""
    pair = await token_manager.create_token_pair("user-blacklist")

    # Token should not be blacklisted yet
    is_blacklisted = await token_manager.is_blacklisted(pair["access_token"])
    assert is_blacklisted is False

    # Blacklist it
    await token_manager.blacklist_token(pair["access_token"])
    is_blacklisted = await token_manager.is_blacklisted(pair["access_token"])
    assert is_blacklisted is True


@pytest.mark.asyncio
async def test_refresh_rotates_token():
    """Test that refresh rotates (blacklists) the old refresh token."""
    pair = await token_manager.create_token_pair("user-rotate")
    old_refresh = pair["refresh_token"]

    # Refresh should succeed
    new_pair = await token_manager.refresh_access_token(old_refresh)
    assert new_pair is not None

    # Old refresh should now be blacklisted
    is_blacklisted = await token_manager.is_blacklisted(old_refresh)
    assert is_blacklisted is True


@pytest.mark.asyncio
async def test_create_token_pair_with_extra_claims():
    """Test creating a token pair with extra claims."""
    pair = await token_manager.create_token_pair(
        "user-claims", extra_claims={"role": "admin"}
    )

    payload = decode_token(pair["access_token"])
    assert payload is not None
    assert payload["sub"] == "user-claims"
    assert payload.get("role") == "admin"


@pytest.mark.asyncio
async def test_create_access_and_refresh_separately():
    """Test individual token creation functions."""
    access = create_access_token({"sub": "user-individual"})
    refresh = create_refresh_token({"sub": "user-individual"})

    access_payload = decode_token(access)
    refresh_payload = decode_token(refresh)

    assert access_payload is not None
    assert access_payload["type"] == "access"
    assert refresh_payload is not None
    assert refresh_payload["type"] == "refresh"
