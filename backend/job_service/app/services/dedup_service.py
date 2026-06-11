"""Deduplication service for job scraping.

Uses Redis with TTL to track recently seen job URLs and external IDs,
preventing duplicate job entries from being stored.
"""

import hashlib
import json
from typing import Optional

import redis.asyncio as aioredis

from ..core.config import settings, JOB_SERVICE_SETTINGS


class DeduplicationService:
    """Redis-backed dedup for job URLs and external IDs."""

    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self._redis = redis_client
        self._prefix = "job_dedup:"
        self._ttl_seconds = JOB_SERVICE_SETTINGS["dedup_redis_ttl_hours"] * 3600

    async def _get_redis(self) -> aioredis.Redis:
        """Lazy-initialize Redis connection."""
        if self._redis is None:
            self._redis = aioredis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
        return self._redis

    def _hash_url(self, url: str) -> str:
        """Create a deterministic hash from a URL."""
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def _hash_external_id(self, source: str, ext_id: str) -> str:
        """Create a deterministic hash from source + external_id."""
        return hashlib.sha256(f"{source}:{ext_id}".encode("utf-8")).hexdigest()

    async def is_duplicate_url(self, url: str) -> bool:
        """Check if a job URL has been seen recently."""
        if not url:
            return False
        r = await self._get_redis()
        key = f"{self._prefix}url:{self._hash_url(url)}"
        return bool(await r.exists(key))

    async def is_duplicate_external_id(self, source: str, external_id: str) -> bool:
        """Check if a source + external_id combination has been seen."""
        if not source or not external_id:
            return False
        r = await self._get_redis()
        key = f"{self._prefix}extid:{self._hash_external_id(source, external_id)}"
        return bool(await r.exists(key))

    async def mark_seen(self, url: str, source: str = "", external_id: str = "") -> None:
        """Mark a job URL and/or external ID as seen with TTL."""
        r = await self._get_redis()
        pipe = r.pipeline()

        if url:
            url_key = f"{self._prefix}url:{self._hash_url(url)}"
            pipe.setex(url_key, self._ttl_seconds, "1")

        if source and external_id:
            extid_key = f"{self._prefix}extid:{self._hash_external_id(source, external_id)}"
            pipe.setex(extid_key, self._ttl_seconds, "1")

        await pipe.execute()

    async def filter_new(self, jobs: list[dict], source: str = "") -> tuple[list[dict], int]:
        """Filter a list of jobs to only include new (non-duplicate) ones.

        Args:
            jobs: List of normalized job dicts.
            source: Source name for external_id dedup.

        Returns:
            Tuple of (new_jobs, duplicate_count).
        """
        new_jobs = []
        duplicate_count = 0

        for job in jobs:
            url = job.get("job_url", "") or job.get("apply_url", "")
            ext_id = job.get("external_id", "")

            if await self.is_duplicate_url(url):
                duplicate_count += 1
                continue

            if source and ext_id and await self.is_duplicate_external_id(source, ext_id):
                duplicate_count += 1
                continue

            new_jobs.append(job)

        return new_jobs, duplicate_count

    async def mark_batch_seen(self, jobs: list[dict], source: str = "") -> None:
        """Mark a batch of jobs as seen."""
        r = await self._get_redis()
        pipe = r.pipeline()

        for job in jobs:
            url = job.get("job_url", "") or job.get("apply_url", "")
            ext_id = job.get("external_id", "")

            if url:
                url_key = f"{self._prefix}url:{self._hash_url(url)}"
                pipe.setex(url_key, self._ttl_seconds, "1")

            if source and ext_id:
                extid_key = f"{self._prefix}extid:{self._hash_external_id(source, ext_id)}"
                pipe.setex(extid_key, self._ttl_seconds, "1")

        await pipe.execute()

    async def clear(self) -> None:
        """Clear all dedup keys (for testing)."""
        r = await self._get_redis()
        cursor = 0
        while True:
            cursor, keys = await r.scan(cursor, match=f"{self._prefix}*")
            if keys:
                await r.delete(*keys)
            if cursor == 0:
                break

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
