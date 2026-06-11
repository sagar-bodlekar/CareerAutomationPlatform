"""API integration tests for Profile Service."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "profile-service"


@pytest.mark.asyncio
async def test_create_profile(client: AsyncClient, sample_profile_data):
    """Test creating a profile via API."""
    response = await client.post(
        "/api/v1/profiles",
        json=sample_profile_data,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Profile created"
    profile = data["data"]
    assert profile["headline"] == "Senior Software Engineer"
    assert profile["personal_info"]["full_name"] == "John Doe"
    assert len(profile["skills"]) == 3
    assert len(profile["social_links"]) == 2


@pytest.mark.asyncio
async def test_get_profile(client: AsyncClient, sample_profile_data):
    """Test getting a profile by ID."""
    create_resp = await client.post("/api/v1/profiles", json=sample_profile_data)
    profile_id = create_resp.json()["data"]["id"]

    response = await client.get(f"/api/v1/profiles/{profile_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["id"] == profile_id
    assert data["data"]["headline"] == "Senior Software Engineer"


@pytest.mark.asyncio
async def test_get_profile_not_found(client: AsyncClient):
    """Test getting a non-existent profile returns 404."""
    response = await client.get(f"/api/v1/profiles/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


@pytest.mark.asyncio
async def test_get_profile_by_user(client: AsyncClient, sample_profile_data):
    """Test getting a profile by user ID."""
    create_resp = await client.post("/api/v1/profiles", json=sample_profile_data)
    created = create_resp.json()["data"]
    user_id = sample_profile_data["user_id"]

    response = await client.get(f"/api/v1/profiles/user/{user_id}")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == created["id"]


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, sample_profile_data):
    """Test updating a profile."""
    create_resp = await client.post("/api/v1/profiles", json=sample_profile_data)
    profile_id = create_resp.json()["data"]["id"]

    update_payload = {"headline": "Principal Engineer", "summary": "Updated summary"}
    response = await client.put(f"/api/v1/profiles/{profile_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["headline"] == "Principal Engineer"
    assert data["data"]["summary"] == "Updated summary"


@pytest.mark.asyncio
async def test_delete_profile(client: AsyncClient, sample_profile_data):
    """Test deleting a profile."""
    create_resp = await client.post("/api/v1/profiles", json=sample_profile_data)
    profile_id = create_resp.json()["data"]["id"]

    response = await client.delete(f"/api/v1/profiles/{profile_id}")
    assert response.status_code == 200

    # Verify deleted
    get_resp = await client.get(f"/api/v1/profiles/{profile_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_list_profiles(client: AsyncClient, sample_profile_data):
    """Test listing profiles."""
    # Create a profile
    await client.post("/api/v1/profiles", json=sample_profile_data)

    response = await client.get("/api/v1/profiles?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_add_skill(client: AsyncClient, sample_profile_data):
    """Test adding a skill to a profile."""
    create_resp = await client.post("/api/v1/profiles", json=sample_profile_data)
    profile_id = create_resp.json()["data"]["id"]

    skill_data = {"name": "Kubernetes", "category": "DevOps", "proficiency": "intermediate"}
    response = await client.post(
        f"/api/v1/profiles/{profile_id}/skills", json=skill_data
    )
    assert response.status_code == 201
    assert response.json()["data"]["name"] == "Kubernetes"


@pytest.mark.asyncio
async def test_bulk_add_skills(client: AsyncClient, sample_profile_data):
    """Test bulk adding skills."""
    create_resp = await client.post("/api/v1/profiles", json=sample_profile_data)
    profile_id = create_resp.json()["data"]["id"]

    skills_data = {
        "skills": [
            {"name": "Go", "category": "Language", "proficiency": "intermediate"},
            {"name": "Redis", "category": "Database", "proficiency": "advanced"},
        ]
    }
    response = await client.post(
        f"/api/v1/profiles/{profile_id}/skills/bulk", json=skills_data
    )
    assert response.status_code == 201
    assert len(response.json()["data"]) == 2


@pytest.mark.asyncio
async def test_export_profile(client: AsyncClient, sample_profile_data):
    """Test exporting a profile as JSON."""
    create_resp = await client.post("/api/v1/profiles", json=sample_profile_data)
    profile_id = create_resp.json()["data"]["id"]

    response = await client.get(f"/api/v1/profiles/{profile_id}/export")
    assert response.status_code == 200
    export_data = response.json()["data"]
    assert export_data["profile"] is not None
    assert export_data["personal_info"] is not None
    assert len(export_data["skills"]) == 3


@pytest.mark.asyncio
async def test_analytics(client: AsyncClient, sample_profile_data):
    """Test profile analytics endpoint."""
    create_resp = await client.post("/api/v1/profiles", json=sample_profile_data)
    profile_id = create_resp.json()["data"]["id"]

    response = await client.get(f"/api/v1/profiles/{profile_id}/analytics")
    assert response.status_code == 200
    analytics = response.json()["data"]
    assert analytics["total_skills"] == 3
    assert len(analytics["skill_categories"]) > 0
