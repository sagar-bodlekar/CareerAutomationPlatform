"""API tests for Tracking Service."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test that health endpoint returns OK."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_get_stats_invalid(client: AsyncClient):
    """Test stats endpoint requires profile_id."""
    response = await client.get("/api/v1/tracking/stats")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_analytics(client: AsyncClient):
    """Test analytics endpoint."""
    response = await client.get("/api/v1/tracking/analytics?profile_id=1")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_funnel(client: AsyncClient):
    """Test funnel endpoint."""
    response = await client.get("/api/v1/tracking/funnel?profile_id=1")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_trends(client: AsyncClient):
    """Test daily trends endpoint."""
    response = await client.get("/api/v1/tracking/trends?profile_id=1&days=7")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_tracking_applications(client: AsyncClient):
    """Test listing applications for tracking."""
    response = await client.get("/api/v1/tracking/applications?profile_id=1")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_export_json(client: AsyncClient):
    """Test JSON export endpoint."""
    response = await client.post("/api/v1/tracking/export?profile_id=1&format=json")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_export_csv(client: AsyncClient):
    """Test CSV export endpoint."""
    response = await client.post("/api/v1/tracking/export?profile_id=1&format=csv")
    assert response.status_code == 200
