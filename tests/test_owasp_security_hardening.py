"""
Automated OWASP security hardening verification tests:
- get_optional_current_user rejects deactivated and logged-out (session_revoked_before) tokens
- AppSettings.validate_production_security() blocks default secrets in production
- SecurityHeadersMiddleware emits CSP & Permissions-Policy headers
- ScreenshotOCRService rejects MIME-spoofed non-allowed image formats (e.g., GIF as image/png)
"""

import io
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from PIL import Image

from backend.app.config.settings import AppSettings
from backend.app.database.manager import db_manager
from backend.app.database.collections import get_users_collection
from backend.app.main import app
from backend.app.security.dependencies import get_optional_current_user
from backend.app.security.jwt import create_access_token
from backend.app.services.ocr_service import ocr_service


def test_production_secrets_validation_blocks_defaults():
    s = AppSettings(APP_ENV="production")
    with pytest.raises(RuntimeError, match="Production SECRET_KEY"):
        s.validate_production_security()

    s2 = AppSettings(APP_ENV="production", SECRET_KEY="a" * 48)
    with pytest.raises(RuntimeError, match="ADMIN_DEFAULT_PASSWORD"):
        s2.validate_production_security()

    s3 = AppSettings(APP_ENV="production", SECRET_KEY="a" * 48, ADMIN_DEFAULT_PASSWORD="Strong!Unique#Password2026")
    s3.validate_production_security()


def test_optional_current_user_enforces_active_and_revocation():
    import asyncio
    db_manager._use_fallback = True

    async def _run():
        users = get_users_collection()
        await users.insert_one({
            "user_id": "u-sec-1",
            "email": "sec1@trustlens.ai",
            "is_active": False,
        })
        tok1 = create_access_token({"sub": "u-sec-1"})
        assert await get_optional_current_user(tok1) is None

        await users.insert_one({
            "user_id": "u-sec-2",
            "email": "sec2@trustlens.ai",
            "is_active": True,
            "session_revoked_before": datetime.now(timezone.utc) + timedelta(seconds=10),
        })
        tok2 = create_access_token({"sub": "u-sec-2"})
        assert await get_optional_current_user(tok2) is None

    asyncio.run(_run())


def test_security_headers_and_upload_format_spoofing():
    db_manager._use_fallback = True
    client = TestClient(app)
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert r.headers.get("Permissions-Policy") == "geolocation=(), microphone=(), camera=()"
    assert "default-src 'none'" in (r.headers.get("Content-Security-Policy") or "")

    # Upload a GIF pretending to be image/png -> rejected with 415
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buf, format="GIF")
    fake_upload = MagicMock()
    fake_upload.content_type = "image/png"
    fake_upload.read = AsyncMock(return_value=buf.getvalue())

    import asyncio
    with pytest.raises(HTTPException) as exc:
        asyncio.run(ocr_service.validate_and_read_image(fake_upload))
    assert exc.value.status_code == 415
