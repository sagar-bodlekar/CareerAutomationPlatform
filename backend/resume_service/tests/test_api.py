"""API integration tests for Resume Service."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "resume-service"


@pytest.mark.asyncio
async def test_health_v1(client: AsyncClient):
    """Test health check via v1 route."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_templates_empty(client: AsyncClient):
    """Test listing templates (no auth required)."""
    response = await client.get("/api/v1/templates")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_get_template_not_found(client: AsyncClient):
    """Test getting non-existent template returns 404."""
    import uuid

    response = await client.get(f"/api/v1/templates/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_resume_unauthorized(client: AsyncClient, sample_resume_data):
    """Test creating a resume without auth returns 401."""
    response = await client.post("/api/v1/resumes", json=sample_resume_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_resume_unauthorized(client: AsyncClient):
    """Test getting a resume without auth returns 401."""
    import uuid

    response = await client.get(f"/api/v1/resumes/{uuid.uuid4()}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_resumes_unauthorized(client: AsyncClient):
    """Test listing resumes without auth returns 401."""
    response = await client.get("/api/v1/resumes")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_generate_resume_requires_auth(client: AsyncClient):
    """Test generate endpoint without auth returns 401."""
    import uuid

    response = await client.post(
        f"/api/v1/resumes/{uuid.uuid4()}/generate",
        json={"resume_id": str(uuid.uuid4()), "target_role": "Developer"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_optimize_resume_requires_auth(client: AsyncClient):
    """Test optimize endpoint without auth returns 401."""
    import uuid

    response = await client.post(
        f"/api/v1/resumes/{uuid.uuid4()}/optimize",
        json={"job_description": "Looking for a Python developer with 5+ years experience in web development with React and PostgreSQL. The ideal candidate will have strong communication skills and experience with agile methodologies."},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_seed_templates(client: AsyncClient):
    """Test seeding default templates."""
    response = await client.post("/api/v1/templates/seed")
    assert response.status_code == 200

    # Verify templates were created
    list_resp = await client.get("/api/v1/templates")
    assert list_resp.status_code == 200
    templates = list_resp.json()["data"]
    assert len(templates) > 0

    # Each template should have HTML content
    for t in templates:
        assert t["html_content"]
        assert t["name"] in ("master", "modern", "classic", "minimal")
