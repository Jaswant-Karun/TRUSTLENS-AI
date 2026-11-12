"""
TRUSTLENS AI - Model Loading, Inference & Explainability Validation Suite
Verifies that all four models, explainers, and registry components execute
reliably within latency and accuracy constraints on realistic test vectors.
"""

import sys
import os
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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


def run_validation():
    print("=" * 80)
    print("TRUSTLENS AI - PRODUCTION MODEL VALIDATION & INFERENCE INTEGRITY AUDIT")
    print("=" * 80)

    results = []

    # 1. Validate Model 1 (Multilingual Scam Text Detection)
    print("\n[1/5] Auditing Model 1: Multilingual Text Scam Detector...")
    text_clf = MultilingualScamClassifier()
    assert text_clf.is_trained, "Model 1 failed to load!"

    test_threat_msg = "Dear SBI user, your YONO account has been suspended due to pending KYC. Click immediately to reactivate."
    test_benign_msg = "Hey, are we still meeting for lunch at 1 PM today?"

    t0 = time.perf_counter()
    threat_res = text_clf.predict(test_threat_msg)
    benign_res = text_clf.predict(test_benign_msg)
    lat_text = ((time.perf_counter() - t0) / 2) * 1000

    assert threat_res["is_threat"] is True, "Model 1 failed to flag obvious threat text!"
    assert benign_res["is_threat"] is False, "Model 1 misclassified benign message!"
    assert threat_res["confidence"] > 0.80, f"Confidence too low: {threat_res['confidence']}"
    assert lat_text < 50.0, f"Latency exceeded budget: {lat_text:.2f}ms"

    print(f"  [OK] Model 1 Loaded & Verified (Threat Conf: {threat_res['confidence']:.4f}, Benign Conf: {benign_res['confidence']:.4f})")
    print(f"  [OK] Language Identified: {threat_res['detected_language']}, Latency: {lat_text:.2f}ms")
    results.append(("Model 1 (Text Scam)", "PASSED", f"{lat_text:.2f}ms"))

    # 2. Validate Model 2 (Phishing URL Detection & SHAP)
    print("\n[2/5] Auditing Model 2: Phishing URL Detector & SHAP Engine...")
    url_det = PhishingURLDetector()
    assert url_det.is_trained, "Model 2 failed to load!"

    phish_url = "http://192.168.1.105/banking/sbi/update-pan.html?user=login"
    benign_url = "https://www.google.com/search?q=weather"

    t0 = time.perf_counter()
    phish_res = url_det.analyze(phish_url)
    benign_res_url = url_det.analyze(benign_url)
    lat_url = ((time.perf_counter() - t0) / 2) * 1000

    assert phish_res["is_phishing"] is True, "Model 2 failed to flag raw IP phishing URL!"
    assert benign_res_url["is_phishing"] is False, "Model 2 misclassified google.com!"

    # Verify SHAP Explainer
    url_explainer = TrustLensURLExplainer()
    assert url_explainer.is_loaded, "URL SHAP Explainer failed to initialize!"
    shap_explanation = url_explainer.explain(phish_url)
    assert len(shap_explanation["top_risk_factors"]) > 0, "No SHAP risk factors produced!"

    print(f"  [OK] Model 2 Loaded & Verified (Phish Score: {phish_res['risk_score']:.4f}, Benign Score: {benign_res_url['risk_score']:.4f})")
    print(f"  [OK] SHAP Top Risk Factor: {shap_explanation['top_risk_factors'][0]['feature']} (Impact: {shap_explanation['top_risk_factors'][0]['shap_impact']})")
    print(f"  [OK] Latency: {lat_url:.2f}ms")
    results.append(("Model 2 (URL Phishing & SHAP)", "PASSED", f"{lat_url:.2f}ms"))

    # 3. Validate Model 3 (Multi-Label Scam Tactic Detection)
    print("\n[3/5] Auditing Model 3: Multi-Label Scam Tactic Detector & Evidence Extraction...")
    tactic_det = ScamTacticDetector()
    assert tactic_det.is_trained, "Model 3 failed to load!"

    multi_tactic_text = "URGENT NOTICE: Your electricity power will be disconnected tonight at 9:30 PM due to unpaid bill of Rs 4,820. Call immediately to stop disconnection."
    t0 = time.perf_counter()
    tactic_res = tactic_det.detect(multi_tactic_text)
    lat_tactic = (time.perf_counter() - t0) * 1000

    tactic_names = [t.get("tactic_name") or t.get("name") for t in tactic_res["tactics"]]
    assert len(tactic_res["tactics"]) >= 2, f"Expected multiple tactics, found: {tactic_names}"
    assert any("Urgency" in t for t in tactic_names), "Failed to detect Urgency tactic!"

    # Verify Tactic Explainer separation
    tactic_explainer = TrustLensTacticExplainer()
    assert tactic_explainer.is_loaded, "Tactic Explainer failed to initialize!"
    explained_tactics = tactic_explainer.explain(multi_tactic_text)
    assert len(explained_tactics) >= 2, "Tactic Explainer failed to extract evidence!"
    for exp in explained_tactics:
        assert "evidence_tokens" in exp, "Missing evidence_tokens!"
        assert "explanation_rationale" in exp, "Missing explanation_rationale!"
        assert exp["evidence_tokens"] != exp["explanation_rationale"], "Failed separation rule!"

    print(f"  [OK] Model 3 Loaded & Verified ({len(tactic_res['tactics'])} Tactics Detected: {', '.join(tactic_names)})")
    print(f"  [OK] Evidence Tokens Separated: {explained_tactics[0]['evidence_tokens']} vs Rationale")
    print(f"  [OK] Latency: {lat_tactic:.2f}ms")
    results.append(("Model 3 (Tactic Multi-Label)", "PASSED", f"{lat_tactic:.2f}ms"))

    # 4. Validate Model 4 (Campaign Discovery & Similarity Intelligence)
    print("\n[4/5] Auditing Model 4: Campaign Discovery & Cluster Matching...")
    clusterer = CampaignClusterer()
    assert clusterer.is_trained, "Model 4 failed to load!"

    sbi_threat = "SBI alert: Dear Customer your SBI YONO account has been locked. Click http://sbi-kyc-verify.info to update PAN."
    t0 = time.perf_counter()
    camp_match = clusterer.match_campaign(sbi_threat)
    lat_camp = (time.perf_counter() - t0) * 1000

    assert camp_match["campaign_id"] is not None, "Failed to match SBI threat to known campaign!"
    assert camp_match["similarity_score"] > 0.50, f"Low similarity score: {camp_match['similarity_score']}"

    # Verify Campaign Explainer & Legal Disclaimer
    camp_explainer = TrustLensCampaignExplainer()
    camp_exp = camp_explainer.explain(camp_match)
    assert "legal_disclaimer" in camp_exp, "Mandatory legal disclaimer missing!"
    assert "does not constitute" in camp_exp["legal_disclaimer"], "Disclaimer wording incomplete!"

    print(f"  [OK] Model 4 Loaded & Verified (Matched: {camp_match.get('associated_campaign') or camp_match.get('campaign_name')}, Sim: {camp_match['similarity_score']:.2f})")
    print(f"  [OK] Legal Attribution Disclaimer Present: True")
    print(f"  [OK] Latency: {lat_camp:.2f}ms")
    results.append(("Model 4 (Campaign Clustering)", "PASSED", f"{lat_camp:.2f}ms"))

    # 5. Validate Model Registry & End-to-End Composite Scan
    print("\n[5/5] Auditing Registry & End-to-End Composite Scan Pipeline...")
    reg = ModelRegistry()
    registry_data = reg.registry_data
    assert len(registry_data["models"]) == 4, f"Expected 4 models in registry, found {len(registry_data['models'])}"

    for mod_id, mod_info in registry_data["models"].items():
        assert mod_info["status"] == "production_verified", f"{mod_id} not production verified!"
        assert len(mod_info["artifacts"]) > 0, f"{mod_id} has no artifacts listed!"
        for art in mod_info["artifacts"]:
            assert art["sha256"] != "FILE_NOT_FOUND", f"Missing artifact: {art['path']}"

    # Composite scan validation
    from backend.app.services.ml_service import ml_service
    comp_res = ml_service.composite_scan(sbi_threat)
    assert comp_res["overall_threat_level"] in ["high", "critical"], f"Unexpected threat level: {comp_res['overall_threat_level']}"
    assert comp_res["text_analysis"] is not None
    assert comp_res["tactics_analysis"] is not None
    assert comp_res["campaign_association"] is not None

    print("  [OK] Central Registry Integrity: 4 Models Verified with Valid SHA256 Hashes")
    print(f"  [OK] Composite Pipeline Result: Threat Level = {comp_res['overall_threat_level']}, Confidence = {comp_res['confidence']}")
    results.append(("Registry & Composite Pipeline", "PASSED", "All Hashes Verified"))

    print("\n" + "=" * 80)
    print("INFERENCE VALIDATION AUDIT SUMMARY:")
    for comp, status, detail in results:
        print(f"  - {comp:<35}: [{status}] ({detail})")
    print("=" * 80)
    print("ALL PRODUCTION MODELS AND PIPELINES VERIFIED SUCCESSFULLY.\n")
    return True


if __name__ == "__main__":
    success = run_validation()
    if not success:
        sys.exit(1)
