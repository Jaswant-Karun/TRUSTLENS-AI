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
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfileResponse,
)
from backend.app.services.auth_service import auth_service
from backend.app.security.dependencies import get_current_user

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
    )


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
        "created_at": current_user["created_at"],
        "last_login": current_user.get("last_login"),
    }

