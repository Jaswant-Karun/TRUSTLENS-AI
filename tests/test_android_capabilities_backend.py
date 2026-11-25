from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.security.dependencies import get_current_user


def test_android_device_token_registration_and_removal():
    db_manager._use_fallback = True
    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": "usr-android-1",
        "email": "android@trustlens.ai",
        "role": "user",
        "is_active": True,
    }
    try:
        with TestClient(app) as client:
                # Register valid FCM token
            r = client.post(
                "/api/v1/notifications/device-token",
                json={"platform": "android", "device_token": "fcm_test_token_1234567890abcdef"},
            )
            assert r.status_code == 200
            assert r.json()["registered"] is True
            assert r.json()["platform"] == "android"

            # Reject invalid platform
            bad = client.post(
                "/api/v1/notifications/device-token",
                json={"platform": "symbian", "device_token": "fcm_test_token_1234567890abcdef"},
            )
            assert bad.status_code == 422

            # Unregister token
            d = client.delete(
                "/api/v1/notifications/device-token",
                params={"device_token": "fcm_test_token_1234567890abcdef"},
            )
            assert d.status_code == 200
            assert d.json()["unregistered"] is True
    finally:
        app.dependency_overrides.pop(get_current_user, None)
