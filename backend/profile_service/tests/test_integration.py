"""Integration tests for the full profile lifecycle."""

import uuid
from datetime import date

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_profile_lifecycle(client: AsyncClient):
    """Test the complete profile lifecycle: create → read → update → add sub-entities → export → delete."""
    # 1. Create
    user_id = uuid.uuid4()
    create_data = {
        "user_id": str(user_id),
        "profile": {
            "headline": "Full Stack Developer",
            "summary": "Building great products.",
            "location_city": "Austin",
            "location_country": "USA",
            "location_type": "hybrid",
            "preferred_roles": ["Full Stack Developer", "Backend Engineer"],
            "target_salary_min": 120000,
            "target_salary_max": 160000,
            "open_to_work": True,
            "years_of_experience": 6.0,
            "personal_info": {
                "full_name": "Alice Johnson",
                "email": "alice@example.com",
                "phone": "+1-555-0200",
                "city": "Austin",
                "country": "USA",
            },
            "skills": [
                {"name": "TypeScript", "category": "Language", "proficiency": "advanced", "years_used": 4},
                {"name": "Node.js", "category": "Runtime", "proficiency": "advanced", "years_used": 5},
                {"name": "GraphQL", "category": "API", "proficiency": "intermediate", "years_used": 2},
            ],
        },
    }

    create_resp = await client.post("/api/v1/profiles", json=create_data)
    assert create_resp.status_code == 201
    profile_id = create_resp.json()["data"]["id"]
    assert create_resp.json()["data"]["headline"] == "Full Stack Developer"

    # 2. Read
    get_resp = await client.get(f"/api/v1/profiles/{profile_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["personal_info"]["full_name"] == "Alice Johnson"

    # 3. Read by user
    user_resp = await client.get(f"/api/v1/profiles/user/{user_id}")
    assert user_resp.status_code == 200
    assert user_resp.json()["data"]["id"] == profile_id

    # 4. Update
    update_resp = await client.put(
        f"/api/v1/profiles/{profile_id}",
        json={"headline": "Lead Full Stack Developer", "summary": "Leading product development."},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["headline"] == "Lead Full Stack Developer"

    # 5. Bulk add more skills
    skills_resp = await client.post(
        f"/api/v1/profiles/{profile_id}/skills/bulk",
        json={
            "skills": [
                {"name": "Docker", "category": "DevOps", "proficiency": "advanced"},
                {"name": "Kubernetes", "category": "DevOps", "proficiency": "intermediate"},
            ]
        },
    )
    assert skills_resp.status_code == 201
    assert len(skills_resp.json()["data"]) == 2

    # 6. Add work experience
    exp_resp = await client.post(
        f"/api/v1/profiles/{profile_id}/experiences",
        json={
            "company_name": "Tech Co",
            "job_title": "Senior Developer",
            "start_date": "2021-03-01",
            "is_current": True,
            "employment_type": "full_time",
            "description": "Building scalable microservices.",
            "achievements": ["Led team of 5", "Reduced latency by 40%"],
            "skills_used": ["TypeScript", "Node.js", "Docker"],
        },
    )
    assert exp_resp.status_code == 201

    # 7. Export
    export_resp = await client.get(f"/api/v1/profiles/{profile_id}/export")
    assert export_resp.status_code == 200
    export_data = export_resp.json()["data"]
    assert export_data["profile"]["headline"] == "Lead Full Stack Developer"
    assert len(export_data["skills"]) >= 3

    # 8. Analytics
    analytics_resp = await client.get(f"/api/v1/profiles/{profile_id}/analytics")
    assert analytics_resp.status_code == 200
    analytics = analytics_resp.json()["data"]
    assert analytics["total_skills"] >= 3
    assert analytics["total_experiences"] >= 1

    # 9. Delete
    delete_resp = await client.delete(f"/api/v1/profiles/{profile_id}")
    assert delete_resp.status_code == 200

    # 10. Verify delete
    get_deleted = await client.get(f"/api/v1/profiles/{profile_id}")
    assert get_deleted.status_code == 404
