"""
User Pydantic v2 Schemas for request validation and response serialization.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user attributes."""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = UserRole.STUDENT
    learning_goal: Optional[str] = None
    avatar_url: Optional[str] = None
    terminal_theme: str = "cloudforge-dark"
    terminal_font_size: int = Field(default=14, ge=10, le=24)
    email_notifications: bool = True


class UserCreate(UserBase):
    """Schema used internally for user creation with hashed password."""
    hashed_password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile and terminal/notification preferences."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    avatar_url: Optional[str] = None
    learning_goal: Optional[str] = None
    terminal_theme: Optional[str] = None
    terminal_font_size: Optional[int] = Field(default=None, ge=10, le=24)
    email_notifications: Optional[bool] = None


class UserResponse(BaseModel):
    """Public user response schema. NEVER exposes hashed_password."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    name: str
    role: UserRole
    avatar_url: Optional[str] = None
    learning_goal: Optional[str] = None
    is_active: bool
    is_verified: bool
    terminal_theme: str
    terminal_font_size: int
    email_notifications: bool
    created_at: datetime
    updated_at: datetime
