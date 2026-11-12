"""
TRUSTLENS AI - Authentication Request & Response Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="Valid corporate or user email address")
    password: str = Field(..., min_length=8, description="Password (at least 8 chars)")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    role: Optional[str] = Field("user", description="user | analyst (admin restricted)")


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserSummary(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: UserSummary


class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
