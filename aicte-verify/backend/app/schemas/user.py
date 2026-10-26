"""Pydantic schemas for user accounts, credentials, and authentication tokens."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user properties shared across request and response schemas."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: str = Field("college_user", description="admin, officer, or college_user")
    region: Optional[str] = Field(None, max_length=100)
    institution_id: Optional[int] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for registering a new user."""
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user details."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    region: Optional[str] = None
    institution_id: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserRoleUpdate(BaseModel):
    """Schema for administrative role assignment."""
    role: str = Field(..., description="Target role: admin, officer, or college_user")


class UserLogin(BaseModel):
    """Schema for OAuth2 / JSON login requests."""
    username: str
    password: str


class UserResponse(UserBase):
    """Public user response schema excluding password hash."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """JWT bearer token structure returned upon successful authentication."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Decoded JWT payload data."""
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
