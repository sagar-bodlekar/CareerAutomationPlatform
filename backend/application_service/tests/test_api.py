"""API tests for Application Service."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test that health endpoint returns OK."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_create_application(client: AsyncClient):
    """Test creating an application draft (real service with mock session)."""
    response = await client.post(
        "/api/v1/applications",
        json={
            "profile_id": 1,
            "job_id": 100,
            "company_name": "Tech Corp",
            "job_title": "Software Engineer",
            "job_location": "Remote",
            "match_score": 85.0,
        },
    )
    assert response.status_code == 201
    data = response.json()
    body = data.get("data", data)
    assert body.get("id") is not None
    assert body.get("status") == "draft"
    assert body.get("progress_percentage") == 0


@pytest.mark.asyncio
async def test_get_application_not_found(client: AsyncClient):
    """Test that non-existent application returns 404."""
    response = await client.get("/api/v1/applications/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_applications(client: AsyncClient):
    """Test listing applications with filters."""
    response = await client.get("/api/v1/applications?profile_id=1")
    assert response.status_code == 200
    # Response should contain data (could be wrapped in APIResponse or flat)
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_submit_application_not_found(client: AsyncClient):
    """Test submitting a non-existent application returns 404."""
    response = await client.post("/api/v1/applications/999/submit")
    assert response.status_code == 404
