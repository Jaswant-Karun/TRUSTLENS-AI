"""
TRUSTLENS AI - Extensible Organization, Role & Account Lifecycle Service
Supports lightweight organization membership, admin role assignment,
account activation/deactivation, personal data export, and account deletion
without unnecessary multi-tenant database complexity.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid
from fastapi import HTTPException, status

from backend.app.database.collections import (
    get_analyses_collection,
    get_audit_collection,
    get_investigations_collection,
    get_users_collection,
)
from backend.app.database.manager import db_manager
from backend.app.security.password import verify_password


class OrganizationAndLifecycleService:
    """Manages organization membership, RBAC role governance, and account lifecycle."""

    def _orgs_coll(self):
        return db_manager.db["organizations"]

    async def create_organization(self, name: str, creator_user: Dict[str, Any]) -> Dict[str, Any]:
        clean_name = name.strip()
        if len(clean_name) < 2:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Organization name too short.")

        org_id = f"org-{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": org_id,
            "name": clean_name,
            "owner_id": creator_user["user_id"],
            "created_at": now,
            "is_active": True,
        }
        await self._orgs_coll().insert_one(doc)
        await get_users_collection().update_one(
            {"user_id": creator_user["user_id"]},
            {"$set": {"organization_id": org_id, "organization_role": "org_admin", "updated_at": now}},
        )
        await get_audit_collection().insert_one({
            "audit_id": str(uuid.uuid4()),
            "user_id": creator_user["user_id"],
            "action": "organization_created",
            "resource_type": "organization",
            "resource_id": org_id,
            "timestamp": now,
            "details": {"name": clean_name},
        })
        doc.pop("_id", None)
        return doc

    async def assign_membership(
        self,
        target_user_id: str,
        organization_id: str,
        organization_role: str,
        actor_user: Dict[str, Any],
    ) -> Dict[str, Any]:
        is_platform_admin = actor_user.get("role") == "admin"
        is_same_org_admin = (
            actor_user.get("organization_id") == organization_id
            and actor_user.get("organization_role") == "org_admin"
        )
        if not (is_platform_admin or is_same_org_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform administrators or this organization's org_admin can assign membership.",
            )

        org = await self._orgs_coll().find_one({"organization_id": organization_id})
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")

        users_coll = get_users_collection()
        target = await users_coll.find_one({"user_id": target_user_id})
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found.")

        now = datetime.now(timezone.utc)
        await users_coll.update_one(
            {"user_id": target_user_id},
            {"$set": {"organization_id": organization_id, "organization_role": organization_role, "updated_at": now}},
        )
        await get_audit_collection().insert_one({
            "audit_id": str(uuid.uuid4()),
            "user_id": actor_user["user_id"],
            "action": "organization_membership_updated",
            "resource_type": "user",
            "resource_id": target_user_id,
            "timestamp": now,
            "details": {"organization_id": organization_id, "organization_role": organization_role},
        })
        return {
            "user_id": target_user_id,
            "organization_id": organization_id,
            "organization_role": organization_role,
        }

    async def assign_platform_role(
        self,
        target_user_id: str,
        new_role: str,
        actor_id: str,
    ) -> Dict[str, Any]:
        users_coll = get_users_collection()
        target = await users_coll.find_one({"user_id": target_user_id})
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found.")

        now = datetime.now(timezone.utc)
        await users_coll.update_one(
            {"user_id": target_user_id},
            {"$set": {"role": new_role, "updated_at": now}},
        )
        await get_audit_collection().insert_one({
            "audit_id": str(uuid.uuid4()),
            "user_id": actor_id,
            "action": "user_role_assigned",
            "resource_type": "user",
            "resource_id": target_user_id,
            "timestamp": now,
            "details": {"role": new_role},
        })
        return {"user_id": target_user_id, "role": new_role}

    async def set_account_status(
        self,
        target_user_id: str,
        is_active: bool,
        actor_id: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        if target_user_id == actor_id and not is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrators cannot deactivate their own active account.",
            )
        users_coll = get_users_collection()
        target = await users_coll.find_one({"user_id": target_user_id})
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found.")

        now = datetime.now(timezone.utc)
        update_doc: Dict[str, Any] = {"is_active": is_active, "updated_at": now}
        if not is_active:
            update_doc["session_revoked_before"] = now
        await users_coll.update_one({"user_id": target_user_id}, {"$set": update_doc})

        await get_audit_collection().insert_one({
            "audit_id": str(uuid.uuid4()),
            "user_id": actor_id,
            "action": "account_lifecycle_updated",
            "resource_type": "user",
            "resource_id": target_user_id,
            "timestamp": now,
            "details": {"is_active": is_active, "reason": reason},
        })
        return {"user_id": target_user_id, "is_active": is_active}

    async def export_personal_data(self, user: Dict[str, Any]) -> Dict[str, Any]:
        user_id = user["user_id"]
        analyses = await get_analyses_collection().find(
            {"user_id": user_id},
            {"_id": 0},
        ).sort("created_at", -1).limit(500).to_list(length=500)

        investigations = await get_investigations_collection().find(
            {"owner_id": user_id},
            {"_id": 0},
        ).sort("created_at", -1).limit(200).to_list(length=200)

        safe_profile = {
            "user_id": user["user_id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "organization_id": user.get("organization_id"),
            "organization_role": user.get("organization_role"),
            "onboarding_preferences": user.get("onboarding_preferences"),
            "created_at": user["created_at"],
        }
        return {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "profile": safe_profile,
            "analyses_count": len(analyses),
            "analyses": analyses,
            "investigations_count": len(investigations),
            "investigations": investigations,
        }

    async def delete_own_account(self, user: Dict[str, Any], password: str) -> Dict[str, Any]:
        if not verify_password(password, user.get("hashed_password", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password confirmation failed.",
            )
        user_id = user["user_id"]
        now = datetime.now(timezone.utc)

        await get_analyses_collection().delete_many({"user_id": user_id})
        await get_investigations_collection().delete_many({"owner_id": user_id, "visibility": "Private"})
        await get_users_collection().update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "is_active": False,
                    "deleted_at": now,
                    "session_revoked_before": now,
                    "email": f"deleted-{user_id}@redacted.local",
                    "full_name": "Deleted User",
                    "hashed_password": "",
                    "onboarding_preferences": {},
                }
            },
        )
        await get_audit_collection().insert_one({
            "audit_id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": "account_deleted",
            "resource_type": "user",
            "resource_id": user_id,
            "timestamp": now,
        })
        return {"deleted": True, "user_id": user_id}


organization_service = OrganizationAndLifecycleService()
