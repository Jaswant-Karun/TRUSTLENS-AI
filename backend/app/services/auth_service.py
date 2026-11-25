"""
TRUSTLENS AI - Authentication & User Management Service
Handles user registration, credential verification, and initial administrator bootstrap.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from pydantic import EmailStr

from backend.app.config.settings import settings
from backend.app.database.collections import get_users_collection, get_audit_collection
from backend.app.security.password import hash_password, verify_password
from backend.app.security.jwt import create_access_token, decode_access_token


class AuthenticationService:
    """Core user security & authentication operations."""

    async def register_user(
        self,
        email: str,
        password: str,
        full_name: str,
        role: str = "user",
        client_ip: Optional[str] = None,
        privacy_accepted: bool = True,
        terms_accepted: bool = True,
        onboarding_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Registers a new user account with hashed password, consent, and verification token."""
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
        prefs = onboarding_preferences or {
            "preferred_language": "en",
            "primary_focus": "message_scanning",
            "threat_alerts_opt_in": False,
        }

        user_doc = {
            "user_id": user_id,
            "email": norm_email,
            "hashed_password": hashed_pwd,
            "full_name": full_name.strip(),
            "role": role,
            "is_active": True,
            "email_verified": False,
            "privacy_accepted": bool(privacy_accepted),
            "terms_accepted": bool(terms_accepted),
            "consent_recorded_at": now,
            "onboarding_preferences": prefs,
            "created_at": now,
            "last_login": None,
        }

        await users_coll.insert_one(user_doc)

        verification_token = create_access_token(
            data={"sub": user_id, "purpose": "email_verification"},
            expires_delta=timedelta(hours=24),
        )

        # Audit log
        await audit_coll.insert_one({
            "audit_id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": "user_registration",
            "resource_type": "user",
            "resource_id": user_id,
            "client_ip": client_ip,
            "timestamp": now,
            "details": {
                "email": norm_email,
                "role": role,
                "privacy_accepted": bool(privacy_accepted),
                "terms_accepted": bool(terms_accepted),
            },
        })

        return {
            "user_id": user_id,
            "email": norm_email,
            "full_name": user_doc["full_name"],
            "role": role,
            "is_active": True,
            "email_verified": False,
            "onboarding_preferences": prefs,
            "verification_token": verification_token if settings.APP_ENV != "production" else None,
            "created_at": now,
        }

    async def verify_email_token(self, token: str) -> Dict[str, Any]:
        """Validates signed email-verification token and marks user email_verified=True."""
        payload = decode_access_token(token)
        if not payload or payload.get("purpose") != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired email verification token.",
            )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email verification token subject.",
            )
        users_coll = get_users_collection()
        audit_coll = get_audit_collection()
        now = datetime.now(timezone.utc)
        res = await users_coll.update_one(
            {"user_id": user_id},
            {"$set": {"email_verified": True, "email_verified_at": now}},
        )
        if res.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        await audit_coll.insert_one({
            "audit_id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": "email_verified",
            "resource_type": "user",
            "resource_id": user_id,
            "timestamp": now,
        })
        return {"verified": True, "user_id": user_id}

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

