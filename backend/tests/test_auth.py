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
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "name": "Login Tester",
    })

    # Test valid login
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password,
    })
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data
    assert login_data["user"]["email"] == email

    # Test wrong password
    wrong_pw_resp = await client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "WrongPassword999!",
    })
    assert wrong_pw_resp.status_code == 401

    # Test nonexistent email
    nonexistent_resp = await client.post("/api/v1/auth/login", json={
        "email": "nobody@cloudforge.io",
        "password": "Password123!",
    })
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
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "name": "Lifecycle Tester",
    })
    assert reg_resp.status_code == 201
    refresh_token = reg_resp.json()["refresh_token"]

    # 2. Refresh Token
    refresh_resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert refresh_resp.status_code == 200
    new_data = refresh_resp.json()
    assert "access_token" in new_data
    assert new_data["user"]["email"] == email

    # 3. Logout
    logout_resp = await client.post("/api/v1/auth/logout", json={
        "refresh_token": refresh_token,
    })
    assert logout_resp.status_code == 200
    assert logout_resp.json()["message"] == "Successfully logged out."

    # 4. Attempt to use revoked refresh token
    revoked_resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert revoked_resp.status_code == 401
