"""
TRUSTLENS AI - Phase 2.3: Social Engineering Tactic Taxonomy & Label Mapping
Defines the 10 target tactics, genuine ScamShield annotation mappings,
explicitly unavailable labels (fake_investment), and human annotation workflow schema.
"""

import json
from typing import Dict, Any, List

TACTIC_LABELS: Dict[str, Dict[str, Any]] = {
    "urgency_time_pressure": {
        "name": "Urgency and Time Pressure",
        "code": "TACTIC_URGENCY",
        "supported": True,
        "source": "ScamShield head1_social_engineering.urgency == 1",
    },
    "threats_intimidation": {
        "name": "Threats and Intimidation",
        "code": "TACTIC_INTIMIDATION",
        "supported": True,
        "source": "ScamShield head1.fear == 1 OR head2 in ['Electricity Disconnection', 'Traffic e-Challan']",
    },
    "otp_credential_requests": {
        "name": "OTP or Credential Requests",
        "code": "TACTIC_CREDENTIAL_THEFT",
        "supported": True,
        "source": "ScamShield head2 == 'OTP / Credential Theft' OR metadata.has_otp == True",
    },
    "bank_impersonation": {
        "name": "Bank Impersonation",
        "code": "TACTIC_BANK_IMPERSONATION",
        "supported": True,
        "source": "ScamShield head1.authority_impersonation == 1 AND head2 in ['Fake KYC', 'Bank Account Freeze', 'Loan Scam']",
    },
    "government_impersonation": {
        "name": "Government Impersonation",
        "code": "TACTIC_GOV_IMPERSONATION",
        "supported": True,
        "source": "ScamShield head2 in ['Traffic e-Challan', 'Electricity Disconnection']",
    },
    "fake_employment": {
        "name": "Fake Employment",
        "code": "TACTIC_FAKE_EMPLOYMENT",
        "supported": True,
        "source": "ScamShield head2 == 'Telegram Job'",
    },
    "fake_investment": {
        "name": "Fake Investment",
        "code": "TACTIC_FAKE_INVESTMENT",
        "supported": False,
        "source": "UNAVAILABLE: Zero verified ground-truth annotations in ScamShield/Mendeley. Blocked pending human annotation.",
    },
    "prize_reward_manipulation": {
        "name": "Prize and Reward Manipulation",
        "code": "TACTIC_REWARD_BAIT",
        "supported": True,
        "source": "ScamShield head1.reward_bait == 1 OR head2 == 'Lottery / Prize'",
    },
    "account_suspension_threats": {
        "name": "Account Suspension Threats",
        "code": "TACTIC_ACCOUNT_SUSPENSION",
        "supported": True,
        "source": "ScamShield head2 == 'Bank Account Freeze' OR (head2 == 'Fake KYC' AND head1.fear == 1)",
    },
    "refund_payment_manipulation": {
        "name": "Refund and Payment Manipulation",
        "code": "TACTIC_PAYMENT_MANIPULATION",
        "supported": True,
        "source": "ScamShield head2 in ['UPI Fraud', 'Courier Scam']",
    },
}

SUPPORTED_LABELS: List[str] = [k for k, v in TACTIC_LABELS.items() if v["supported"]]
UNSUPPORTED_LABELS: List[str] = [k for k, v in TACTIC_LABELS.items() if not v["supported"]]


def map_processed_row_to_tactics(tactics_json: str, intent: str, metadata_json: str) -> Dict[str, int]:
    """Deterministically maps genuine ScamShield multi-head annotations to the 10-tactic taxonomy."""
    se = json.loads(tactics_json) if tactics_json and tactics_json != "{}" else {}
    meta = json.loads(metadata_json) if metadata_json and metadata_json != "{}" else {}

    return {
        "urgency_time_pressure": int(se.get("urgency", 0) == 1),
        "threats_intimidation": int(
            se.get("fear", 0) == 1 or intent in ["Electricity Disconnection", "Traffic e-Challan"]
        ),
        "otp_credential_requests": int(
            intent == "OTP / Credential Theft" or meta.get("has_otp", False) is True
        ),
        "bank_impersonation": int(
            se.get("authority_impersonation", 0) == 1
            and intent in ["Fake KYC", "Bank Account Freeze", "Loan Scam"]
        ),
        "government_impersonation": int(
            intent in ["Traffic e-Challan", "Electricity Disconnection"]
        ),
        "fake_employment": int(intent == "Telegram Job"),
        "fake_investment": 0,  # Explicitly unsupported
        "prize_reward_manipulation": int(
            se.get("reward_bait", 0) == 1 or intent == "Lottery / Prize"
        ),
        "account_suspension_threats": int(
            intent == "Bank Account Freeze" or (intent == "Fake KYC" and se.get("fear", 0) == 1)
        ),
        "refund_payment_manipulation": int(intent in ["UPI Fraud", "Courier Scam"]),
    }
