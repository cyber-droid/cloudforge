"""
API Dependencies Module.

Provides reusable FastAPI dependencies for database sessions, JWT authentication,
current-user extraction, and role-based authorization (RBAC).

Why this exists:
Centralizes authentication extraction and security policies. Routes simply declare
`current_user: User = Depends(get_current_user)` or
`admin_user: User = Depends(require_roles(UserRole.ADMIN))` to enforce authorization.
"""

from typing import Callable, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole
from app.repositories.user_repo import user_repo

# HTTP Bearer security scheme for OpenAPI UI
http_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token_auth: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
) -> User:
    """
    Extract and validate JWT Bearer token from the Authorization header.
    Loads and returns the active User model instance from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token_auth or not token_auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = token_auth.credentials
    payload = decode_token(token)
    if not payload:
        raise credentials_exception

    token_type = payload.get("type")
    if token_type != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    user = await user_repo.get_by_id(db, id=user_id)
    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    return user


async def get_optional_current_user(
    db: AsyncSession = Depends(get_db),
    token_auth: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
) -> Optional[User]:
    """
    Optionally extract and validate JWT Bearer token.
    Returns User if valid token is provided, or None if no Authorization header is present.
    """
    if not token_auth or not token_auth.credentials:
        return None
    try:
        return await get_current_user(db=db, token_auth=token_auth)
    except HTTPException:
        return None


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure current authenticated user is active."""
    return current_user


def require_roles(*allowed_roles: UserRole) -> Callable:
    """
    Role-Based Access Control (RBAC) Dependency Factory.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_roles(UserRole.ADMIN))])
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {[r.value for r in allowed_roles]}",
            )
        return current_user

    return role_checker
