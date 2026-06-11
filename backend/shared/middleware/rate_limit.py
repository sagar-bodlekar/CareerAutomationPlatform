"""Redis-backed rate limiting middleware for FastAPI applications."""

import time
import logging
from typing import Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """Redis-backed sliding window rate limiter.

    Requires redis to be available. Falls back to no-op if redis is unavailable.
    """

    def __init__(
        self,
        app: FastAPI,
        redis_url: str = "redis://localhost:6379/0",
        default_limit: int = 100,
        default_window: int = 60,  # seconds
        burst_limit: int = 20,
    ):
        self.app = app
        self.redis_url = redis_url
        self.default_limit = default_limit
        self.default_window = default_window
        self.burst_limit = burst_limit
        self._redis: Optional["redis.Redis"] = None  # type: ignore

    def _get_redis(self):
        if self._redis is None:
            try:
                import redis.asyncio as aioredis
                self._redis = aioredis.from_url(self.redis_url, decode_responses=True)
            except Exception as e:
                logger.warning("Rate limiting disabled: redis unavailable: %s", e)
                return None
        return self._redis

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        path = scope.get("path", "/unknown")

        # Skip rate limiting for metrics and health
        if path in ("/metrics", "/health"):
            return await self.app(scope, receive, send)

        client_ip = scope.get("client", ("127.0.0.1", 0))[0]
        key = f"ratelimit:{client_ip}:{path}"

        r = self._get_redis()
        if r is None:
            return await self.app(scope, receive, send)

        try:
            now = time.time()
            window_start = now - self.default_window

            # Remove old entries and count current
            await r.zremrangebyscore(key, 0, window_start)
            count = await r.zcard(key)

            if count >= self.default_limit:
                response = JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests",
                        "retry_after": self.default_window,
                    },
                    headers={"Retry-After": str(self.default_window)},
                )
                return await response(scope, receive, send)

            # Add current request
            await r.zadd(key, {f"{now}:{id(scope)}": now})
            await r.expire(key, self.default_window * 2)

        except Exception as e:
            logger.warning("Rate limit check failed: %s", e)

        return await self.app(scope, receive, send)
