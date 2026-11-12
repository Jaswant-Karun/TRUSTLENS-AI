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


class ScamTacticInferenceEngine:
    """Production inference engine for Model 3."""

    def __init__(self, artifacts_dir: Optional[str] = None):
        self.artifacts_dir = Path(artifacts_dir or "ml/artifacts/tactic_detection")
        self.model_path = self.artifacts_dir / "best_tactic_model.joblib"
        self.vectorizer_path = self.artifacts_dir / "vectorizer.joblib"
        self.thresholds_path = self.artifacts_dir / "thresholds.json"
        self.metadata_path = self.artifacts_dir / "tactic_metadata.json"

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
                if self.thresholds_path.exists():
                    with open(self.thresholds_path, "r", encoding="utf-8") as f:
                        self.thresholds = json.load(f)
                else:
                    self.thresholds = {k: 0.50 for k in SUPPORTED_TACTIC_KEYS}
                self.is_loaded = True
            except Exception as e:
                print(f"[WARN] Failed to load tactic artifacts: {e}")
                self.is_loaded = False
        else:
            self.is_loaded = False

    def extract_evidence(self, text: str, tactic_key: str) -> List[str]:
        """Extracts key evidence words and salient tokens from the message."""
        text_lower = text.lower()
        evidence = []

        # Characteristic threat keywords per tactic for context extraction
        evidence_clues = {
            "urgency_time_pressure": ["immediate", "turant", "today", "24 hours", "24 hrs", "now", "urgent", "deadline", "last date", "jaldi"],
            "threats_intimidation": ["disconnect", "block", "freeze", "police", "legal", "arrest", "action", "penalty", "challan", "court"],
            "otp_credential_requests": ["otp", "pin", "password", "cvv", "verification", "secret code", "credentials", "share"],
            "financial_manipulation": ["debit", "credited", "transfer", "amount", "charge", "refund", "fee", "loan", "rs", "inr"],
            "authority_impersonation": ["sbi", "hdfc", "icici", "pnb", "rbi", "income tax", "customs", "govt", "police", "electricity"],
            "fake_employment": ["part-time", "job", "salary", "daily income", "telegram", "task", "youtube", "earn", "work from home"],
            "account_suspension": ["blocked", "block", "suspend", "kyc", "pan", "deactivat", "freeze", "band"],
            "prize_reward_scams": ["won", "winner", "lottery", "prize", "cash", "lucky", "crore", "lakhs", "congratulations", "gift", "reward"],
            "refund_payment_manipulation": ["refund", "upi", "collect", "cashback", "courier", "delivery", "pay", "qr code"],
        }

        clues = evidence_clues.get(tactic_key, [])
        for clue in clues:
            if clue in text_lower:
                evidence.append(clue)

        return evidence[:5]

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Analyzes a message and returns all detected psychological manipulation tactics,
        confidence scores, supporting evidence, and plain-English explanations.
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
        for idx, key in enumerate(SUPPORTED_TACTIC_KEYS):
            conf = float(probs[idx])
            thresh = self.thresholds.get(key, 0.50)
            meta = TACTIC_REGISTRY[key]

            if conf >= thresh:
                evidence = self.extract_evidence(clean_text, key)
                detected.append({
                    "tactic_id": key,
                    "tactic_name": meta["name"],
                    "tactic_code": meta["code"],
                    "threat_level": meta["threat_level"],
                    "confidence": round(conf, 4),
                    "threshold_applied": thresh,
                    "explanation": meta["description"],
                    "evidence_tokens": evidence,
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
            "model_version": "trustlens-model3-calibrated-linear-v1.0",
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
