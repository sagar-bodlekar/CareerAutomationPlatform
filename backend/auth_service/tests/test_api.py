"""API integration tests for Auth Service."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "auth-service"


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """Test user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "apitest@example.com",
            "password": "SecurePass123!",
            "display_name": "API Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "apitest@example.com"
    assert data["data"]["is_verified"] is False


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    """Test duplicate registration returns 409."""
    payload = {
        "email": "dupeapi@example.com",
        "password": "SecurePass123!",
        "display_name": "Dupe User",
    }
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """Test login returns JWT tokens."""
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginapi@example.com",
            "password": "SecurePass123!",
            "display_name": "Login API",
        },
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "loginapi@example.com", "password": "SecurePass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with wrong password returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    """Test refreshing an access token."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "refreshapi@example.com",
            "password": "SecurePass123!",
            "display_name": "Refresh API",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "refreshapi@example.com", "password": "SecurePass123!"},
    )
    refresh_token = login_resp.json()["data"]["refresh_token"]

    # Refresh
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test logout blacklists the refresh token."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "logoutapi@example.com",
            "password": "SecurePass123!",
            "display_name": "Logout API",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "logoutapi@example.com", "password": "SecurePass123!"},
    )
    access_token = login_resp.json()["data"]["access_token"]
    refresh_token = login_resp.json()["data"]["refresh_token"]

    # Logout
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
        headers=headers,
    )
    assert response.status_code == 200

    # Old refresh should no longer work
    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    """Test getting current user info."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "meapi@example.com",
            "password": "SecurePass123!",
            "display_name": "Me API",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "meapi@example.com", "password": "SecurePass123!"},
    )
    access_token = login_resp.json()["data"]["access_token"]

    # Get me
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == "meapi@example.com"
    assert data["data"]["display_name"] == "Me API"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """Test accessing /me without token returns 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient):
    """Test changing password."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "changepassapi@example.com",
            "password": "OldPass123!",
            "display_name": "Change Pass API",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "changepassapi@example.com", "password": "OldPass123!"},
    )
    access_token = login_resp.json()["data"]["access_token"]

    # Change password
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "OldPass123!", "new_password": "NewPass456!"},
        headers=headers,
    )
    assert response.status_code == 200

    # Login with new password
    login_resp2 = await client.post(
        "/api/v1/auth/login",
        json={"email": "changepassapi@example.com", "password": "NewPass456!"},
    )
    assert login_resp2.status_code == 200


@pytest.mark.asyncio
async def test_forgot_password(client: AsyncClient):
    """Test forgot password (dev mode returns token)."""
    # Register
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "forgotapi@example.com",
            "password": "SecurePass123!",
            "display_name": "Forgot API",
        },
    )

    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "forgotapi@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "reset_token" in data["data"]  # Dev mode returns token


@pytest.mark.asyncio
async def test_reset_password(client: AsyncClient):
    """Test password reset flow."""
    # Register
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "resetapi@example.com",
            "password": "OldPass123!",
            "display_name": "Reset API",
        },
    )

    # Forgot password
    forgot_resp = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "resetapi@example.com"},
    )
    reset_token = forgot_resp.json()["data"]["reset_token"]

    # Reset password
    response = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": "NewPass789!"},
    )
    assert response.status_code == 200

    # Login with new password
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "resetapi@example.com", "password": "NewPass789!"},
    )
    assert login_resp.status_code == 200


@pytest.mark.asyncio
async def test_oauth_initiate(client: AsyncClient):
    """Test OAuth initiation endpoint."""
    response = await client.get("/api/v1/auth/oauth/google")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["provider"] == "google"


@pytest.mark.asyncio
async def test_oauth_invalid_provider(client: AsyncClient):
    """Test OAuth with invalid provider returns 400."""
    response = await client.get("/api/v1/auth/oauth/invalid_provider")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_api_key(client: AsyncClient):
    """Test creating an API key."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "apikeyapi@example.com",
            "password": "SecurePass123!",
            "display_name": "API Key User",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "apikeyapi@example.com", "password": "SecurePass123!"},
    )
    access_token = login_resp.json()["data"]["access_token"]

    # Create API key
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.post(
        "/api/v1/api-keys",
        json={"name": "Test Key"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["name"] == "Test Key"
    assert "key" in data["data"]  # Full key returned once
    assert len(data["data"]["key"]) > 8


@pytest.mark.asyncio
async def test_list_api_keys(client: AsyncClient):
    """Test listing API keys."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "listkeysapi@example.com",
            "password": "SecurePass123!",
            "display_name": "List Keys",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "listkeysapi@example.com", "password": "SecurePass123!"},
    )
    access_token = login_resp.json()["data"]["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    # Create a key first
    await client.post(
        "/api/v1/api-keys", json={"name": "My Key"}, headers=headers
    )

    # List keys
    response = await client.get("/api/v1/api-keys", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1


@pytest.mark.asyncio
async def test_revoke_api_key(client: AsyncClient):
    """Test revoking an API key."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "revokekeyapi@example.com",
            "password": "SecurePass123!",
            "display_name": "Revoke Key",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "revokekeyapi@example.com", "password": "SecurePass123!"},
    )
    access_token = login_resp.json()["data"]["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    # Create a key
    create_resp = await client.post(
        "/api/v1/api-keys", json={"name": "Test Revoke"}, headers=headers
    )
    key_id = create_resp.json()["data"]["id"]

    # Revoke it
    response = await client.delete(
        f"/api/v1/api-keys/{key_id}", headers=headers
    )
    assert response.status_code == 200
