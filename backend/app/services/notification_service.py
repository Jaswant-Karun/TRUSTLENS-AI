"""
TRUSTLENS AI - Secure Asynchronous Notification Service
Supports investigation updates, suspicious activity alerts, and consented threat
intelligence notifications with read/unread state, preferences, and delivery history.
Never sends unsolicited alerts or exposes raw sensitive message text.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from fastapi import HTTPException, status

from backend.app.database.collections import get_audit_collection, get_users_collection
from backend.app.database.manager import db_manager


ALLOWED_CATEGORIES = {"investigation_update", "suspicious_activity", "threat_intelligence"}


class NotificationService:
    """Consent-aware, asynchronous notification queue and delivery service."""

    def __init__(self):
        self._queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

    def _notif_coll(self):
        return db_manager.db["notifications"]

    def _delivery_coll(self):
        return db_manager.db["notification_deliveries"]

    def _device_tokens_coll(self):
        return db_manager.db["device_push_tokens"]

    async def register_device_token(
        self,
        user_id: str,
        platform: str,
        device_token: str,
    ) -> Dict[str, Any]:
        clean_platform = platform.strip().lower()
        if clean_platform not in {"android", "ios", "web"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unsupported push platform.",
            )
        token_clean = device_token.strip()
        if len(token_clean) < 16 or len(token_clean) > 512:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid device push token format.",
            )
        now = datetime.now(timezone.utc)
        await self._device_tokens_coll().update_one(
            {"user_id": user_id, "device_token": token_clean},
            {
                "$set": {
                    "user_id": user_id,
                    "platform": clean_platform,
                    "device_token": token_clean,
                    "active": True,
                    "updated_at": now,
                },
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )
        return {"registered": True, "platform": clean_platform}

    async def unregister_device_token(self, user_id: str, device_token: str) -> Dict[str, Any]:
        await self._device_tokens_coll().update_one(
            {"user_id": user_id, "device_token": device_token.strip()},
            {"$set": {"active": False, "updated_at": datetime.now(timezone.utc)}},
        )
        return {"unregistered": True}

    async def get_preferences(self, user: Dict[str, Any]) -> Dict[str, Any]:
        prefs = user.get("onboarding_preferences") or {}
        return {
            "in_app_notifications": prefs.get("in_app_notifications", True),
            "email_notifications": prefs.get("email_notifications", False),
            "threat_alerts_opt_in": prefs.get("threat_alerts_opt_in", False),
        }

    async def update_preferences(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        users_coll = get_users_collection()
        user = await users_coll.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        prefs = dict(user.get("onboarding_preferences") or {})
        for key in ("in_app_notifications", "email_notifications", "threat_alerts_opt_in"):
            if key in updates and updates[key] is not None:
                prefs[key] = bool(updates[key])

        now = datetime.now(timezone.utc)
        await users_coll.update_one(
            {"user_id": user_id},
            {"$set": {"onboarding_preferences": prefs, "updated_at": now}},
        )
        return {
            "in_app_notifications": prefs.get("in_app_notifications", True),
            "email_notifications": prefs.get("email_notifications", False),
            "threat_alerts_opt_in": prefs.get("threat_alerts_opt_in", False),
        }

    async def enqueue_notification(
        self,
        user_id: str,
        category: str,
        title: str,
        summary: str,
        severity: str = "info",
        reference_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if category not in ALLOWED_CATEGORIES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unsupported notification category: {category}",
            )

        user = await get_users_collection().find_one({"user_id": user_id})
        if not user or not user.get("is_active", True):
            return {"queued": False, "status": "skipped_inactive_user"}

        prefs = await self.get_preferences(user)
        # Strict consent check: never send unsolicited threat intelligence or opted-out alerts
        if category == "threat_intelligence" and not prefs["threat_alerts_opt_in"]:
            return {"queued": False, "status": "skipped_opt_out"}
        if not prefs["in_app_notifications"]:
            return {"queued": False, "status": "skipped_opt_out"}

        now = datetime.now(timezone.utc)
        notif_id = f"notif-{uuid.uuid4().hex[:10]}"
        safe_title = title.strip()[:140]
        safe_summary = summary.strip()[:240]

        doc = {
            "notification_id": notif_id,
            "user_id": user_id,
            "category": category,
            "title": safe_title,
            "summary": safe_summary,
            "severity": severity,
            "reference_id": reference_id,
            "read": False,
            "read_at": None,
            "delivery_status": "queued",
            "created_at": now,
        }
        await self._notif_coll().insert_one(doc)
        await self._queue.put({"notification_id": notif_id, "user_id": user_id, "channel": "in_app"})
        doc.pop("_id", None)
        return {"queued": True, "notification_id": notif_id, "status": "queued"}

    async def process_pending_queue(self, max_items: int = 50) -> int:
        """Asynchronously drains queued notifications into delivered state and logs delivery history."""
        processed = 0
        while not self._queue.empty() and processed < max_items:
            item = await self._queue.get()
            now = datetime.now(timezone.utc)
            notif_id = item["notification_id"]
            await self._notif_coll().update_one(
                {"notification_id": notif_id},
                {"$set": {"delivery_status": "delivered", "delivered_at": now}},
            )
            await self._delivery_coll().insert_one({
                "delivery_id": f"dlv-{uuid.uuid4().hex[:10]}",
                "notification_id": notif_id,
                "user_id": item["user_id"],
                "channel": item.get("channel", "in_app"),
                "status": "delivered",
                "delivered_at": now,
            })
            self._queue.task_done()
            processed += 1
        return processed

    async def list_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        # Drain any queued items for immediate consistency when user checks inbox
        await self.process_pending_queue()
        query: Dict[str, Any] = {"user_id": user_id}
        if unread_only:
            query["read"] = False

        coll = self._notif_coll()
        total = await coll.count_documents(query)
        unread_count = await coll.count_documents({"user_id": user_id, "read": False})
        skip = (page - 1) * page_size
        items = await coll.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(page_size).to_list(length=page_size)
        return {
            "items": items,
            "total_count": total,
            "unread_count": unread_count,
            "page": page,
            "page_size": page_size,
        }

    async def mark_read(self, notification_id: str, user_id: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        res = await self._notif_coll().update_one(
            {"notification_id": notification_id, "user_id": user_id},
            {"$set": {"read": True, "read_at": now}},
        )
        if res.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
        return {"notification_id": notification_id, "read": True, "read_at": now.isoformat()}

    async def mark_all_read(self, user_id: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        res = await self._notif_coll().update_many(
            {"user_id": user_id, "read": False},
            {"$set": {"read": True, "read_at": now}},
        )
        return {"marked_count": res.modified_count}

    async def get_delivery_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        await self.process_pending_queue()
        return await self._delivery_coll().find(
            {"user_id": user_id},
            {"_id": 0},
        ).sort("delivered_at", -1).limit(limit).to_list(length=limit)


notification_service = NotificationService()
