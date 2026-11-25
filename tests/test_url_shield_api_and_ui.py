"""
TRUSTLENS AI - URL Shield ML Inference & Safety Tests
Tests real /api/v1/analyze/url predictions, empty-input rejection,
and UI safety (never auto-navigating or rendering untrusted URLs as clickable links).
"""

from pathlib import Path
import pytest
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
async def test_url_shield_real_ml_inference(client: AsyncClient):
    created_ids = []
    try:
        # 1. Empty URL rejected -> 422
        empty_res = await client.post("/api/v1/analyze/url", json={"url": ""})
        assert empty_res.status_code == 422

        # 2. Direct IP phishing URL (never visited/fetched)
        phish_res = await client.post(
            "/api/v1/analyze/url",
            json={"url": "http://192.168.1.50/sbi-kyc/update.php"},
        )
        assert phish_res.status_code == 200, phish_res.text
        phish_data = phish_res.json()
        created_ids.append(phish_data["analysis_id"])
        assert 0.0 <= phish_data["risk_score"] <= 1.0
        assert "url_model" in phish_data
        assert "risk_assessment" in phish_data
        assert phish_data["url_model"].get("features") is not None
    finally:
        if created_ids:
            await get_analyses_collection().delete_many({"analysis_id": {"$in": created_ids}})


def test_url_shield_ui_safety_and_limitations_disclosed():
    src = Path("frontend/app/analyze/url/page.tsx").read_text(encoding="utf-8")
    assert "cyber-panel" in src
    assert "bg-white" not in src
    assert "ROC-AUC 1.000" not in src
    assert "Model Limitations" in src
    assert "window.open" not in src
    assert "<a " not in src
