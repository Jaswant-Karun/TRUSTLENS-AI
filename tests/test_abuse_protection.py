"""
Automated tests for Application Abuse Protection:
- Brute-force login lockout (5 failed attempts -> 6th returns 429 + Retry-After + operational alert)
- Uniform 401 error response on unknown vs wrong password (anti-enumeration)
- Suspicious query/path probe detection & operational alert
- Oversized Content-Length resource-exhaustion guard (413)
- Analyst/admin-gated /api/v1/security/abuse-monitoring endpoint
"""

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.manager import db_manager
from backend.app.security.dependencies import require_analyst_or_admin
from backend.app.services.abuse_service import abuse_service


def test_brute_force_lockout_suspicious_probes_and_alerts():
    db_manager._use_fallback = True
    abuse_service._login_failures.clear()
    abuse_service._lockouts.clear()
    abuse_service._suspicious_counts.clear()
    client = TestClient(app)

    # 1. Uniform 401 on 5 failed login attempts -> 6th triggers 429 lockout
    for _ in range(5):
        r = client.post("/api/v1/auth/login", json={"email": "victim@trustlens.ai", "password": "wrong"})
        assert r.status_code == 401
        assert r.json()["detail"] == "Incorrect email or password."

    locked = client.post("/api/v1/auth/login", json={"email": "victim@trustlens.ai", "password": "wrong"})
    assert locked.status_code == 429
    assert "Retry-After" in locked.headers

    # 2. Suspicious NoSQL operator query probe -> 400 + alert
    probe = client.get("/api/v1/threat-library?search=$where")
    assert probe.status_code == 400

    # 3. Oversized Content-Length -> 413
    big = client.post("/api/v1/analyze/text", headers={"Content-Length": str(20 * 1024 * 1024)}, json={"text": "hi"})
    assert big.status_code == 413

    # 4. Abuse monitoring requires analyst/admin (401 unauthenticated)
    assert client.get("/api/v1/security/abuse-monitoring").status_code == 401

    app.dependency_overrides[require_analyst_or_admin] = lambda: {"user_id": "soc-1", "role": "analyst"}
    try:
        mon = client.get("/api/v1/security/abuse-monitoring")
        assert mon.status_code == 200
        mdata = mon.json()
        assert mdata["active_login_lockouts"] >= 1
        assert mdata["operational_alerts_count"] >= 2
        alert_types = {a["alert_type"] for a in mdata["operational_alerts"]}
        assert "brute_force_login_lockout" in alert_types
        assert "suspicious_request_probe" in alert_types
    finally:
        app.dependency_overrides.pop(require_analyst_or_admin, None)
