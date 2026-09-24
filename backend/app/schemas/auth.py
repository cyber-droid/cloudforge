"""
Authentication Pydantic v2 Schemas.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole
from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    """Payload for registering a new user account."""

    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plaintext password, minimum 8 chars",
    )
    name: str = Field(..., min_length=2, max_length=100)
    role: Optional[UserRole] = UserRole.STUDENT
    learning_goal: Optional[str] = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    """Payload for authenticating with email & password."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class RefreshTokenRequest(BaseModel):
    """Payload for refreshing an expired access token."""

    refresh_token: str = Field(..., min_length=10)


class LogoutRequest(BaseModel):
    """Optional payload specifying the refresh token to revoke on logout."""

    refresh_token: Optional[str] = None


class TokenResponse(BaseModel):
    """Successful authentication response containing JWT tokens and user metadata."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
