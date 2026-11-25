"""
TRUSTLENS AI - Screenshot Intelligence OCR & File Security Tests
Tests empty upload rejection, disguised executable/invalid signature rejection,
valid PNG OCR triage, and UI magic-byte + honest-scope contracts.
"""

import io
from pathlib import Path
import pytest
from PIL import Image, ImageDraw
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.database.collections import get_analyses_collection


@pytest.fixture(autouse=True)
async def setup_db():
    await db_manager.connect()
    yield
    await db_manager.disconnect()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_screenshot_upload_validation_and_ocr(client: AsyncClient):
    created_ids = []
    try:
        # 1. Empty 0-byte upload rejected -> 400
        empty_res = await client.post(
            "/api/v1/analyze/image",
            files={"file": ("empty.png", b"", "image/png")},
        )
        assert empty_res.status_code == 400

        # 2. Disguised executable/invalid signature rejected -> 400 or 415
        bad_sig = await client.post(
            "/api/v1/analyze/image",
            files={"file": ("malware.png", b"MZ\x90\x00not_a_real_png_header", "image/png")},
        )
        assert bad_sig.status_code in (400, 415)

        # 3. Valid in-memory PNG with readable text
        img = Image.new("RGB", (600, 120), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((20, 40), "URGENT SBI KYC SUSPENDED VERIFY NOW", fill=(0, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        ok_res = await client.post(
            "/api/v1/analyze/image",
            files={"file": ("kyc_scam.png", buf.getvalue(), "image/png")},
        )
        assert ok_res.status_code == 200, ok_res.text
        data = ok_res.json()
        assert "analysis_status" in data
        assert "ocr_confidence" in data
        if data.get("analysis_result") and data["analysis_result"].get("analysis_id"):
            created_ids.append(data["analysis_result"]["analysis_id"])
    finally:
        if created_ids:
            await get_analyses_collection().delete_many({"analysis_id": {"$in": created_ids}})


def test_screenshot_ui_magic_bytes_and_cyber_theme():
    src = Path("frontend/app/analyze/image/page.tsx").read_text(encoding="utf-8")
    assert "hasValidImageSignature" in src
    assert "cyber-panel" in src
    assert "bg-white" not in src
    assert "No Pixel/Deepfake Vision" in src
