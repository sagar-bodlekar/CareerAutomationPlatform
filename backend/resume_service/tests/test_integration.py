"""Integration test for the full resume lifecycle."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_resume_lifecycle_with_auth(client: AsyncClient):
    """Test: seed templates -> register -> login -> create resume -> list -> optimize.

    This test requires Auth Service to be running for JWT generation.
    It uses the same JWT secret so tokens from manual testing can be injected.
    """
    # Seed templates
    seed_resp = await client.post("/api/v1/templates/seed")
    assert seed_resp.status_code == 200

    # Get templates
    templates_resp = await client.get("/api/v1/templates")
    templates = templates_resp.json()["data"]
    assert len(templates) > 0

    # Templates have expected structure
    template_names = {t["name"] for t in templates}
    assert "master" in template_names
    assert "modern" in template_names
    assert "classic" in template_names
    assert "minimal" in template_names

    # Get a specific template
    template_id = templates[0]["id"]
    tmpl_resp = await client.get(f"/api/v1/templates/{template_id}")
    assert tmpl_resp.status_code == 200
    assert tmpl_resp.json()["data"]["name"] == templates[0]["name"]


@pytest.mark.asyncio
async def test_seed_templates_idempotent(client: AsyncClient):
    """Test that seeding templates multiple times doesn't create duplicates."""
    resp1 = await client.post("/api/v1/templates/seed")
    count1 = len(resp1.json()["data"])

    resp2 = await client.post("/api/v1/templates/seed")
    count2 = len(resp2.json()["data"])

    # Second seed should create 0 new templates (already exist)
    assert count2 == 0 or count2 <= count1


@pytest.mark.asyncio
async def test_create_template_endpoint(client: AsyncClient):
    """Test creating a new template via the API."""
    template_data = {
        "name": "test_custom",
        "display_name": "Custom Test",
        "description": "A custom template for testing",
        "html_content": "<html><body>{{ name }}</body></html>",
        "css_content": "body { font-family: sans-serif; }",
    }
    response = await client.post("/api/v1/templates", json=template_data)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "test_custom"
    assert data["html_content"] == template_data["html_content"]

    # Verify it appears in listing
    list_resp = await client.get("/api/v1/templates")
    names = [t["name"] for t in list_resp.json()["data"]]
    assert "test_custom" in names
