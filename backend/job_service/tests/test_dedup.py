"""Tests for job deduplication service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.dedup_service import DeduplicationService


class TestDeduplicationService:
    """Tests for DeduplicationService."""

    @pytest.fixture
    def dedup(self):
        """Create dedup service with mocked Redis."""
        redis_mock = AsyncMock()
        redis_mock.exists = AsyncMock(return_value=False)
        redis_mock.setex = AsyncMock()
        redis_mock.pipeline = MagicMock()
        pipe = AsyncMock()
        pipe.setex = AsyncMock()
        pipe.execute = AsyncMock()
        redis_mock.pipeline.return_value = pipe
        service = DeduplicationService(redis_client=redis_mock)
        return service

    @pytest.mark.asyncio
    async def test_is_duplicate_url_new(self, dedup):
        """New URL should not be a duplicate."""
        dedup._redis.exists.return_value = False
        result = await dedup.is_duplicate_url("https://example.com/job")
        assert result is False

    @pytest.mark.asyncio
    async def test_is_duplicate_url_existing(self, dedup):
        """Existing URL should be detected as duplicate."""
        dedup._redis.exists.return_value = True
        result = await dedup.is_duplicate_url("https://example.com/job")
        assert result is True

    @pytest.mark.asyncio
    async def test_is_duplicate_url_empty(self, dedup):
        """Empty URL should not be a duplicate."""
        result = await dedup.is_duplicate_url("")
        assert result is False

    @pytest.mark.asyncio
    async def test_is_duplicate_external_id_new(self, dedup):
        """New external ID should not be duplicate."""
        dedup._redis.exists.return_value = False
        result = await dedup.is_duplicate_external_id("remoteok", "job123")
        assert result is False

    @pytest.mark.asyncio
    async def test_is_duplicate_external_id_existing(self, dedup):
        """Existing external ID should be detected."""
        dedup._redis.exists.return_value = True
        result = await dedup.is_duplicate_external_id("remoteok", "job123")
        assert result is True

    @pytest.mark.asyncio
    async def test_mark_seen(self, dedup):
        """Mark seen should store with TTL."""
        await dedup.mark_seen(
            url="https://example.com/job",
            source="remoteok",
            external_id="job123",
        )
        pipe = dedup._redis.pipeline.return_value
        assert pipe.setex.call_count == 2
        pipe.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_seen_url_only(self, dedup):
        """Mark seen with only URL should store one key."""
        await dedup.mark_seen(url="https://example.com/job")
        pipe = dedup._redis.pipeline.return_value
        assert pipe.setex.call_count == 1

    @pytest.mark.asyncio
    async def test_filter_new_all_new(self, dedup):
        """Filter new should return all jobs when none are duplicates."""
        dedup._redis.exists.return_value = False
        jobs = [
            {"job_url": "https://example.com/job1", "external_id": "src1"},
            {"job_url": "https://example.com/job2", "external_id": "src2"},
        ]
        new_jobs, dup_count = await dedup.filter_new(jobs, source="test")
        assert len(new_jobs) == 2
        assert dup_count == 0

    @pytest.mark.asyncio
    async def test_filter_new_all_duplicates(self, dedup):
        """Filter new should return empty when all are duplicates."""
        dedup._redis.exists.return_value = True
        jobs = [
            {"job_url": "https://example.com/job1", "external_id": "src1"},
            {"job_url": "https://example.com/job2", "external_id": "src2"},
        ]
        new_jobs, dup_count = await dedup.filter_new(jobs, source="test")
        assert len(new_jobs) == 0
        assert dup_count == 2

    @pytest.mark.asyncio
    async def test_filter_new_mixed(self, dedup):
        """Filter new should handle mixed new and duplicate jobs."""
        dedup._redis.exists.side_effect = [True, False]  # First is dup, second is new
        jobs = [
            {"job_url": "https://example.com/job1", "external_id": "src1"},
            {"job_url": "https://example.com/job2", "external_id": "src2"},
        ]
        new_jobs, dup_count = await dedup.filter_new(jobs, source="test")
        assert len(new_jobs) == 1
        assert dup_count == 1

    @pytest.mark.asyncio
    async def test_mark_batch_seen(self, dedup):
        """Batch mark seen should store all keys."""
        jobs = [
            {"job_url": "https://example.com/job1", "external_id": "1"},
            {"job_url": "https://example.com/job2", "external_id": "2"},
        ]
        await dedup.mark_batch_seen(jobs, source="test")
        pipe = dedup._redis.pipeline.return_value
        assert pipe.setex.call_count == 4  # 2 URLs + 2 external IDs
        pipe.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_hash_consistency(self, dedup):
        """Same URL should produce same hash."""
        hash1 = dedup._hash_url("https://example.com/job")
        hash2 = dedup._hash_url("https://example.com/job")
        assert hash1 == hash2

    @pytest.mark.asyncio
    async def test_clear(self, dedup):
        """Clear should delete all dedup keys."""
        dedup._redis.scan = AsyncMock(return_value=(0, ["key1", "key2"]))
        dedup._redis.delete = AsyncMock()
        await dedup.clear()
        dedup._redis.delete.assert_called_once_with("key1", "key2")
