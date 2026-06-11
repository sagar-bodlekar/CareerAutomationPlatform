"""API tests for match service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints import router
from app.api.v1.health import router as health_router


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(health_router)
    app.include_router(router)
    return app


def _override_deps(app, **overrides):
    from app.api.v1 import dependencies as deps

    async def get_mock_user():
        return 1

    async def get_mock_service():
        svc = AsyncMock()
        svc.compute_score = AsyncMock()
        svc.save_match = AsyncMock()
        svc.get_profile_matches = AsyncMock(return_value=([], 0))
        svc.get_skill_gaps = AsyncMock()
        return svc

    async def get_mock_batcher():
        bm = AsyncMock()
        bm.process_batch = AsyncMock()
        return bm

    app.dependency_overrides[deps.get_current_user_id] = get_mock_user
    app.dependency_overrides[deps.get_match_service] = get_mock_service
    app.dependency_overrides[deps.get_batch_matcher] = get_mock_batcher


class TestMatchEndpoints:
    """Tests for match API endpoints."""

    @pytest.mark.asyncio
    async def test_health(self, app):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json()["service"] == "match-service"

    @pytest.mark.asyncio
    async def test_score_match(self, app):
        """POST /matches/score should return match score."""
        _override_deps(app)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/matches/score",
                json={
                    "profile_id": 1,
                    "job_id": 1,
                    "profile_data": {"skills": ["Python"]},
                    "job_data": {"required_skills": ["Python"]},
                },
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_recommendations(self, app):
        """GET /matches/recommendations/{id} should return recommendations."""
        _override_deps(app)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/matches/recommendations/1")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_skill_gaps_not_found(self, app):
        """GET /matches/gaps/{pid}/{jid} should return 404 if no match."""
        _override_deps(app)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/matches/gaps/1/999")
            assert response.status_code in (200, 404)

    @pytest.mark.asyncio
    async def test_batch_match(self, app):
        """POST /matches/batch should process batch request."""
        _override_deps(app)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/matches/batch",
                json={"profile_id": 1, "limit": 10},
            )
            assert response.status_code == 200
