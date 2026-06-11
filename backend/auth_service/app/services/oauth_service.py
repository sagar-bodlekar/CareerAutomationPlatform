"""OAuth service — third-party authentication provider integration."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import AuthUser, OAuthConnection


class OAuthService:
    """Service for managing OAuth provider connections."""

    PROVIDERS = {"google", "linkedin", "github"}

    def __init__(self, session: AsyncSession):
        self.session = session

    async def connect_provider(
        self,
        user: AuthUser,
        provider: str,
        provider_user_id: str,
        access_token: str,
        refresh_token: str | None = None,
        expires_at: datetime | None = None,
    ) -> OAuthConnection:
        """Connect an OAuth provider to a user account.

        If the connection already exists, updates the tokens.
        """
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")

        # Check for existing connection
        result = await self.session.execute(
            select(OAuthConnection).where(
                OAuthConnection.user_id == user.id,
                OAuthConnection.provider == provider,
            )
        )
        connection = result.scalar_one_or_none()

        if connection:
            # Update existing connection
            connection.access_token = access_token
            if refresh_token:
                connection.refresh_token = refresh_token
            if expires_at:
                connection.expires_at = expires_at
        else:
            # Create new connection
            connection = OAuthConnection(
                id=uuid.uuid4(),
                user_id=user.id,
                provider=provider,
                provider_user_id=provider_user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )
            self.session.add(connection)

        await self.session.flush()
        return connection

    async def get_connection(
        self, user_id: uuid.UUID, provider: str
    ) -> OAuthConnection | None:
        """Get a user's OAuth connection for a specific provider."""
        result = await self.session.execute(
            select(OAuthConnection).where(
                OAuthConnection.user_id == user_id,
                OAuthConnection.provider == provider,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_connections(
        self, user_id: uuid.UUID
    ) -> list[OAuthConnection]:
        """Get all OAuth connections for a user."""
        result = await self.session.execute(
            select(OAuthConnection).where(OAuthConnection.user_id == user_id)
        )
        return list(result.scalars().all())

    async def disconnect_provider(
        self, user_id: uuid.UUID, provider: str
    ) -> bool:
        """Disconnect an OAuth provider from a user account."""
        connection = await self.get_connection(user_id, provider)
        if connection is None:
            return False
        await self.session.delete(connection)
        await self.session.flush()
        return True

    async def find_or_create_from_oauth(
        self,
        provider: str,
        provider_user_id: str,
        email: str,
        display_name: str | None = None,
    ) -> tuple[AuthUser, bool]:
        """Find an existing user by OAuth connection, or create a new one.

        Returns:
            Tuple of ``(AuthUser, created)`` where ``created`` is ``True``
            if a new user was registered.
        """
        # Try to find existing connection
        result = await self.session.execute(
            select(OAuthConnection).where(
                OAuthConnection.provider == provider,
                OAuthConnection.provider_user_id == provider_user_id,
            )
        )
        connection = result.scalar_one_or_none()

        if connection:
            user = await self.session.get(AuthUser, connection.user_id)
            if user:
                return user, False

        # Try to find by email
        result = await self.session.execute(
            select(AuthUser).where(AuthUser.email == email)
        )
        user = result.scalar_one_or_none()

        if user:
            # Link OAuth to existing user
            await self.connect_provider(
                user=user,
                provider=provider,
                provider_user_id=provider_user_id,
                access_token="",  # Will be updated after OAuth callback
            )
            return user, False

        # Create new user
        import secrets

        random_password = secrets.token_urlsafe(32)
        from app.core.security import hash_password

        user = AuthUser(
            id=uuid.uuid4(),
            email=email,
            password_hash=hash_password(random_password),
            display_name=display_name or email.split("@")[0],
            is_verified=True,  # Email verified by OAuth provider
            is_active=True,
        )
        self.session.add(user)
        await self.session.flush()

        await self.connect_provider(
            user=user,
            provider=provider,
            provider_user_id=provider_user_id,
            access_token="",
        )
        return user, True
