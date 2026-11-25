"""
Automated verification tests for Model 1 (Multilingual Text Fraud Detection):
- CentralModelLoader SHA-256 verification of promoted v2.1 production model
- Inference API backward compatibility (ScamMessageInferenceEngine + MultilingualScamClassifier)
- Code-mixed Hinglish, spelling variations, regional terminology, and unverified Tamil disclosure
- Presence of per-language metrics, confusion matrices, FNR, and transformer comparison
"""

import json
from pathlib import Path

from backend.app.ml_engine.model_loader import CentralModelLoader
from ml.text_detection.classifier import MultilingualScamClassifier
from ml.text_detection.infer import ScamMessageInferenceEngine


def test_registry_promotes_v21_with_verified_sha256():
    loader = CentralModelLoader()
    status = loader.verify_registry_artifacts()
    assert status.get("text_classification") is True
    entry = loader.get_verified_entry("text_classification")
    assert entry is not None
    assert entry["model_id"] == "trustlens-text-v2.1-candidate"
    assert entry["deployment_status"] == "Production"


def test_inference_api_preserved_and_4class_native():
    clf = MultilingualScamClassifier()
    assert clf.is_trained is True

    res = clf.predict("URGENT: Your SBI KYC is expired. Update at http://sbi-kyc.example.com or account blocked!")
    for key in ("text", "predicted_label", "confidence", "is_threat", "detected_language", "is_trained", "model_version", "explanation", "processing_time_ms"):
        assert key in res
    assert res["is_threat"] is True
    assert res["predicted_label"] in ("spam", "smishing", "scam")
    assert res["model_version"] == "trustlens-model1-v2.1"
    assert res["language_support_status"] == "evaluated"

    legit = clf.predict("Your monthly bank statement for October is ready to view in the official mobile app.")
    assert legit["is_threat"] is False
    assert legit["predicted_label"] == "legitimate"


def test_codemixed_spelling_variation_and_unverified_tamil_disclosure():
    engine = ScamMessageInferenceEngine()
    sp_var = engine.predict("Apka P.YATM K.Y.C expyre ho gya h aaj hi update kro wrna acount blck hoga")
    assert sp_var["detected_language"] == "Hinglish"
    assert sp_var["is_threat"] is True
    assert sp_var["language_support_status"] == "evaluated"

    tamil = engine.predict("உங்கள் வங்கி கணக்கு முடக்கப்படும் உடனே KYC புதுப்பிக்கவும்")
    assert tamil["detected_language"] == "Tamil"
    assert tamil["language_support_status"] == "unsupported_unverified"


def test_multilingual_audit_and_transformer_comparison_report():
    report_path = Path("ml/artifacts/text_detection/multilingual_audit_and_comparison.json")
    assert report_path.exists()
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["unsupported_languages_zero_samples"] == ["Tamil", "Bengali"]
    v21 = data["models_full_test"]["v2.1_union_tfidf_linearsvc"]
    assert set(v21["by_language"].keys()) == {"English", "Hindi", "Hinglish"}
    for lang_metrics in v21["by_language"].values():
        assert "false_negative_rate" in lang_metrics
        assert "confusion_matrix_2x2" in lang_metrics
        assert "4class_confusion_matrix" in lang_metrics
    assert "multilingual_minilm_l12_v2_linearsvc" in data["transformer_comparison_slice"]
