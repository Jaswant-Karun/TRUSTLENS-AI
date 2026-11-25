"""
TRUSTLENS AI - Authentication Request & Response Schemas
"""

from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class OnboardingPreferences(BaseModel):
    preferred_language: str = Field("en", description="en | hi | hinglish")
    primary_focus: str = Field("message_scanning", description="message_scanning | url_shield | investigations")
    threat_alerts_opt_in: bool = False


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="Valid corporate or user email address")
    password: str = Field(..., min_length=8, description="Password (at least 8 chars)")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    role: Optional[str] = Field("user", description="user | analyst (admin restricted)")
    privacy_accepted: bool = Field(True, description="User accepted privacy policy")
    terms_accepted: bool = Field(True, description="User accepted terms of service")
    onboarding_preferences: Optional[OnboardingPreferences] = None

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v.strip()) < 8:
            raise ValueError("Password must be at least 8 non-whitespace characters.")
        if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one letter and one digit.")
        return v

    @field_validator("privacy_accepted")
    @classmethod
    def must_accept_privacy(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Privacy consent is required to create an account.")
        return v

    @field_validator("terms_accepted")
    @classmethod
    def must_accept_terms(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Terms acceptance is required to create an account.")
        return v


class EmailVerificationRequest(BaseModel):
    token: str = Field(..., min_length=8)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserSummary(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    email_verified: Optional[bool] = False
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: UserSummary


class UserProfileUpdateRequest(BaseModel):
    model_config = {"extra": "forbid"}

    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    preferred_language: Optional[str] = Field(None, pattern="^(en|hi|hinglish)$")
    primary_focus: Optional[str] = Field(None, pattern="^(message_scanning|url_shield|investigations)$")
    threat_alerts_opt_in: Optional[bool] = None
    email_notifications: Optional[bool] = None
    in_app_notifications: Optional[bool] = None


class OrganizationCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class OrganizationMembershipRequest(BaseModel):
    organization_id: str = Field(..., min_length=3, max_length=64)
    organization_role: str = Field("member", pattern="^(member|analyst|org_admin)$")


class RoleAssignmentRequest(BaseModel):
    role: str = Field(..., pattern="^(user|reviewer|analyst|admin)$")


class AccountStatusRequest(BaseModel):
    is_active: bool
    reason: Optional[str] = Field(None, max_length=250)


class AccountDeleteRequest(BaseModel):
    password: str = Field(..., min_length=1)


class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    email_verified: Optional[bool] = False
    organization_id: Optional[str] = None
    organization_role: Optional[str] = None
    onboarding_preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    last_login: Optional[datetime] = None
