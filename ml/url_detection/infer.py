"""
TRUSTLENS AI - Model 2 Production URL Inference Pipeline
Evaluates untrusted raw URLs strictly through deterministic lexical and entropy features.
Guarantees zero outbound network connections to target endpoints.
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import pandas as pd
import numpy as np

from ml.url_detection.features import extract_url_features, FEATURE_COLUMNS


class PhishingURLInferenceEngine:
    """Production inference engine for Model 2."""

    def __init__(self, artifacts_dir: Optional[str] = None):
        self.artifacts_dir = Path(artifacts_dir or "ml/artifacts/url_detection")
        self.model_path = self.artifacts_dir / "best_url_model.joblib"
        self.feature_schema_path = self.artifacts_dir / "feature_schema.json"

        self.model = None
        self.is_loaded = False
        self._load_model()

    def _load_model(self) -> None:
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                self.is_loaded = True
            except Exception as e:
                print(f"[WARN] Failed to load URL model: {e}")
                self.is_loaded = False
        else:
            self.is_loaded = False

    def identify_risk_factors(self, features: Dict[str, Any]) -> List[str]:
        """Identifies key contributing risk factors from structural properties."""
        factors = []
        if features.get("has_ip_address", 0) == 1:
            factors.append("Direct IPv4/IPv6 address used in place of domain name")
        if features.get("percentage_numeric_chars", 0.0) > 25.0:
            factors.append(f"High numeric character density ({features['percentage_numeric_chars']:.1f}%)")
        if features.get("dot_count", 0) >= 3:
            factors.append(f"High dot count ({features['dot_count']} dots) indicates nested spoofing subdomains")
        if features.get("url_entropy", 0.0) > 4.2:
            factors.append(f"High URL Shannon entropy ({features['url_entropy']:.2f}) indicates algorithmic generation")
        if features.get("has_hyphen_in_domain", 0) == 1:
            factors.append("Hyphen present in domain name (common typo-squatting indicator)")
        if features.get("suspicious_file_extension", 0) == 1:
            factors.append("Suspicious executable or script file extension in URL path")
        if features.get("https_flag", 1) == 0:
            factors.append("Unencrypted HTTP transmission scheme")
        return factors

    def predict(self, raw_url: str) -> Dict[str, Any]:
        """Evaluates an untrusted raw URL string."""
        start_time = time.perf_counter()

        # Step 1: Deterministic offline feature extraction
        features = extract_url_features(raw_url)
        risk_factors = self.identify_risk_factors(features)

        if not self.is_loaded:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "url": raw_url,
                "is_phishing": False,
                "predicted_label": "unclassified",
                "risk_score": 0.0,
                "features": features,
                "top_risk_factors": risk_factors,
                "model_version": "uninitialized",
                "processing_time_ms": latency_ms,
                "security_note": "Offline lexical analysis only. No network request initiated.",
            }

        # Step 2: Model Prediction
        df_feats = pd.DataFrame([[features[c] for c in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
        pred_prob = float(self.model.predict_proba(df_feats.values)[0][1])
        is_phishing = bool(pred_prob >= 0.50)
        predicted_label = "phishing" if is_phishing else "legitimate"

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "url": raw_url,
            "is_phishing": is_phishing,
            "predicted_label": predicted_label,
            "risk_score": round(pred_prob, 4),
            "features": features,
            "top_risk_factors": risk_factors,
            "model_version": "trustlens-model2-xgboost-v1.0",
            "processing_time_ms": latency_ms,
            "security_disclaimer": "Lexical indicators provide statistical risk profiling and do not prove server maliciousness.",
        }


url_engine = PhishingURLInferenceEngine()


if __name__ == "__main__":
    test_urls = [
        "https://keraekken-loagginnusa.godaddysites.com/",
        "http://192.168.1.100/secure-banking-login/index.php?update_kyc=98214",
        "https://stackoverflow.com/questions/tagged/python",
        "https://github.com/torvalds/linux"
    ]
    for u in test_urls:
        print("\nURL:", u)
        res = url_engine.predict(u)
        print("Prediction:", res["predicted_label"], "| Risk Score:", res["risk_score"], "| Latency:", res["processing_time_ms"], "ms")
        print("Risk Factors:", res["top_risk_factors"])
