"""Redis caching utilities for application data."""

import json
import logging
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis-backed cache for frequently accessed data.

    Usage:
        cache = RedisCache("redis://localhost:6379/0")

        # Cache a value
        await cache.set("key", {"data": 123}, ttl=300)

        # Get cached value
        value = await cache.get("key")

        # Use as decorator
        @cache.cached(ttl=60)
        async def get_expensive_data(user_id: int):
            return await fetch_from_db(user_id)
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self._redis: Optional[Any] = None
        self._enabled = True

    def _get_redis(self):
        if self._redis is None and self._enabled:
            try:
                import redis.asyncio as aioredis
                self._redis = aioredis.from_url(self.redis_url, decode_responses=True)
            except Exception as e:
                logger.warning("Redis cache disabled: %s", e)
                self._enabled = False
        return self._redis

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        r = self._get_redis()
        if r is None:
            return None
        try:
            data = await r.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning("Cache get failed: %s", e)
        return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set a value in cache with TTL in seconds."""
        r = self._get_redis()
        if r is None:
            return False
        try:
            await r.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.warning("Cache set failed: %s", e)
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        r = self._get_redis()
        if r is None:
            return False
        try:
            await r.delete(key)
            return True
        except Exception as e:
            logger.warning("Cache delete failed: %s", e)
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern.

        Args:
            pattern: Redis glob pattern (e.g., "profile:*")

        Returns:
            Number of keys invalidated.
        """
        r = self._get_redis()
        if r is None:
            return 0
        try:
            keys = await r.keys(pattern)
            if keys:
                return await r.delete(*keys)
            return 0
        except Exception as e:
            logger.warning("Cache pattern invalidation failed: %s", e)
            return 0

    def cached(self, ttl: int = 300, key_prefix: str = ""):
        """Decorator to cache async function results.

        Args:
            ttl: Cache TTL in seconds.
            key_prefix: Optional prefix for cache key.

        Usage:
            @cache.cached(ttl=60)
            async def get_profile(profile_id: int):
                ...
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                r = self._get_redis()
                if r is None:
                    return await func(*args, **kwargs)

                # Build cache key from function name and arguments
                key_parts = [key_prefix or func.__name__]
                key_parts.extend(str(a) for a in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)

                # Try cache
                cached = await self.get(cache_key)
                if cached is not None:
                    return cached

                # Compute and cache
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl=ttl)
                return result

            return wrapper

        return decorator
