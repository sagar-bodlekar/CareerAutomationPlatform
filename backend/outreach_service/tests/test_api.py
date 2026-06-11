"""API tests for Outreach Service."""

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
async def test_generate_cover_letter(client: AsyncClient):
    """Test cover letter generation via real service with mock DB."""
    response = await client.post(
        "/api/v1/outreach/cover-letter",
        json={
            "profile_id": 1,
            "job_id": 100,
            "job_title": "Software Engineer",
            "company_name": "Tech Corp",
            "candidate_name": "John Doe",
            "current_role": "Senior Developer",
            "skills": ["Python", "React"],
            "achievements": ["Led a team"],
            "use_ai": False,
        },
    )
    # Assert HTTP status and that response body has a data section
    assert response.status_code == 201
    data = response.json()
    # Response structure: APIResponse wraps data; handle generic serialization
    assert isinstance(data, dict)
    body = data.get("data", data)
    assert body.get("content_type") == "cover_letter"
    assert body.get("id") is not None


@pytest.mark.asyncio
async def test_generate_email(client: AsyncClient):
    """Test email generation via real service with mock DB."""
    response = await client.post(
        "/api/v1/outreach/email",
        json={
            "profile_id": 1,
            "job_id": 100,
            "job_title": "Software Engineer",
            "company_name": "Tech Corp",
            "candidate_name": "John Doe",
            "current_role": "Senior Developer",
            "recipient_name": "Jane Smith",
            "recipient_role": "Hiring Manager",
            "use_ai": False,
        },
    )
    assert response.status_code == 201
    data = response.json()
    body = data.get("data", data)
    assert body.get("content_type") == "email"
    assert body.get("id") is not None


@pytest.mark.asyncio
async def test_cover_letter_not_found(client: AsyncClient):
    """Test that non-existent cover letter returns 404."""
    response = await client.get("/api/v1/outreach/cover-letter/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_email_not_found(client: AsyncClient):
    """Test that non-existent email returns 404."""
    response = await client.get("/api/v1/outreach/email/999")
    assert response.status_code == 404
