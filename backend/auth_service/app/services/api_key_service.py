"""API key service — creation, validation, and revocation."""

import hashlib
import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import ApiKey, AuthUser


class ApiKeyService:
    """Service for managing API keys."""

    KEY_LENGTH = 48  # Total characters
    PREFIX_LENGTH = 8

    def __init__(self, session: AsyncSession):
        self.session = session

    def _generate_key(self) -> tuple[str, str, str]:
        """Generate a new API key.

        Returns:
            Tuple of ``(full_key, prefix, hashed_key)``.
        """
        raw = secrets.token_urlsafe(36)  # 48 chars
        prefix = raw[: self.PREFIX_LENGTH]
        hashed = hashlib.sha256(raw.encode()).hexdigest()
        return raw, prefix, hashed

    def _hash_key(self, key: str) -> str:
        """Hash an API key for secure storage."""
        return hashlib.sha256(key.encode()).hexdigest()

    async def create_key(
        self,
        user: AuthUser,
        name: str,
        scopes: str | None = None,
        expires_at: datetime | None = None,
    ) -> tuple[ApiKey, str]:
        """Create a new API key for a user.

        Returns:
            Tuple of ``(ApiKey, full_key)``. The full key is only returned
            once and cannot be retrieved later.
        """
        full_key, prefix, hashed = self._generate_key()

        api_key = ApiKey(
            id=uuid.uuid4(),
            user_id=user.id,
            key_prefix=prefix,
            key_hash=hashed,
            name=name,
            scopes=scopes,
            is_active=True,
            expires_at=expires_at,
        )
        self.session.add(api_key)
        await self.session.flush()
        return api_key, full_key

    async def validate_key(self, key: str) -> AuthUser | None:
        """Validate an API key and return the owning user.

        Returns the ``AuthUser`` if valid, or ``None`` if the key is
        invalid, expired, or revoked.
        """
        hashed = self._hash_key(key)

        result = await self.session.execute(
            select(ApiKey).where(ApiKey.key_hash == hashed)
        )
        api_key = result.scalar_one_or_none()

        if api_key is None:
            return None
        if not api_key.is_active:
            return None
        if api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
            return None

        # Update last used timestamp
        api_key.last_used_at = datetime.now(timezone.utc)
        await self.session.flush()

        user = await self.session.get(AuthUser, api_key.user_id)
        return user

    async def revoke_key(self, key_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Revoke an API key (soft delete by deactivating).

        Returns ``True`` if the key was revoked, ``False`` if not found.
        """
        result = await self.session.execute(
            select(ApiKey).where(
                ApiKey.id == key_id,
                ApiKey.user_id == user_id,
            )
        )
        api_key = result.scalar_one_or_none()
        if api_key is None:
            return False

        api_key.is_active = False
        await self.session.flush()
        return True

    async def list_keys(self, user_id: uuid.UUID) -> list[ApiKey]:
        """List all API keys for a user."""
        result = await self.session.execute(
            select(ApiKey)
            .where(ApiKey.user_id == user_id)
            .order_by(ApiKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_key(self, key_id: uuid.UUID, user_id: uuid.UUID) -> ApiKey | None:
        """Get a specific API key by ID."""
        result = await self.session.execute(
            select(ApiKey).where(
                ApiKey.id == key_id,
                ApiKey.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()
