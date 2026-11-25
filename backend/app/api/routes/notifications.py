"""
TRUSTLENS AI - Secure Notification API Endpoints
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, Query
from pydantic import BaseModel

from backend.app.security.dependencies import get_current_user
from backend.app.services.notification_service import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationPreferencesUpdate(BaseModel):
    in_app_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    threat_alerts_opt_in: Optional[bool] = None


class NotificationDispatchRequest(BaseModel):
    category: str
    title: str
    summary: str
    severity: str = "info"
    reference_id: Optional[str] = None


class DeviceTokenRequest(BaseModel):
    platform: str = "android"
    device_token: str


@router.get("", response_model=Dict[str, Any])
async def list_my_notifications(
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    return await notification_service.list_notifications(
        user_id=current_user["user_id"],
        unread_only=unread_only,
        page=page,
        page_size=page_size,
    )


@router.get("/preferences", response_model=Dict[str, Any])
async def get_my_notification_preferences(current_user: Dict[str, Any] = Depends(get_current_user)):
    return await notification_service.get_preferences(current_user)


@router.patch("/preferences", response_model=Dict[str, Any])
async def update_my_notification_preferences(
    payload: NotificationPreferencesUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    return await notification_service.update_preferences(
        user_id=current_user["user_id"],
        updates=payload.model_dump(exclude_none=True),
    )


@router.post("/dispatch", response_model=Dict[str, Any])
async def dispatch_self_notification(
    payload: NotificationDispatchRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    res = await notification_service.enqueue_notification(
        user_id=current_user["user_id"],
        category=payload.category,
        title=payload.title,
        summary=payload.summary,
        severity=payload.severity,
        reference_id=payload.reference_id,
    )
    if res.get("queued"):
        background_tasks.add_task(notification_service.process_pending_queue)
    return res


@router.patch("/{notification_id}/read", response_model=Dict[str, Any])
async def mark_notification_read(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    return await notification_service.mark_read(
        notification_id=notification_id,
        user_id=current_user["user_id"],
    )


@router.post("/read-all", response_model=Dict[str, Any])
async def mark_all_notifications_read(current_user: Dict[str, Any] = Depends(get_current_user)):
    return await notification_service.mark_all_read(user_id=current_user["user_id"])


@router.get("/deliveries", response_model=Dict[str, Any])
async def get_my_delivery_history(
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    items = await notification_service.get_delivery_history(user_id=current_user["user_id"], limit=limit)
    return {"items": items}


@router.post("/device-token", response_model=Dict[str, Any])
async def register_device_push_token(
    payload: DeviceTokenRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    return await notification_service.register_device_token(
        user_id=current_user["user_id"],
        platform=payload.platform,
        device_token=payload.device_token,
    )


@router.delete("/device-token", response_model=Dict[str, Any])
async def unregister_device_push_token(
    device_token: str = Query(..., min_length=16, max_length=512),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    return await notification_service.unregister_device_token(
        user_id=current_user["user_id"],
        device_token=device_token,
    )
    return {"items": items, "total_count": len(items)}
