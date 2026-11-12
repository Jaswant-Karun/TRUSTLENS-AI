"""
TRUSTLENS AI - Authentication & User Management Service
Handles user registration, credential verification, and initial administrator bootstrap.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from pydantic import EmailStr

from backend.app.config.settings import settings
from backend.app.database.collections import get_users_collection, get_audit_collection
from backend.app.security.password import hash_password, verify_password
from backend.app.security.jwt import create_access_token


class AuthenticationService:
    """Core user security & authentication operations."""

    async def register_user(
        self, email: str, password: str, full_name: str, role: str = "user", client_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """Registers a new user account with hashed password."""
        users_coll = get_users_collection()
        audit_coll = get_audit_collection()

        norm_email = email.lower().strip()
        existing = await users_coll.find_one({"email": norm_email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email address is already registered.",
            )

        # Enforce role restrictions: public registration cannot create admins
        if role not in ["user", "analyst"]:
            role = "user"

        user_id = str(uuid.uuid4())
        hashed_pwd = hash_password(password)
        now = datetime.now(timezone.utc)

        user_doc = {
            "user_id": user_id,
            "email": norm_email,
            "hashed_password": hashed_pwd,
            "full_name": full_name.strip(),
            "role": role,
            "is_active": True,
            "created_at": now,
            "last_login": None,
        }

        await users_coll.insert_one(user_doc)

        # Audit log
        await audit_coll.insert_one({
            "audit_id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": "user_registration",
            "resource_type": "user",
            "resource_id": user_id,
            "client_ip": client_ip,
            "timestamp": now,
            "details": {"email": norm_email, "role": role},
        })

        return {
            "user_id": user_id,
            "email": norm_email,
            "full_name": user_doc["full_name"],
            "role": role,
            "is_active": True,
            "created_at": now,
        }

    async def authenticate_user(
        self, email: str, password: str, client_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verifies credentials and returns JWT bearer token."""
        users_coll = get_users_collection()
        audit_coll = get_audit_collection()

        norm_email = email.lower().strip()
        user = await users_coll.find_one({"email": norm_email})

        if not user or not verify_password(password, user.get("hashed_password", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive or suspended. Contact security administrator.",
            )

        now = datetime.now(timezone.utc)
        await users_coll.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"last_login": now}}
        )

        # Issue JWT
        token_data = {
            "sub": user["user_id"],
            "email": user["email"],
            "role": user.get("role", "user"),
            "full_name": user.get("full_name", ""),
        }
        token = create_access_token(token_data)

        # Audit log
        await audit_coll.insert_one({
            "audit_id": str(uuid.uuid4()),
            "user_id": user["user_id"],
            "action": "user_login",
            "resource_type": "auth",
            "resource_id": user["user_id"],
            "client_ip": client_ip,
            "timestamp": now,
            "details": {"email": norm_email},
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in_seconds": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "user_id": user["user_id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "is_active": user["is_active"],
                "created_at": user["created_at"],
            },
        }

    async def seed_initial_admin(self) -> None:
        """Seeds default administrator account if database has no admin users."""
        users_coll = get_users_collection()
        admin_email = settings.ADMIN_DEFAULT_EMAIL.lower()
        existing = await users_coll.find_one({"email": admin_email})
        if not existing:
            user_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            await users_coll.insert_one({
                "user_id": user_id,
                "email": admin_email,
                "hashed_password": hash_password(settings.ADMIN_DEFAULT_PASSWORD),
                "full_name": "TRUSTLENS Security Admin",
                "role": "admin",
                "is_active": True,
                "created_at": now,
                "last_login": None,
            })


auth_service = AuthenticationService()
