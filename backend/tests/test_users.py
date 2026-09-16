"""
Integration Tests for User Profile and Preferences API.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_current_user_profile(client: AsyncClient):
    """Test retrieving current authenticated user profile."""
    # 1. Register a user
    email = "profile_user@cloudforge.io"
    password = "ProfilePassword123!"
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "name": "Alex DevOps",
        "role": "student",
        "learning_goal": "Cloud Architect",
    })
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]

    # 2. Access /users/me without token -> should fail with 401
    unauth_resp = await client.get("/api/v1/users/me")
    assert unauth_resp.status_code == 401

    # 3. Access /users/me with valid Bearer token -> should succeed with 200
    auth_resp = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert auth_resp.status_code == 200
    user_data = auth_resp.json()
    assert user_data["email"] == email
    assert user_data["name"] == "Alex DevOps"
    assert user_data["learning_goal"] == "Cloud Architect"
    assert user_data["role"] == "student"
    assert "hashed_password" not in user_data


@pytest.mark.asyncio
async def test_update_current_user_preferences(client: AsyncClient):
    """Test updating user preferences (terminal theme, font size, notifications, name)."""
    # 1. Register a user
    email = "settings_user@cloudforge.io"
    password = "SettingsPassword123!"
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "name": "Default Name",
    })
    token = reg_resp.json()["access_token"]

    # 2. Patch user settings
    patch_payload = {
        "name": "Updated Engineer Name",
        "terminal_theme": "dracula",
        "terminal_font_size": 16,
        "email_notifications": False,
        "learning_goal": "Site Reliability Engineer",
    }
    patch_resp = await client.patch(
        "/api/v1/users/me",
        json=patch_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert patch_resp.status_code == 200
    updated_data = patch_resp.json()

    assert updated_data["name"] == "Updated Engineer Name"
    assert updated_data["terminal_theme"] == "dracula"
    assert updated_data["terminal_font_size"] == 16
    assert updated_data["email_notifications"] is False
    assert updated_data["learning_goal"] == "Site Reliability Engineer"

    # 3. Confirm GET /users/me reflects the patched changes
    get_resp = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["terminal_theme"] == "dracula"


@pytest.mark.asyncio
async def test_role_assignment_and_rbac(client: AsyncClient):
    """Test creating users with different roles (student, instructor, admin) and verifying role assignment."""
    roles = ["student", "instructor", "admin"]
    for role_name in roles:
        email = f"user_{role_name}@cloudforge.io"
        reg_resp = await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "RolePassword123!",
            "name": f"{role_name.capitalize()} User",
            "role": role_name,
        })
        assert reg_resp.status_code == 201
        data = reg_resp.json()
        assert data["user"]["role"] == role_name
        token = data["access_token"]

        # Fetch profile
        me_resp = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["role"] == role_name
