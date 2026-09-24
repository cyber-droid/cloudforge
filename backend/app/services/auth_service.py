"""
Authentication Service Module.

Houses business logic for registration, authentication, token issuance,
session refreshing, and logout token revocation.

Why this exists:
Decouples cryptographic and token orchestration from API route handlers,
enabling easy unit testing and reuse across multiple transport layers (REST, WebSocket, CLI).
"""

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from app.models.user import User, UserRole
from app.repositories.user_repo import refresh_token_repo, user_repo
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse


class AuthService:
    """Authentication and session management business service."""

    async def register(
        self, db: AsyncSession, *, data: RegisterRequest
    ) -> TokenResponse:
        """
        Register a new user account and issue an initial authenticated session.
        Prevents duplicate email registrations.
        """
        existing_user = await user_repo.get_by_email(db, email=data.email)
        if existing_user:
            logger.warning(f"Registration attempt with duplicate email: {data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email address already exists.",
            )

        # Hash password securely with bcrypt
        hashed_password = get_password_hash(data.password)

        user_create_data = UserCreate(
            email=data.email,
            name=data.name,
            role=data.role or UserRole.STUDENT,
            learning_goal=data.learning_goal,
            hashed_password=hashed_password,
        )

        user = await user_repo.create_user(db, obj_in=user_create_data)
        logger.info(
            f"User registered successfully: id={user.id}, role={user.role.value}"
        )

        return await self._generate_session_tokens(db, user=user)

    async def authenticate(
        self, db: AsyncSession, *, data: LoginRequest
    ) -> TokenResponse:
        """
        Authenticate credentials and generate JWT access and refresh token pair.
        """
        user = await user_repo.get_by_email(db, email=data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: {data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            logger.warning(f"Inactive user login attempt: {user.id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account has been deactivated.",
            )

        logger.info(f"User authenticated successfully: id={user.id}")
        return await self._generate_session_tokens(db, user=user)

    async def refresh_access_token(
        self, db: AsyncSession, *, refresh_token_str: str
    ) -> TokenResponse:
        """
        Validate a refresh token against the database and issue a fresh access token.
        """
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        token_digest = hash_token(refresh_token_str)

        # Check token validity and revocation state in database
        db_token = await refresh_token_repo.get_active_by_hash(
            db, token_hash=token_digest
        )
        if not db_token:
            logger.warning(
                f"Attempt to use invalid/revoked refresh token for user {user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is invalid or has been revoked.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await user_repo.get_by_id(db, id=user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or deactivated.",
            )

        # Generate fresh access token
        access_token = create_access_token(
            subject=user.id,
            role=user.role.value,
            email=user.email,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    async def logout(
        self,
        db: AsyncSession,
        *,
        refresh_token_str: Optional[str] = None,
        user: Optional[User] = None,
    ) -> bool:
        """
        Invalidate session refresh token(s).
        """
        if refresh_token_str:
            token_digest = hash_token(refresh_token_str)
            await refresh_token_repo.revoke_by_hash(db, token_hash=token_digest)
        elif user:
            await refresh_token_repo.revoke_all_user_tokens(db, user_id=user.id)
        return True

    async def _generate_session_tokens(
        self, db: AsyncSession, *, user: User
    ) -> TokenResponse:
        """Helper to create access/refresh token pair and persist hashed refresh token."""
        access_token = create_access_token(
            subject=user.id,
            role=user.role.value,
            email=user.email,
        )
        raw_refresh_token, expires_at = create_refresh_token(subject=user.id)

        # Store hashed digest in DB
        await refresh_token_repo.create(
            db,
            user_id=user.id,
            token_hash=hash_token(raw_refresh_token),
            expires_at=expires_at,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )


auth_service = AuthService()
