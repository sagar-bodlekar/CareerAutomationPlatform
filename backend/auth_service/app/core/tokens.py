"""Token management — creation, validation, and blacklisting."""

from datetime import timedelta
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TokenManager:
    """Manages JWT access and refresh tokens with Redis blacklisting."""

    def __init__(self) -> None:
        self._redis: aioredis.Redis | None = None

    async def _get_redis(self) -> aioredis.Redis:
        """Lazy-init Redis connection."""
        if self._redis is None:
            self._redis = aioredis.from_url(
                settings.redis_url, decode_responses=True
            )
        return self._redis

    async def create_token_pair(
        self, user_id: str, extra_claims: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Create an access + refresh token pair for a user.

        Args:
            user_id: The user's UUID string (used as ``sub``).
            extra_claims: Optional additional claims to embed.

        Returns:
            Dict with ``access_token``, ``refresh_token``, ``token_type``.
        """
        claims = {"sub": user_id}
        if extra_claims:
            claims.update(extra_claims)

        access_token = create_access_token(data=claims)
        refresh_token = create_refresh_token(data=claims)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_access_token(self, refresh_token: str) -> dict[str, Any] | None:
        """Issue a new access token from a valid refresh token.

        Returns a new token pair with rotated refresh token, or ``None``
        if the refresh token is invalid, expired, or blacklisted.
        """
        if await self.is_blacklisted(refresh_token):
            return None

        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # Blacklist the old refresh token (rotation)
        await self.blacklist_token(refresh_token)

        return await self.create_token_pair(user_id)

    async def blacklist_token(self, token: str, ttl_seconds: int | None = None) -> None:
        """Add a token to the Redis blacklist.

        Args:
            token: The JWT to blacklist.
            ttl_seconds: TTL override. Defaults to the token's remaining lifetime.
        """
        redis_conn = await self._get_redis()
        payload = decode_token(token)
        if payload and "exp" in payload:
            remaining = max(0, payload["exp"] - int((
                __import__("datetime").datetime.now(
                    __import__("datetime").timezone.utc
                ).timestamp()
            )))
            ttl = ttl_seconds or remaining
        else:
            ttl = ttl_seconds or 3600  # Default 1 hour

        await redis_conn.setex(f"token_blacklist:{token}", int(ttl), "1")

    async def is_blacklisted(self, token: str) -> bool:
        """Check if a token has been blacklisted."""
        redis_conn = await self._get_redis()
        return await redis_conn.exists(f"token_blacklist:{token}") > 0

    async def close(self) -> None:
        """Close the Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None


# Global singleton
token_manager = TokenManager()
