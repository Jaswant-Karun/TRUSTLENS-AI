"""
TRUSTLENS AI - Authentication Endpoints
POST /api/v1/auth/register
POST /api/v1/auth/login
GET /api/v1/auth/me
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.schemas.auth import (
    AccountDeleteRequest,
    AccountStatusRequest,
    EmailVerificationRequest,
    OrganizationCreateRequest,
    OrganizationMembershipRequest,
    RoleAssignmentRequest,
    UserRegisterRequest,
    UserLoginRequest,
    UserProfileUpdateRequest,
    TokenResponse,
    UserProfileResponse,
)
from backend.app.services.auth_service import auth_service
from backend.app.services.organization_service import organization_service
from backend.app.security.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest, request: Request):
    """
    Registers a new user account. Passwords are automatically hashed via bcrypt.
    """
    client_ip = request.client.host if request.client else "unknown"
    return await auth_service.register_user(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role=payload.role or "user",
        client_ip=client_ip,
        privacy_accepted=payload.privacy_accepted,
        terms_accepted=payload.terms_accepted,
        onboarding_preferences=(
            payload.onboarding_preferences.model_dump()
            if payload.onboarding_preferences
            else None
        ),
    )


@router.post("/verify-email", response_model=Dict[str, Any])
async def verify_email(payload: EmailVerificationRequest):
    """Validates signed email-verification token and marks email_verified=True."""
    return await auth_service.verify_email_token(payload.token)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    payload: Optional[UserLoginRequest] = None,
    form_data: Optional[OAuth2PasswordRequestForm] = Depends(lambda: None),
):
    """
    Authenticates user and returns JWT access token.
    Supports both JSON body and OAuth2 form data (for Swagger UI).
    """
    client_ip = request.client.host if request.client else "unknown"

    # Support OAuth2PasswordRequestForm or JSON payload
    if form_data and form_data.username and form_data.password:
        email = form_data.username
        password = form_data.password
    elif payload:
        email = payload.email
        password = payload.password
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing login credentials (provide JSON body or form-data).",
        )

    return await auth_service.authenticate_user(
        email=email,
        password=password,
        client_ip=client_ip,
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Retrieves currently authenticated user profile.
    """
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user["role"],
        "is_active": current_user["is_active"],
        "email_verified": current_user.get("email_verified", False),
        "organization_id": current_user.get("organization_id"),
        "organization_role": current_user.get("organization_role"),
        "onboarding_preferences": current_user.get("onboarding_preferences"),
        "created_at": current_user["created_at"],
        "last_login": current_user.get("last_login"),
    }


@router.patch("/me", response_model=UserProfileResponse)
async def update_my_profile(
    payload: UserProfileUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Updates the authenticated user's own profile and preferences."""
    return await auth_service.update_profile(
        user_id=current_user["user_id"],
        updates=payload.model_dump(exclude_none=True),
    )


@router.get("/sessions", response_model=Dict[str, Any])
async def list_my_sessions(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns real session/auth audit events for the authenticated user."""
    return await auth_service.get_user_sessions(user_id=current_user["user_id"])


@router.post("/logout", response_model=Dict[str, Any])
async def logout_current_session(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Revokes current user's active JWT session."""
    client_ip = request.client.host if request.client else "unknown"
    return await auth_service.logout_user(
        user_id=current_user["user_id"],
        client_ip=client_ip,
    )


@router.post("/organizations", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Creates an organization and assigns creator as org_admin."""
    return await organization_service.create_organization(name=payload.name, creator_user=current_user)


@router.post("/users/{target_user_id}/organization", response_model=Dict[str, Any])
async def assign_organization_membership(
    target_user_id: str,
    payload: OrganizationMembershipRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Assigns organization membership (platform admin or org_admin of that organization)."""
    return await organization_service.assign_membership(
        target_user_id=target_user_id,
        organization_id=payload.organization_id,
        organization_role=payload.organization_role,
        actor_user=current_user,
    )


@router.patch("/users/{target_user_id}/role", response_model=Dict[str, Any])
async def assign_platform_role(
    target_user_id: str,
    payload: RoleAssignmentRequest,
    admin_user: Dict[str, Any] = Depends(require_admin),
):
    """Admin-only platform role assignment."""
    return await organization_service.assign_platform_role(
        target_user_id=target_user_id,
        new_role=payload.role,
        actor_id=admin_user["user_id"],
    )


@router.patch("/users/{target_user_id}/status", response_model=Dict[str, Any])
async def update_account_status(
    target_user_id: str,
    payload: AccountStatusRequest,
    admin_user: Dict[str, Any] = Depends(require_admin),
):
    """Admin-only account activation/deactivation lifecycle control."""
    return await organization_service.set_account_status(
        target_user_id=target_user_id,
        is_active=payload.is_active,
        actor_id=admin_user["user_id"],
        reason=payload.reason,
    )


@router.get("/export-data", response_model=Dict[str, Any])
async def export_my_personal_data(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Exports authenticated user's own profile, analyses, and owned investigations."""
    return await organization_service.export_personal_data(user=current_user)


@router.delete("/account", response_model=Dict[str, Any])
async def delete_my_account(
    payload: AccountDeleteRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Self-service account deletion with password confirmation."""
    return await organization_service.delete_own_account(user=current_user, password=payload.password)

