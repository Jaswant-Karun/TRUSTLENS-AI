"""
TRUSTLENS AI - Model 3: Multi-Label Scam Tactic Inference Pipeline
Production inference engine for detecting manipulation tactics, extracting token evidence,
and formulating plain-English explainable assessments.
"""

import sys
import os
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import joblib
import numpy as np

from ml.tactic_detection.taxonomy import (
    TACTIC_REGISTRY,
    SUPPORTED_TACTIC_KEYS,
    ALL_TACTIC_KEYS,
)
from ml.tactic_detection.labels import TACTIC_LABELS, SUPPORTED_LABELS


class ScamTacticInferenceEngine:
    """Production inference engine for Model 3."""

    def __init__(self, artifacts_dir: Optional[str] = None):
        self.artifacts_dir = Path(artifacts_dir or "ml/artifacts/tactic_detection")
        v2_dir = self.artifacts_dir / "v2.3_candidate"
        v2_model = v2_dir / "ovr_linearsvc.joblib"
        v2_vec = v2_dir / "vectorizer.joblib"
        v2_eval = v2_dir / "evaluation_report.json"

        if v2_model.exists() and v2_vec.exists():
            self.model_path = v2_model
            self.vectorizer_path = v2_vec
            self.eval_report_path = v2_eval
            self.thresholds_path = self.artifacts_dir / "thresholds.json"
            self.is_v23 = True
            self.active_keys = SUPPORTED_LABELS
            self.model_version_tag = "trustlens-model3-calibrated-linear-v2.3"
        else:
            self.model_path = self.artifacts_dir / "best_tactic_model.joblib"
            self.vectorizer_path = self.artifacts_dir / "vectorizer.joblib"
            self.eval_report_path = None
            self.thresholds_path = self.artifacts_dir / "thresholds.json"
            self.is_v23 = False
            self.active_keys = SUPPORTED_TACTIC_KEYS
            self.model_version_tag = "trustlens-model3-calibrated-linear-v1.0"

        self.model = None
        self.vectorizer = None
        self.thresholds: Dict[str, float] = {}
        self.is_loaded = False
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        if self.model_path.exists() and self.vectorizer_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
                if self.is_v23 and self.eval_report_path and self.eval_report_path.exists():
                    rep = json.loads(self.eval_report_path.read_text(encoding="utf-8"))
                    per_lbl = rep.get("selected_model_summary", {}).get("per_label", {})
                    self.thresholds = {k: float(per_lbl[k]["threshold"]) for k in self.active_keys if k in per_lbl}
                elif self.thresholds_path.exists():
                    with open(self.thresholds_path, "r", encoding="utf-8") as f:
                        self.thresholds = json.load(f)
                else:
                    self.thresholds = {k: 0.50 for k in self.active_keys}
                self.is_loaded = True
            except Exception as e:
                print(f"[WARN] Failed to load tactic artifacts: {e}")
                self.is_loaded = False
        else:
            self.is_loaded = False

    def extract_model_evidence(self, X_vec, label_idx: int, top_k: int = 4) -> List[str]:
        """Extracts model-grounded top contributing TF-IDF n-grams for the predicted tactic."""
        try:
            est = self.model.estimators_[label_idx]
            if hasattr(est, "calibrated_classifiers_"):
                coef = est.calibrated_classifiers_[0].estimator.coef_[0]
            elif hasattr(est, "coef_"):
                coef = est.coef_[0]
            else:
                return []
            nonzero_idx = X_vec.nonzero()[1]
            if len(nonzero_idx) == 0:
                return []
            feature_names = np.array(self.vectorizer.get_feature_names_out())
            contributions = X_vec.data * coef[nonzero_idx]
            pos_mask = contributions > 0
            if not np.any(pos_mask):
                return []
            pos_indices = nonzero_idx[pos_mask]
            pos_contribs = contributions[pos_mask]
            top_idx = pos_indices[np.argsort(pos_contribs)[-top_k:]]
            return [
                str(feature_names[i]).replace("word__", "").replace("char__", "")
                for i in reversed(top_idx)
            ]
        except Exception:
            return []

    def extract_evidence(self, text: str, tactic_key: str) -> List[str]:
        """Fallback characteristic threat keywords per tactic."""
        text_lower = text.lower()
        evidence = []
        evidence_clues = {
            "urgency_time_pressure": ["immediate", "turant", "today", "24 hours", "24 hrs", "now", "urgent", "deadline", "last date", "jaldi"],
            "threats_intimidation": ["disconnect", "block", "freeze", "police", "legal", "arrest", "action", "penalty", "challan", "court"],
            "otp_credential_requests": ["otp", "pin", "password", "cvv", "verification", "secret code", "credentials", "share"],
            "financial_manipulation": ["debit", "credited", "transfer", "amount", "charge", "refund", "fee", "loan", "rs", "inr"],
            "authority_impersonation": ["sbi", "hdfc", "icici", "pnb", "rbi", "income tax", "customs", "govt", "police", "electricity"],
            "bank_impersonation": ["sbi", "hdfc", "icici", "pnb", "rbi", "bank", "kyc", "loan", "account"],
            "government_impersonation": ["police", "income tax", "customs", "govt", "challan", "electricity", "uidai", "aadhaar"],
            "fake_employment": ["part-time", "job", "salary", "daily income", "telegram", "task", "youtube", "earn", "work from home"],
            "account_suspension": ["blocked", "block", "suspend", "kyc", "pan", "deactivat", "freeze", "band"],
            "account_suspension_threats": ["blocked", "block", "suspend", "kyc", "pan", "deactivat", "freeze", "band"],
            "prize_reward_scams": ["won", "winner", "lottery", "prize", "cash", "lucky", "crore", "lakhs", "congratulations", "gift", "reward"],
            "prize_reward_manipulation": ["won", "winner", "lottery", "prize", "cash", "lucky", "crore", "lakhs", "congratulations", "gift", "reward"],
            "refund_payment_manipulation": ["refund", "upi", "collect", "cashback", "courier", "delivery", "pay", "qr code"],
        }
        for clue in evidence_clues.get(tactic_key, []):
            if clue in text_lower:
                evidence.append(clue)
        return evidence[:5]

    def _get_meta(self, key: str) -> Dict[str, Any]:
        if key in TACTIC_REGISTRY:
            return TACTIC_REGISTRY[key]
        lbl = TACTIC_LABELS.get(key, {})
        threat_lvl = "critical" if key in {"threats_intimidation", "otp_credential_requests"} else (
            "medium" if key in {"fake_employment", "prize_reward_manipulation"} else "high"
        )
        return {
            "name": lbl.get("name", key),
            "code": lbl.get("code", key.upper()),
            "threat_level": threat_lvl,
            "description": lbl.get("source", lbl.get("name", key)),
        }

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Analyzes a message and returns all detected psychological manipulation tactics,
        calibrated confidence scores, model-grounded evidence tokens, and plain-English explanations.
        """
        start_time = time.perf_counter()
        clean_text = str(text).strip()

        if not self.is_loaded or not clean_text:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "text": text,
                "tactics": [],
                "tactic_count": 0,
                "primary_vector": None,
                "model_version": "uninitialized",
                "processing_time_ms": latency_ms,
                "status": "model_not_loaded",
            }

        # Vectorize input
        X_vec = self.vectorizer.transform([clean_text])
        probs = self.model.predict_proba(X_vec)[0]

        detected = []
        for idx, key in enumerate(self.active_keys):
            conf = float(probs[idx])
            thresh = self.thresholds.get(key, 0.50)
            meta = self._get_meta(key)

            if conf >= thresh:
                model_tokens = self.extract_model_evidence(X_vec, idx, top_k=4)
                evidence = model_tokens if model_tokens else self.extract_evidence(clean_text, key)
                detected.append({
                    "tactic_id": key,
                    "tactic_name": meta["name"],
                    "tactic_code": meta["code"],
                    "threat_level": meta["threat_level"],
                    "confidence": round(conf, 4),
                    "threshold_applied": thresh,
                    "explanation": meta["description"],
                    "evidence_tokens": evidence,
                    "evidence_source": "linear_saliency" if model_tokens else "keyword_clue",
                })

        # Sort detected tactics by confidence descending
        detected.sort(key=lambda x: x["confidence"], reverse=True)
        primary_vector = detected[0]["tactic_name"] if detected else None

        # Check for investment keywords to surface transparent advisory without fabricating a model
        investment_advisory = None
        invest_keywords = ["invest", "trading", "crypto", "bitcoin", "forex", "daily profit", "guaranteed return"]
        if any(kw in clean_text.lower() for kw in invest_keywords):
            investment_advisory = {
                "tactic_id": "fake_investment",
                "tactic_name": "Fake Investment Opportunities",
                "status": "unavailable_no_ground_truth_labels",
                "advisory": (
                    "Message contains investment keywords. Note: TRUSTLENS AI explicitly does not fabricate "
                    "a trained ML classifier for 'Fake Investment Opportunities' due to absence of verified ground-truth "
                    "training labels in the benchmark dataset (compliance with anti-fabrication policy)."
                ),
            }

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "text": text,
            "tactics": detected,
            "tactic_count": len(detected),
            "primary_vector": primary_vector,
            "investment_advisory": investment_advisory,
            "model_version": self.model_version_tag,
            "processing_time_ms": latency_ms,
        }


tactic_engine = ScamTacticInferenceEngine()


if __name__ == "__main__":
    samples = [
        "Dear SBI Customer, your bank account will be blocked today within 24 hours. Update KYC immediately.",
        "Congratulations! You have won Rs 25,00,000 in KBC Lucky Draw. Call now to claim prize.",
        "Your electricity power will be disconnected tonight at 9:30 PM due to unpaid bill. Pay immediately.",
        "Hi, part time job opportunity. Earn 3000 to 5000 daily by liking YouTube videos. Contact on Telegram.",
        "Hey, are you free for lunch tomorrow at 1 PM?",
    ]
    for s in samples:
        print("\n" + "=" * 60)
        print("Message:", s)
        res = tactic_engine.predict(s)
        print(f"Detected Tactics ({res['tactic_count']}):")
        for t in res["tactics"]:
            print(f"  - [{t['threat_level'].upper()}] {t['tactic_name']} (Conf: {t['confidence']:.2%}) | Evidence: {t['evidence_tokens']}")
        if res.get("investment_advisory"):
            print("  - [ADVISORY]", res["investment_advisory"]["advisory"])
