"""
Automated tests for Risk Aggregation & Explainability:
- Separation of model_probabilities, risk_normalization, and severity_classification
- Uncalibrated model outputs never misrepresented as calibrated probabilities
- Model-specific uncertainty & version tracking
- SHAP TreeExplainer (v2.2 URL) and Linear Saliency (v2.1 Text) explainability
"""

from backend.app.services.risk_service import TransparentRiskAggregationService
from ml.explainability.explainer import TrustLensURLExplainer, TrustLensTextExplainer


def test_calibrated_vs_uncalibrated_separation():
    svc = TransparentRiskAggregationService()

    # 1. Platt-calibrated text + tactics -> calibrated_probability_verified=True
    res_cal = svc.assess_risk(
        text_result={"is_threat": True, "confidence": 0.94, "model_version": "trustlens-model1-v2.1", "detected_language": "English"},
        tactic_result={"tactics": [{"tactic_name": "Urgency and Time Pressure", "confidence": 0.91}], "model_version": "trustlens-model3-calibrated-linear-v2.3"},
        raw_content="Urgent verify your KYC now",
    )
    assert res_cal["uncertainty_assessment"]["calibrated_probability_verified"] is True
    assert res_cal["model_probabilities"]["text_model"]["calibrated"] is True
    assert res_cal["model_versions"]["text_model"] == "trustlens-model1-v2.1"
    assert res_cal["severity_classification"]["level"] == res_cal["threat_level"]
    assert res_cal["risk_normalization"]["normalized_risk_score"] == res_cal["risk_score"]
    assert "Platt-calibrated" in res_cal["human_readable_explanation"]

    # 2. Uncalibrated URL model alone -> calibrated_probability_verified=False
    res_url = svc.assess_risk(
        url_result={"is_phishing": True, "risk_score": 0.96, "model_version": "trustlens-model2-xgboost-v2.2", "features": {"url_length": 45}},
        raw_content="http://192.168.1.50/sbi-kyc.php",
    )
    assert res_url["uncertainty_assessment"]["calibrated_probability_verified"] is False
    assert res_url["model_probabilities"]["url_model"]["calibrated"] is False
    assert res_url["model_versions"]["url_model"] == "trustlens-model2-xgboost-v2.2"


def test_uncertainty_for_borderline_and_unverified_language():
    svc = TransparentRiskAggregationService()
    res = svc.assess_risk(
        text_result={
            "is_threat": True,
            "confidence": 0.55,
            "model_version": "trustlens-model1-v2.1",
            "detected_language": "Tamil",
            "language_support_status": "unsupported_unverified",
        },
        raw_content="உங்கள் வங்கி கணக்கு முடக்கப்படும்",
    )
    assert res["uncertainty_assessment"]["overall_uncertainty"] >= 0.85
    assert res["uncertainty_assessment"]["requires_human_review"] is True
    assert any("Tamil" in r for r in res["uncertainty_assessment"]["uncertainty_reasons"])


def test_v2_shap_and_linear_explainers():
    url_exp = TrustLensURLExplainer()
    assert url_exp.is_loaded is True
    u_out = url_exp.explain("http://192.168.1.100/secure-login/index.php?kyc=1")
    assert len(u_out["top_risk_factors"]) > 0
    assert "TreeExplainer" in u_out["methodology"]

    txt_exp = TrustLensTextExplainer()
    assert txt_exp.is_loaded is True
    t_out = txt_exp.explain("URGENT: Your SBI KYC is expired, update immediately!")
    assert len(t_out["evidence_tokens"]) > 0
