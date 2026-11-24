"""
TRUSTLENS AI - Comprehensive Frontend Integration & Quality Assurance Test Suite
Validates API contracts, response parsing, ML inference pipelines, input validation,
error states, authentication lifecycles, and chart data formatting.
"""

import pytest
import httpx
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000/api/v1"


@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as c:
        yield c


@pytest.fixture(scope="session")
def auth_token(client):
    res = client.post("/auth/login", json={"email": "admin@trustlens.ai", "password": "Admin@TrustLens2026!"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json().get("access_token")
    assert token is not None
    return token


class TestFrontendAPIContracts:
    """Verifies that all backend responses strictly adhere to frontend TypeScript types in frontend/lib/api.ts."""

    def test_health_contract(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data
        assert "models_loaded" in data
        assert isinstance(data["models_loaded"], dict)
        assert data["models_loaded"].get("model_1_text_scam") is True
        assert data["models_loaded"].get("model_2_phishing_url") is True

    def test_text_analysis_parsing(self, client):
        payload = {"text": "URGENT: SBI account 3821 blocked due to KYC. Update pan at http://sbi-kyc.top", "channel": "sms"}
        res = client.post("/analyze/text", json=payload)
        assert res.status_code == 200
        data = res.json()
        
        # Verify ScanResult interface fields
        assert "analysis_id" in data
        assert "threat_level" in data
        assert data["threat_level"] in ["clean", "low", "medium", "high", "critical", "inconclusive"]
        assert "risk_score" in data
        assert isinstance(data["risk_score"], (int, float))
        assert "risk_assessment" in data
        assert "verdict" in data["risk_assessment"]
        assert "remedial_actions" in data["risk_assessment"]
        assert isinstance(data["risk_assessment"]["remedial_actions"], list)
        
        # Verify text_model contract
        assert data.get("text_model") is not None
        assert "predicted_label" in data["text_model"]
        assert "confidence" in data["text_model"]

    def test_url_analysis_and_shap_contract(self, client):
        payload = {"url": "http://secure-sbi-portal-verify.online/login.php"}
        res = client.post("/analyze/url", json=payload)
        assert res.status_code == 200
        data = res.json()
        
        assert "url_model" in data
        url_model = data["url_model"]
        assert "is_phishing" in url_model
        assert "risk_score" in url_model
        assert "features" in url_model
        assert "model_version" in url_model
        
        # Verify SHAP explainability contract (Zero Attention Weight fabrication)
        assert "explainability" in data
        exp = data["explainability"]
        assert "url_evidence" in exp
        assert "top_risk_factors" in exp["url_evidence"]
        assert "all_feature_shap" in exp["url_evidence"]
        assert "methodology" in exp["url_evidence"]
        assert "TreeExplainer" in exp["url_evidence"]["methodology"]

    def test_comprehensive_investigation_contract(self, client):
        payload = {
            "content": "Electricity board warning: power cut tonight at 9 PM. Call 9876543210 or pay at http://bses-bill.xyz",
            "channel": "sms",
            "sender": "+919876543210"
        }
        res = client.post("/analyze/comprehensive", json=payload)
        assert res.status_code == 200
        data = res.json()
        
        assert "risk_score" in data
        assert "risk_assessment" in data
        assert "extracted_iocs" in data
        assert isinstance(data["extracted_iocs"], dict)
        assert "urls" in data["extracted_iocs"] or "phones" in data["extracted_iocs"]

    def test_model_metrics_chart_contract(self, client):
        res = client.get("/models/metrics")
        assert res.status_code == 200
        data = res.json()
        
        assert "overall_summary" in data
        summary = data["overall_summary"]
        assert "active_models_count" in summary
        assert "production_readiness" in summary
        assert "average_inference_latency_ms" in summary
        
        assert "models" in data
        models = data["models"]
        assert "text_scam_detector" in models
        assert "phishing_url_detector" in models
        assert "tactic_detector" in models
        assert "campaign_clusterer" in models

    def test_campaign_dossier_contract(self, client):
        res = client.get("/campaigns?limit=5")
        assert res.status_code == 200
        clusters = res.json()
        assert isinstance(clusters, list)
        assert len(clusters) > 0
        
        cid = clusters[0].get("cluster_id") or clusters[0].get("campaign_id") or 11
        dossier_res = client.get(f"/campaigns/{cid}")
        assert dossier_res.status_code == 200
        dossier = dossier_res.json()
        assert "exemplar_message" in dossier
        assert "cohesion_score" in dossier
        assert "shared_iocs" in dossier or "shared_threat_indicators" in dossier or "shared_urls" in dossier
        assert "legal_disclaimer" in dossier

    def test_community_reports_workflow(self, client):
        # 1. Submit report
        report_data = {
            "target_type": "url",
            "content": "Reported fake loan verification link: http://instant-cash-loan-approval.top",
            "target_identifier": "http://instant-cash-loan-approval.top",
            "description": "Scam WhatsApp loan offer"
        }
        create_res = client.post("/reports", json=report_data)
        assert create_res.status_code in [200, 201]
        created = create_res.json()
        report_id = created.get("report_id")
        assert report_id is not None
        
        # 2. Query reports list
        list_res = client.get("/reports?page=1&page_size=10")
        assert list_res.status_code == 200
        listing = list_res.json()
        assert "items" in listing
        assert any(item["report_id"] == report_id for item in listing["items"])


class TestAuthenticationAndSecurity:
    """Tests authentication protection, JWT lifecycle, and RBAC enforcement."""

    def test_unauthenticated_analyses_rejection(self, client):
        res = client.get("/analyses")
        assert res.status_code == 401
        assert "detail" in res.json()

    def test_authenticated_analyses_access(self, client, auth_token):
        res = client.get("/analyses?page=1&page_size=5", headers={"Authorization": f"Bearer {auth_token}"})
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total_count" in data
        assert isinstance(data["items"], list)

    def test_invalid_token_rejection(self, client):
        res = client.get("/analyses", headers={"Authorization": "Bearer invalid.token.payload"})
        assert res.status_code == 401

    def test_current_user_profile(self, client, auth_token):
        res = client.get("/auth/me", headers={"Authorization": f"Bearer {auth_token}"})
        assert res.status_code == 200
        user = res.json()
        assert user.get("email") == "admin@trustlens.ai"
        assert user.get("role") == "admin"


class TestInputValidationAndErrorResilience:
    """Verifies that malicious or corrupted inputs are rejected without crashing or predicting false negatives."""

    def test_empty_text_analysis_validation(self, client):
        res = client.post("/analyze/text", json={"text": ""})
        assert res.status_code in [400, 422]

    def test_oversized_payload_handling(self, client):
        large_text = "Phishing test " * 5000  # 70,000 chars
        res = client.post("/analyze/text", json={"text": large_text, "channel": "sms"})
        assert res.status_code in [200, 400, 413, 422]
        if res.status_code == 200:
            assert "threat_level" in res.json()

    def test_invalid_campaign_id_returns_404(self, client):
        res = client.get("/campaigns/99999999")
        assert res.status_code == 404
