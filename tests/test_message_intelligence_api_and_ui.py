"""
TRUSTLENS AI - Message Intelligence ML Inference & UI Tests
Tests real /api/v1/analyze/text responses (English scam, Hindi scam, legitimate alert)
and verifies Message Intelligence UI contracts.
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
async def test_message_intelligence_real_ml_inference(client: AsyncClient):
    created_ids = []
    try:
        # 1. Empty text rejected -> 422
        empty_res = await client.post("/api/v1/analyze/text", json={"text": ""})
        assert empty_res.status_code == 422

        # 2. English phishing/KYC scam
        scam_res = await client.post(
            "/api/v1/analyze/text",
            json={
                "text": "URGENT: Your SBI KYC is suspended. Verify immediately at http://sbi-kyc-alert.xyz or account will be blocked.",
                "channel": "sms",
            },
        )
        assert scam_res.status_code == 200, scam_res.text
        scam_data = scam_res.json()
        created_ids.append(scam_data["analysis_id"])
        assert scam_data["threat_level"] in ("high", "critical", "medium")
        assert 0.0 <= scam_data["risk_score"] <= 1.0
        assert "text_model" in scam_data
        assert scam_data["text_model"].get("detected_language")

        # 3. Hindi Devanagari text
        hi_res = await client.post(
            "/api/v1/analyze/text",
            json={
                "text": "प्रिय ग्राहक, आपका बिजली कनेक्शन आज रात 9:30 बजे काट दिया जाएगा। तुरंत संपर्क करें।",
                "channel": "sms",
            },
        )
        assert hi_res.status_code == 200, hi_res.text
        hi_data = hi_res.json()
        created_ids.append(hi_data["analysis_id"])
        assert "risk_assessment" in hi_data
        assert hi_data["text_model"].get("detected_language")

        # 4. Plain conversational message should score lower than explicit KYC scam
        legit_res = await client.post(
            "/api/v1/analyze/text",
            json={
                "text": "Hey, are we still meeting for lunch at 1pm tomorrow? Let me know.",
                "channel": "sms",
            },
        )
        assert legit_res.status_code == 200, legit_res.text
        legit_data = legit_res.json()
        created_ids.append(legit_data["analysis_id"])
        assert 0.0 <= legit_data["risk_score"] <= 1.0
        assert legit_data["risk_score"] < scam_data["risk_score"]
    finally:
        if created_ids:
            await get_analyses_collection().delete_many({"analysis_id": {"$in": created_ids}})


def test_message_intelligence_ui_uses_cyber_theme_and_honest_engine_label():
    src = Path("frontend/app/analyze/text/page.tsx").read_text(encoding="utf-8")
    assert "cyber-panel" in src
    assert "Bi-LSTM" not in src
    assert "Calibrated LinearSVC" in src
    assert "bg-white" not in src
