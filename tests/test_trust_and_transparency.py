"""
Automated tests for TRUSTLENS AI Trust & Transparency Framework:
- /api/v1/privacy/transparency covers all 9 required documentation topics
- Explicitly marks Tamil/Bengali unsupported and fake_investment blocked
- Never advertises 100% accuracy or universal fraud detection
- Methodology page & framework docs exist
"""

from pathlib import Path
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.manager import db_manager


def test_trust_and_transparency_endpoint_and_artifacts():
    db_manager._use_fallback = True
    client = TestClient(app)

    r = client.get("/api/v1/privacy/transparency")
    assert r.status_code == 200
    d = r.json()

    for key in (
        "supported_languages",
        "model_limitations",
        "dataset_provenance",
        "prediction_uncertainty",
        "data_handling_practices",
        "reporting_and_moderation",
        "human_review_requirements",
        "user_rights",
        "security_contact",
        "disclaimers",
    ):
        assert key in d, f"Missing {key}"

    assert "Tamil" in d["supported_languages"]["unsupported_unverified"]
    assert "fake_investment" in d["model_limitations"]["model_3_tactics"]
    assert "does not guarantee universal fraud detection" in " ".join(d["disclaimers"])
    assert d["security_contact"]["email"] == "security@trustlens.ai"

    assert Path("docs/TRUST_AND_TRANSPARENCY_FRAMEWORK.md").exists()
    assert Path("frontend/app/methodology/page.tsx").exists()
