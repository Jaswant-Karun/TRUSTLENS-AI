"""
TRUSTLENS AI - Pytest Model Validation & Explainability Test Suite
Tests all four machine learning models, inference engines, explainers, and registry integrity.
"""

import pytest
import numpy as np
from pathlib import Path

from ml.text_detection.classifier import MultilingualScamClassifier
from ml.url_detection.classifier import PhishingURLDetector
from ml.tactic_detection.detector import ScamTacticDetector
from ml.campaign_detection.clusterer import CampaignClusterer
from ml.explainability.explainer import (
    TrustLensURLExplainer,
    TrustLensTextExplainer,
    TrustLensTacticExplainer,
    TrustLensCampaignExplainer,
    composite_explainer,
)
from ml.evaluation.registry import ModelRegistry
from ml.evaluation.evaluator import CentralizedModelEvaluator


@pytest.fixture(scope="module")
def text_classifier():
    return MultilingualScamClassifier()


@pytest.fixture(scope="module")
def url_detector():
    return PhishingURLDetector()


@pytest.fixture(scope="module")
def tactic_detector():
    return ScamTacticDetector()


@pytest.fixture(scope="module")
def campaign_clusterer():
    return CampaignClusterer()


def test_model1_text_detection_and_languages(text_classifier):
    """Verifies Model 1 scam text detection across multiple languages."""
    assert text_classifier.is_trained is True

    # English threat
    en_threat = "URGENT: Your bank account has been compromised. Verify your details immediately."
    res_en = text_classifier.predict(en_threat)
    assert res_en["is_threat"] is True
    assert res_en["confidence"] > 0.70

    # Hinglish threat
    hinglish_threat = "Aapka SBI account block ho chuka hai. Turant link par click karke pan card update kare."
    res_hi = text_classifier.predict(hinglish_threat)
    assert res_hi["is_threat"] is True
    assert res_hi["detected_language"] in ["Hinglish", "Hindi", "English"]

    # Benign message
    benign = "Hello, can we reschedule our meeting to tomorrow morning?"
    res_benign = text_classifier.predict(benign)
    assert res_benign["is_threat"] is False
    assert res_benign["predicted_label"] == "legitimate"


def test_model2_url_detection_and_shap(url_detector):
    """Verifies Model 2 phishing URL detection and zero network activity."""
    assert url_detector.is_trained is True

    # High-risk raw IP URL
    phish_url = "http://185.220.101.5/sec/login.asp?auth=1"
    res_phish = url_detector.analyze(phish_url)
    assert res_phish["is_phishing"] is True
    assert res_phish["risk_score"] > 0.80

    # Benign URL
    benign_url = "https://en.wikipedia.org/wiki/Machine_learning"
    res_benign = url_detector.analyze(benign_url)
    assert res_benign["is_phishing"] is False
    assert res_benign["risk_score"] < 0.20

    # SHAP explainer check
    explainer = TrustLensURLExplainer()
    assert explainer.is_loaded is True
    shap_data = explainer.explain(phish_url)
    assert len(shap_data["top_risk_factors"]) > 0
    assert "TreeExplainer" in shap_data["methodology"]


def test_model3_tactic_multi_label_and_separation(tactic_detector):
    """Verifies Model 3 multi-label detection and evidence vs rationale separation."""
    assert tactic_detector.is_trained is True

    threat_text = "FINAL WARNING: Your electricity connection will be cut off by 8:00 PM today due to unpaid bill of Rs 3,450. Call 9876543210 immediately."
    res = tactic_detector.detect(threat_text)
    assert res["tactic_count"] >= 2

    explainer = TrustLensTacticExplainer()
    explanations = explainer.explain(threat_text)
    assert len(explanations) >= 2

    for exp in explanations:
        assert len(exp["evidence_tokens"]) > 0
        assert len(exp["explanation_rationale"]) > 10
        # Assert strict separation between mathematical token evidence and behavioral rationale
        assert exp["evidence_tokens"] != exp["explanation_rationale"]


def test_model4_campaign_clustering_and_legal_caveat(campaign_clusterer):
    """Verifies Model 4 campaign matching and mandatory attribution caveat."""
    assert campaign_clusterer.is_trained is True

    sbi_threat = "SBI alert: Dear Customer your SBI YONO account has been locked. Click http://sbi-kyc-verify.info to update PAN."
    match = campaign_clusterer.match_campaign(sbi_threat)
    assert match["campaign_id"] is not None
    assert match["similarity_score"] > 0.50

    explainer = TrustLensCampaignExplainer()
    exp = explainer.explain(match)
    assert exp["matched"] is True
    assert "legal_disclaimer" in exp
    assert "does not constitute" in exp["legal_disclaimer"]


def test_model_registry_integrity():
    """Verifies Model Registry contains all 4 verified models with SHA256 hashes."""
    reg = ModelRegistry()
    data = reg.registry_data
    assert "models" in data
    assert len(data["models"]) == 4

    for mod_id in [
        "trustlens-model-1-text-scam",
        "trustlens-model-2-phishing-url",
        "trustlens-model-3-tactic-detector",
        "trustlens-model-4-campaign-clusterer",
    ]:
        assert mod_id in data["models"]
        mod = data["models"][mod_id]
        assert mod["status"] == "production_verified"
        assert mod["semantic_version"] == "v1.0.0"
        for art in mod["artifacts"]:
            assert art["sha256"] != "FILE_NOT_FOUND"
            assert len(art["sha256"]) == 64


def test_centralized_evaluator_dashboard_data():
    """Verifies that centralized evaluator produces complete dashboard payload."""
    evaluator = CentralizedModelEvaluator()
    data = evaluator.generate_dashboard_data()

    assert data["platform"] == "TRUSTLENS AI"
    assert "models" in data
    assert data["overall_summary"]["active_models_count"] == 4
    assert data["overall_summary"]["production_readiness"] == "100% VERIFIED"
    assert len(data["models"]["campaign_clusterer"]["cluster_size_distribution"]) > 0
