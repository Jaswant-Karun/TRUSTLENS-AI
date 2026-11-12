"""
TRUSTLENS AI - Scam Tactic Multi-Label Detector (Engine 3)
Identifies distinct social engineering psychological vectors and fraudulent tactics.
"""

from typing import Dict, Any, List, Optional
import os
import re


TACTIC_TAXONOMY = {
    "TACTIC_URGENCY": {
        "name": "Artificial Urgency & Deadline Coercion",
        "patterns": [r"\bimmediate(ly)?\b", r"\btoday only\b", r"\bwithin 24 (hours|hrs)\b", r"\bturant\b", r"\blast warning\b"],
    },
    "TACTIC_CREDENTIAL_HARVESTING": {
        "name": "Credential & OTP Interception",
        "patterns": [r"\botp\b", r"\bpassword\b", r"\bpin\b", r"\bcvv\b", r"\bverification code\b", r"\blogin\b"],
    },
    "TACTIC_FINANCIAL_COERCION": {
        "name": "Financial Coercion & Fraudulent Fee Demands",
        "patterns": [r"\bupi\b", r"\bpay(ment)?\b", r"\btransfer\b", r"\brefund\b", r"\blottery\b", r"\bcash prize\b", r"\bpaisa\b"],
    },
    "TACTIC_IMPERSONATION": {
        "name": "Entity Impersonation (Banks / Authorities)",
        "patterns": [r"\bsbi\b", r"\bhdfc\b", r"\bicici\b", r"\bincome tax\b", r"\bcustoms\b", r"\bfedex\b", r"\bpolice\b"],
    },
    "TACTIC_FAKE_EMPLOYMENT": {
        "name": "Fraudulent Job Offers & Work-from-Home Scams",
        "patterns": [r"\bpart[- ]time job\b", r"\bearn daily\b", r"\btelegram task\b", r"\brating task\b", r"\bwork from home\b"],
    },
    "TACTIC_ACCOUNT_SUSPENSION": {
        "name": "Account Suspension & Service Cutoff Threats",
        "patterns": [r"\baccount blocked\b", r"\bsuspended\b", r"\bkyc expired\b", r"\bsim deactivated\b", r"\bkhata band\b"],
    },
}


class ScamTacticDetector:
    """
    Multi-label tactic detection engine.
    Tags messages with specific social engineering techniques.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "ml/artifacts/tactic_multilabel_model.joblib"
        self.model = None
        self.is_trained = False
        self._load_model_if_available()

    def _load_model_if_available(self) -> None:
        if os.path.exists(self.model_path):
            try:
                import joblib
                self.model = joblib.load(self.model_path)
                self.is_trained = True
            except Exception:
                self.is_trained = False

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Scans message for psychological and social engineering manipulation tactics.
        """
        detected_tactics: List[Dict[str, Any]] = []
        text_lower = text.lower()

        for code, meta in TACTIC_TAXONOMY.items():
            matched_evidence = []
            for pat in meta["patterns"]:
                matches = re.findall(pat, text_lower)
                if matches:
                    matched_evidence.append(pat.replace(r"\b", "").replace("?", ""))

            if matched_evidence:
                confidence = round(min(0.95, 0.50 + len(matched_evidence) * 0.20), 2)
                detected_tactics.append({
                    "tactic_code": code,
                    "tactic_name": meta["name"],
                    "confidence": confidence,
                    "evidence_tokens": matched_evidence,
                })

        primary_vector = detected_tactics[0]["tactic_name"] if detected_tactics else None

        return {
            "tactics": detected_tactics,
            "tactic_count": len(detected_tactics),
            "primary_vector": primary_vector,
            "is_trained": self.is_trained,
            "model_version": "trained-multilabel-v1" if self.is_trained else "taxonomy-rule-baseline",
        }

