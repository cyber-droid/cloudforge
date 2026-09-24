"""
Authentication API Endpoints.

Handles registration, credential login, token refreshing, and session logout.
"""

from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_optional_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Register a new CloudForge account with email, password, name, and optional learning goal.",
)
async def register(
    data: RegisterRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Create a new user account and return JWT access/refresh token pair."""
    return await auth_service.register(db, data=data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user with email and password, returning JWT access/refresh tokens.",
)
async def login(
    data: LoginRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Validate credentials and issue new authenticated tokens."""
    return await auth_service.authenticate(db, data=data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="Issue a new JWT access token using a valid, non-revoked refresh token.",
)
async def refresh_token(
    data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Validate refresh token and issue fresh access token."""
    return await auth_service.refresh_access_token(
        db, refresh_token_str=data.refresh_token
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Revoke the provided refresh token or all user session tokens.",
)
async def logout(
    data: Optional[LogoutRequest] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Invalidate session tokens."""
    refresh_token_str = data.refresh_token if data else None
    await auth_service.logout(
        db, refresh_token_str=refresh_token_str, user=current_user
    )
    return MessageResponse(message="Successfully logged out.")
