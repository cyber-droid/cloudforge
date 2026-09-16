"""
User Management Service Module.

Handles user profile updates, preference synchronization, and role checks.
"""
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.user import User
from app.repositories.user_repo import user_repo
from app.schemas.user import UserResponse, UserUpdate


class UserService:
    """User profile management service."""

    async def get_by_id(self, db: AsyncSession, *, user_id: str) -> User:
        """Fetch user by id or raise 404."""
        user = await user_repo.get_by_id(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user

    async def update_profile(
        self,
        db: AsyncSession,
        *,
        current_user: User,
        data: UserUpdate
    ) -> UserResponse:
        """Update current user profile and terminal/notification preferences."""
        update_dict = data.model_dump(exclude_unset=True)
        if not update_dict:
            return UserResponse.model_validate(current_user)

        updated_user = await user_repo.update(db, db_obj=current_user, obj_in=update_dict)
        logger.info(f"User profile updated: id={current_user.id}, fields={list(update_dict.keys())}")
        return UserResponse.model_validate(updated_user)


user_service = UserService()
