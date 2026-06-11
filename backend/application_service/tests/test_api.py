"""API tests for service template."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test that health endpoint returns OK."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_get_item_not_found(client: AsyncClient):
    """Test that non-existent item returns 404."""
    response = await client.get("/api/v1/items/999")
    assert response.status_code == 404
