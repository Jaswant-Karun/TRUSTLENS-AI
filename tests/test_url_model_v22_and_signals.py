"""
Automated verification tests for Model 2 (URL Phishing Detection v2.2 + Signals):
- CentralModelLoader SHA-256 verification of promoted v2.2 production model
- Independent domain-grouped test split metrics (precision, recall, F1, FPR, FNR)
- False-positive mitigation on legitimate URLs without weakening open-redirect / homograph / typosquatting detection
- Zero outbound network calls enforced
"""

import socket
from unittest.mock import patch
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

from backend.app.ml_engine.model_loader import CentralModelLoader
from ml.url_detection.features import FEATURE_COLUMNS
from ml.url_detection.infer import PhishingURLInferenceEngine


def test_registry_promotes_url_v22_with_verified_sha256():
    loader = CentralModelLoader()
    status = loader.verify_registry_artifacts()
    assert status.get("url_phishing_classification") is True
    entry = loader.get_verified_entry("url_phishing_classification")
    assert entry is not None
    assert entry["model_id"] == "trustlens-url-v2.2-candidate"
    assert entry["deployment_status"] == "Production"


def test_independent_domain_grouped_test_metrics():
    engine = PhishingURLInferenceEngine()
    assert engine.is_loaded is True
    assert engine.model_version_tag == "trustlens-model2-xgboost-v2.2"

    te = pd.read_parquet("data/processed/urls_test.parquet")
    X_te = te[FEATURE_COLUMNS].astype(float).values
    y_te = te["is_phishing"].astype(int).values
    probs = engine.model.predict_proba(X_te)[:, 1]
    preds = (probs >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_te, preds).ravel()

    assert precision_score(y_te, preds) >= 0.995
    assert recall_score(y_te, preds) >= 0.995
    assert f1_score(y_te, preds) >= 0.995
    assert (fp / (fp + tn)) <= 0.005
    assert (fn / (fn + tp)) <= 0.005


def test_false_positive_mitigation_and_security_invariants():
    engine = PhishingURLInferenceEngine()

    with patch.object(socket, "getaddrinfo", side_effect=AssertionError("Network call forbidden!")):
        # 1. Legitimate URLs with paths/subdomains should NOT be flagged as phishing
        for legit_url in [
            "https://www.google.com/search?q=python",
            "https://github.com/torvalds/linux",
            "https://docs.python.org/3/library/urllib.parse.html",
            "https://www.onlinesbi.sbi/personal/index.html",
        ]:
            res = engine.predict(legit_url)
            assert res["is_phishing"] is False, f"FP on {legit_url}: {res['risk_score']}"
            assert res["predicted_label"] == "legitimate"
            assert res["risk_score"] <= 0.12
            assert res["security_signals"]["redirect_behavior"]["live_redirect_followed"] is False
            assert res["security_signals"]["dns_certificate_evidence"]["live_dns_resolved"] is False

        # 2. Open redirect on official domain MUST NOT be capped
        redir = engine.predict("https://github.com/login?redirect=https://evil-phish.xyz")
        assert redir["fp_mitigation_applied"] is None
        assert redir["security_signals"]["redirect_behavior"]["open_redirect_param_detected"] is True

        # 3. Homograph / Punycode
        homo = engine.predict("https://xn--pypal-4ve.com/login")
        assert homo["is_phishing"] is True
        assert homo["security_signals"]["homograph_and_typosquatting"]["homograph_detected"] is True

        # 4. Typosquatting
        typo = engine.predict("https://paypa1.com/login")
        assert typo["is_phishing"] is True
        assert typo["security_signals"]["homograph_and_typosquatting"]["typosquatting_detected"] is True

        # 5. Brand impersonation
        brand = engine.predict("https://sbi-kyc-update.xyz/verify")
        assert brand["is_phishing"] is True
        assert brand["security_signals"]["brand_impersonation"]["detected"] is True
        assert "sbi" in brand["security_signals"]["brand_impersonation"]["brands"]
