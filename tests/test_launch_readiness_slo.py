from pathlib import Path
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.manager import db_manager


def test_launch_slo_endpoint_and_launch_report():
    db_manager._use_fallback = True
    with TestClient(app) as client:
        r = client.get("/api/v1/health/slo")
        assert r.status_code == 200
        d = r.json()
        assert d["service_availability"]["availability_slo"] == "99.9%"
        assert d["launch_scope_guardrails"]["evaluated_languages"] == ["English", "Hindi", "Hinglish"]
        assert "Tamil" in d["launch_scope_guardrails"]["unsupported_languages"]
        assert d["launch_scope_guardrails"]["auto_expand_scope"] is False
        assert d["launch_scope_guardrails"]["claim_universal_fraud_detection"] is False
        assert d["incident_and_support_contacts"]["security_email"] == "security@trustlens.ai"

    report = Path("docs/CONTROLLED_LAUNCH_REPORT.md")
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "Do not automatically expand supported regions, languages, or fraud detection claims without validation." in text
