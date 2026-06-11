"""Tests for auth service business logic."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.models import AuthUser
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password(self):
        hashed = hash_password("test_password")
        assert hashed != "test_password"
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_password(self):
        hashed = hash_password("test_password")
        assert verify_password("test_password", hashed) is True
        assert verify_password("wrong_password", hashed) is False


class TestJWT:
    """Test JWT creation and decoding."""

    def test_create_access_token(self):
        token = create_access_token({"sub": "user-123"})
        assert token is not None
        assert isinstance(token, str)

    def test_decode_valid_token(self):
        token = create_access_token({"sub": "user-123"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"
        assert payload["type"] == "access"

    def test_decode_expired_token(self):
        from datetime import timedelta

        token = create_access_token(
            {"sub": "user-123"},
            expires_delta=timedelta(seconds=-1),
        )
        payload = decode_token(token)
        assert payload is None

    def test_decode_invalid_token(self):
        payload = decode_token("invalid.token.here")
        assert payload is None


class TestAuthService:
    """Test AuthService business logic."""

    @pytest.mark.asyncio
    async def test_register_user(self, auth_service: AuthService):
        request = RegisterRequest(
            email="newuser@example.com",
            password="SecurePass123!",
            display_name="New User",
        )
        user = await auth_service.register(request)
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.display_name == "New User"
        assert user.is_verified is False
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, auth_service: AuthService):
        request = RegisterRequest(
            email="dupe@example.com",
            password="SecurePass123!",
            display_name="User 1",
        )
        await auth_service.register(request)

        with pytest.raises(ValueError, match="Email already registered"):
            await auth_service.register(request)

    @pytest.mark.asyncio
    async def test_authenticate_success(self, auth_service: AuthService):
        email = "login@example.com"
        password = "MyPassword123!"
        await auth_service.register(
            RegisterRequest(email=email, password=password, display_name="Login User")
        )

        user = await auth_service.authenticate(LoginRequest(email=email, password=password))
        assert user is not None
        assert user.email == email

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self, auth_service: AuthService):
        email = "wrongpass@example.com"
        await auth_service.register(
            RegisterRequest(
                email=email, password="CorrectPass123!", display_name="User"
            )
        )

        user = await auth_service.authenticate(
            LoginRequest(email=email, password="WrongPass123!")
        )
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_nonexistent_email(self, auth_service: AuthService):
        user = await auth_service.authenticate(
            LoginRequest(email="nobody@example.com", password="anything")
        )
        assert user is None

    @pytest.mark.asyncio
    async def test_get_by_email(self, auth_service: AuthService):
        email = "findme@example.com"
        await auth_service.register(
            RegisterRequest(
                email=email, password="Pass123!", display_name="Find Me"
            )
        )

        found = await auth_service.get_by_email(email)
        assert found is not None
        assert found.email == email

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, auth_service: AuthService):
        found = await auth_service.get_by_email("missing@example.com")
        assert found is None

    @pytest.mark.asyncio
    async def test_change_password(self, auth_service: AuthService, db_session: AsyncSession):
        request = RegisterRequest(
            email="changepass@example.com",
            password="OldPass123!",
            display_name="Change Pass",
        )
        user = await auth_service.register(request)

        from app.schemas.auth import ChangePasswordRequest

        result = await auth_service.change_password(
            user,
            ChangePasswordRequest(
                current_password="OldPass123!",
                new_password="NewPass456!",
            ),
        )
        assert result is True

        # Verify new password works
        auth_result = await auth_service.authenticate(
            LoginRequest(email="changepass@example.com", password="NewPass456!")
        )
        assert auth_result is not None

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, auth_service: AuthService):
        request = RegisterRequest(
            email="wrongcurrent@example.com",
            password="OldPass123!",
            display_name="Wrong Current",
        )
        user = await auth_service.register(request)

        from app.schemas.auth import ChangePasswordRequest

        result = await auth_service.change_password(
            user,
            ChangePasswordRequest(
                current_password="WrongOldPass!",
                new_password="NewPass456!",
            ),
        )
        assert result is False
