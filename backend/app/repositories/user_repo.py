"""
User and Refresh Token Repository Layer.

Encapsulates database queries for User accounts and JWT Refresh Token session management.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RefreshToken, User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Data access methods for User entities."""
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Fetch a single user by case-insensitive email address."""
        normalized_email = email.lower().strip()
        result = await db.execute(
            select(User).where(User.email == normalized_email)
        )
        return result.scalars().first()

    async def get_by_id(self, db: AsyncSession, *, id: str) -> Optional[User]:
        """Fetch a single user by primary key ID."""
        result = await db.execute(
            select(User).where(User.id == id)
        )
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Create a new user with normalized email."""
        user_data = obj_in.model_dump()
        user_data["email"] = user_data["email"].lower().strip()
        db_user = User(**user_data)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user


class RefreshTokenRepository:
    """Data access methods for JWT Refresh Tokens."""

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        token_hash: str,
        expires_at: datetime
    ) -> RefreshToken:
        """Create and persist a new refresh token record."""
        db_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked=False,
        )
        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)
        return db_token

    async def get_active_by_hash(
        self,
        db: AsyncSession,
        *,
        token_hash: str
    ) -> Optional[RefreshToken]:
        """Fetch an active, non-revoked refresh token matching the hash."""
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at > now,
            )
        )
        return result.scalars().first()

    async def revoke_by_hash(self, db: AsyncSession, *, token_hash: str) -> bool:
        """Mark a specific refresh token as revoked."""
        result = await db.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(revoked=True)
        )
        await db.commit()
        return result.rowcount > 0

    async def revoke_all_user_tokens(self, db: AsyncSession, *, user_id: str) -> int:
        """Revoke all refresh tokens for a given user (force signout all devices)."""
        result = await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
            .values(revoked=True)
        )
        await db.commit()
        return result.rowcount


user_repo = UserRepository()
refresh_token_repo = RefreshTokenRepository()
