"""Tests for Auth Service SQLAlchemy models."""

import uuid

from app.models.models import ApiKey, AuthUser, OAuthConnection


class TestAuthUser:
    """Test AuthUser model."""

    def test_create_user(self):
        user = AuthUser(
            id=uuid.uuid4(),
            email="user@example.com",
            password_hash="$2b$12$hashedpassword",
            display_name="Test User",
            is_active=True,
            is_verified=False,
        )
        assert user.id is not None
        assert user.email == "user@example.com"
        assert user.is_active is True
        assert user.is_verified is False

    def test_user_defaults(self):
        user = AuthUser(
            id=uuid.uuid4(),
            email="defaults@example.com",
            password_hash="hash",
            is_active=True,
            is_verified=False,
            is_superuser=False,
        )
        assert user.is_active is True
        assert user.is_verified is False
        assert user.is_superuser is False


class TestOAuthConnection:
    """Test OAuthConnection model."""

    def test_create_connection(self):
        user = AuthUser(email="oauth@example.com", password_hash="hash")
        conn = OAuthConnection(
            user=user,
            provider="google",
            provider_user_id="google-id-123",
            access_token="access-token-here",
        )
        assert conn.provider == "google"
        assert conn.provider_user_id == "google-id-123"
        assert conn.user_id == user.id

    def test_multiple_providers(self):
        user = AuthUser(email="multi@example.com", password_hash="hash")
        google = OAuthConnection(
            user=user,
            provider="google",
            provider_user_id="g-id",
            access_token="tok",
        )
        linkedin = OAuthConnection(
            user=user,
            provider="linkedin",
            provider_user_id="li-id",
            access_token="tok",
        )
        assert google.provider == "google"
        assert linkedin.provider == "linkedin"


class TestApiKey:
    """Test ApiKey model."""

    def test_create_api_key(self):
        user = AuthUser(id=uuid.uuid4(), email="apikey@example.com", password_hash="hash")
        key = ApiKey(
            user=user,
            user_id=user.id,
            key_prefix="cp_abc12",
            key_hash="sha256hash",
            name="Test Key",
            scopes="read,write",
            is_active=True,
        )
        assert key.key_prefix == "cp_abc12"
        assert key.name == "Test Key"
        assert key.is_active is True
        assert key.user_id == user.id

    def test_api_key_defaults(self):
        user = AuthUser(id=uuid.uuid4(), email="keydefaults@example.com", password_hash="hash")
        key = ApiKey(
            user=user,
            user_id=user.id,
            key_prefix="cp_test",
            key_hash="hash",
            name="Default Key",
            is_active=True,
        )
        assert key.is_active is True
        assert key.scopes is None
