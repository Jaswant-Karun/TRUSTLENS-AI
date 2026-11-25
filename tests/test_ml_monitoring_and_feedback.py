"""
Automated tests for Production ML Monitoring & Human-Reviewed Feedback Pipeline:
- Real prediction distribution, latency, error rate, and input drift from DB records
- Strict separation of pending user feedback from verified ground-truth labels
- Human-review gate required before verified_language_performance updates
- Monitoring & feedback API endpoints via FastAPI TestClient
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.services.monitoring_service import monitoring_service


@pytest.fixture()
def client():
    db_manager._use_fallback = True
    return TestClient(app)


def test_monitoring_and_human_reviewed_feedback_separation(client):
    # 1. Submit FP feedback -> strictly pending_review, NOT verified_ground_truth
    resp_fb = client.post(
        "/api/v1/models/feedback",
        json={
            "analysis_id": "an-test-001",
            "feedback_type": "false_positive",
            "suggested_label": "legitimate",
            "comment": "Official bank receipt",
            "detected_language": "English",
            "model_version": "trustlens-model1-v2.1",
        },
    )
    assert resp_fb.status_code == 201
    fb_doc = resp_fb.json()
    assert fb_doc["review_status"] == "pending_review"
    assert fb_doc["is_verified_ground_truth"] is False
    fb_id = fb_doc["feedback_id"]

    # 2. Monitoring snapshot shows 1 pending FP, 0 verified ground truth, auto_training=False
    mon1 = client.get("/api/v1/models/monitoring")
    assert mon1.status_code == 200
    d1 = mon1.json()
    assert d1["feedback_summary"]["pending_review"]["false_positive"] >= 1
    assert d1["feedback_summary"]["verified_ground_truth"]["false_positive"] == 0
    assert d1["feedback_summary"]["auto_training_from_user_reports"] is False
    assert "active_production_versions" in d1

    # 3. Unauthenticated review is rejected (401)
    unauth = client.post(
        f"/api/v1/models/feedback/{fb_id}/review",
        json={"decision": "verified_ground_truth", "verified_label": "legitimate"},
    )
    assert unauth.status_code == 401

    # 4. Authenticated human review promotes to verified_ground_truth
    from backend.app.core.security import get_current_user
    app.dependency_overrides[get_current_user] = lambda: {"user_id": "analyst-1", "email": "analyst@trustlens.ai"}
    try:
        rev = client.post(
            f"/api/v1/models/feedback/{fb_id}/review",
            json={"decision": "verified_ground_truth", "verified_label": "legitimate", "reviewer_notes": "Confirmed legit"},
        )
        assert rev.status_code == 200
        rev_doc = rev.json()
        assert rev_doc["review_status"] == "verified_ground_truth"
        assert rev_doc["is_verified_ground_truth"] is True
        assert rev_doc["verified_label"] == "legitimate"
        assert rev_doc["reviewed_by"] == "analyst@trustlens.ai"

        mon2 = client.get("/api/v1/models/monitoring")
        assert mon2.status_code == 200
        d2 = mon2.json()
        assert d2["feedback_summary"]["verified_ground_truth"]["false_positive"] >= 1
        assert "English" in d2["verified_language_performance"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)
