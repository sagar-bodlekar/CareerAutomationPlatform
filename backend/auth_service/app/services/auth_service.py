"""Auth service — registration, login, password management."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token, hash_password, verify_password
from app.core.tokens import token_manager
from app.models.models import AuthUser
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
)


class AuthService:
    """Service for user authentication flows."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ─── Registration ──────────────────────────────────────

    async def register(self, request: RegisterRequest) -> AuthUser:
        """Register a new user.

        Raises:
            ValueError: If the email is already registered.
        """
        # Check for existing user
        existing = await self.get_by_email(request.email)
        if existing:
            raise ValueError("Email already registered")

        user = AuthUser(
            id=uuid.uuid4(),
            email=request.email,
            password_hash=hash_password(request.password),
            display_name=request.display_name,
            is_verified=False,
            is_active=True,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    # ─── Login ─────────────────────────────────────────────

    async def authenticate(self, request: LoginRequest) -> AuthUser | None:
        """Authenticate a user by email and password.

        Returns the user if credentials match, else ``None``.
        Also updates ``last_login_at``.
        """
        user = await self.get_by_email(request.email)
        if user is None:
            return None
        if not user.is_active:
            return None
        if not verify_password(request.password, user.password_hash):
            return None

        user.last_login_at = datetime.now(timezone.utc)
        await self.session.flush()
        return user

    # ─── Password Management ───────────────────────────────

    async def change_password(
        self, user: AuthUser, request: ChangePasswordRequest
    ) -> bool:
        """Change a user's password.

        Returns ``True`` if the password was changed, ``False`` if the
        current password doesn't match.
        """
        if not verify_password(request.current_password, user.password_hash):
            return False

        user.password_hash = hash_password(request.new_password)
        await self.session.flush()
        return True

    async def initiate_password_reset(self, email: str) -> str | None:
        """Generate a password reset token for the given email.

        Returns the reset token, or ``None`` if the email is not found.
        """
        user = await self.get_by_email(email)
        if user is None:
            return None

        from app.core.security import create_access_token
        from datetime import timedelta

        token = create_access_token(
            data={"sub": str(user.id), "purpose": "password_reset"},
            expires_delta=timedelta(hours=1),
        )
        return token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset a user's password using a reset token.

        Returns ``True`` on success, ``False`` if the token is invalid.
        """
        payload = decode_token(token)
        if payload is None or payload.get("purpose") != "password_reset":
            return False

        user_id = payload.get("sub")
        if user_id is None:
            return False

        result = await self.session.execute(
            select(AuthUser).where(AuthUser.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()
        if user is None:
            return False

        user.password_hash = hash_password(new_password)
        await self.session.flush()
        return True

    # ─── Email Verification ────────────────────────────────

    async def verify_email(self, token: str) -> bool:
        """Verify a user's email address using a verification token.

        Returns ``True`` on success, ``False`` if the token is invalid.
        """
        payload = decode_token(token)
        if payload is None or payload.get("purpose") != "email_verification":
            return False

        user_id = payload.get("sub")
        if user_id is None:
            return False

        result = await self.session.execute(
            select(AuthUser).where(AuthUser.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()
        if user is None:
            return False

        user.is_verified = True
        await self.session.flush()
        return True

    def generate_email_verification_token(self, user: AuthUser) -> str:
        """Generate an email verification token for a user."""
        from app.core.security import create_access_token
        from datetime import timedelta

        return create_access_token(
            data={
                "sub": str(user.id),
                "purpose": "email_verification",
                "email": user.email,
            },
            expires_delta=timedelta(days=7),
        )

    # ─── Helpers ───────────────────────────────────────────

    async def get_by_email(self, email: str) -> AuthUser | None:
        """Look up a user by email."""
        result = await self.session.execute(
            select(AuthUser).where(AuthUser.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> AuthUser | None:
        """Look up a user by ID."""
        return await self.session.get(AuthUser, user_id)
