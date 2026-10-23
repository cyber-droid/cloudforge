"""
Integration and Unit Tests for Authentication API & Services.

Verifies:
- Registration with hashing & token generation
- Duplicate email prevention
- Password validation
- Login with correct and incorrect credentials
- Refresh token rotation & revocation
- Logout token invalidation
- Guarantee that password hash is never returned in JSON payloads
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    """Test successful user registration returns tokens and user profile."""
    payload = {
        "email": "devops_student@cloudforge.io",
        "password": "SecureDevOpsPassword123!",
        "name": "DevOps Learner",
        "role": "student",
        "learning_goal": "DevOps Engineer",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == "devops_student@cloudforge.io"
    assert data["user"]["name"] == "DevOps Learner"
    assert data["user"]["role"] == "student"
    assert data["user"]["learning_goal"] == "DevOps Engineer"
    assert "hashed_password" not in data["user"]
    assert "password" not in data["user"]


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client: AsyncClient):
    """Test that attempting to register an existing email returns 400 Bad Request."""
    payload = {
        "email": "duplicate@cloudforge.io",
        "password": "Password123456!",
        "name": "First User",
    }
    # First registration
    resp1 = await client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201

    # Second registration with same email
    resp2 = await client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 400
    assert "already exists" in resp2.json()["message"]


@pytest.mark.asyncio
async def test_register_short_password_fails_validation(client: AsyncClient):
    """Test that passwords shorter than 8 characters fail Pydantic validation (422)."""
    payload = {
        "email": "shortpw@cloudforge.io",
        "password": "short",
        "name": "Short PW User",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert response.json()["error"] == "ValidationError"


@pytest.mark.asyncio
async def test_login_success_and_failure(client: AsyncClient):
    """Test login credentials verification and error cases."""
    # Register user
    email = "login_test@cloudforge.io"
    password = "CorrectPassword123!"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "name": "Login Tester",
        },
    )

    # Test valid login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data
    assert login_data["user"]["email"] == email

    # Test wrong password
    wrong_pw_resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "WrongPassword999!",
        },
    )
    assert wrong_pw_resp.status_code == 401

    # Test nonexistent email
    nonexistent_resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nobody@cloudforge.io",
            "password": "Password123!",
        },
    )
    assert nonexistent_resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_and_logout_flow(client: AsyncClient):
    """
    Test the complete session lifecycle:
    Register -> Login -> Access Token Refresh -> Logout -> Verify Refresh Rejected.
    """
    email = "session_lifecycle@cloudforge.io"
    password = "SessionPassword123!"

    # 1. Register
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "name": "Lifecycle Tester",
        },
    )
    assert reg_resp.status_code == 201
    refresh_token = reg_resp.json()["refresh_token"]

    # 2. Refresh Token
    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )
    assert refresh_resp.status_code == 200
    new_data = refresh_resp.json()
    assert "access_token" in new_data
    assert new_data["user"]["email"] == email

    # 3. Logout
    logout_resp = await client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )
    assert logout_resp.status_code == 200
    assert logout_resp.json()["message"] == "Successfully logged out."

    # 4. Attempt to use revoked refresh token
    revoked_resp = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )
    assert revoked_resp.status_code == 401


@pytest.mark.asyncio
async def test_register_with_email_and_password_only(client: AsyncClient):
    """Test bare-bones registration providing only email and password."""
    payload = {
        "email": "barebones@cloudforge.io",
        "password": "BareBonesPassword123!",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == "barebones@cloudforge.io"
    assert data["user"]["id"] is not None
    assert data["user"]["role"] == "student"


@pytest.mark.asyncio
async def test_access_me_with_and_without_token(client: AsyncClient):
    """Test accessing /me endpoint with and without valid token."""
    # 1. Without token -> 401
    unauth_resp1 = await client.get("/api/v1/auth/me")
    assert unauth_resp1.status_code == 401

    unauth_resp2 = await client.get("/me")
    assert unauth_resp2.status_code == 401

    # 2. Register and obtain token
    email = "test_me_endpoint@cloudforge.io"
    password = "MySecurePassword123!"
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    user_id = reg_resp.json()["user"]["id"]

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Access /api/v1/auth/me with valid Bearer token -> 200
    me_resp1 = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp1.status_code == 200
    me_data1 = me_resp1.json()
    assert me_data1["id"] == user_id
    assert me_data1["email"] == email
    assert me_data1["role"] == "student"

    # 4. Access root /me with valid Bearer token -> 200
    me_resp2 = await client.get("/me", headers=headers)
    assert me_resp2.status_code == 200
    me_data2 = me_resp2.json()
    assert me_data2["id"] == user_id
    assert me_data2["email"] == email
    assert me_data2["role"] == "student"
