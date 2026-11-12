"""
TRUSTLENS AI - Model 3: Social Engineering & Scam Tactic Taxonomy
Defines the 10 target manipulation tactics, mapping rules, and dataset annotation policies.
"""

from typing import Dict, Any, List

# Target 10 Social Engineering Manipulation Tactics
TACTIC_REGISTRY: Dict[str, Dict[str, Any]] = {
    "urgency_time_pressure": {
        "id": "urgency_time_pressure",
        "name": "Urgency and Time Pressure",
        "code": "TACTIC_URGENCY",
        "description": "Imposes artificial deadlines or countdowns to panic victims into hasty compliance without verification.",
        "supported": True,
        "mapping_source": "ScamShield Head 1: urgency == 1",
        "threat_level": "high",
    },
    "threats_intimidation": {
        "id": "threats_intimidation",
        "name": "Threats and Intimidation",
        "code": "TACTIC_INTIMIDATION",
        "description": "Coerces victims using legal threats, police action, service cutoffs, or physical/financial harm.",
        "supported": True,
        "mapping_source": "ScamShield Head 1: fear == 1 OR Head 2 in ['Electricity Disconnection', 'Traffic e-Challan']",
        "threat_level": "critical",
    },
    "otp_credential_requests": {
        "id": "otp_credential_requests",
        "name": "OTP and Credential Requests",
        "code": "TACTIC_CREDENTIAL_THEFT",
        "description": "Directly solicits one-time passwords (OTPs), PINs, passwords, or authentication tokens.",
        "supported": True,
        "mapping_source": "ScamShield Head 2: 'OTP / Credential Theft' OR metadata: has_otp == True",
        "threat_level": "critical",
    },
    "financial_manipulation": {
        "id": "financial_manipulation",
        "name": "Financial Manipulation",
        "code": "TACTIC_FINANCIAL_PRESSURE",
        "description": "Manipulates victims regarding unauthorized debits, transaction disputes, penalty fees, or loan disbursements.",
        "supported": True,
        "mapping_source": "ScamShield Head 1: financial_pressure == 1 OR Head 2: 'Loan Scam'",
        "threat_level": "high",
    },
    "authority_impersonation": {
        "id": "authority_impersonation",
        "name": "Bank or Government Impersonation",
        "code": "TACTIC_AUTHORITY_IMPERSONATION",
        "description": "Falsely impersonates trusted financial institutions (SBI, HDFC), regulatory agencies, police, or government departments.",
        "supported": True,
        "mapping_source": "ScamShield Head 1: authority_impersonation == 1 OR Head 2 in ['Traffic e-Challan', 'Fake KYC']",
        "threat_level": "high",
    },
    "fake_employment": {
        "id": "fake_employment",
        "name": "Fake Employment Opportunities",
        "code": "TACTIC_FAKE_EMPLOYMENT",
        "description": "Lures victims with fraudulent work-from-home, part-time rating, YouTube video liking, or Telegram task jobs.",
        "supported": True,
        "mapping_source": "ScamShield Head 2: 'Telegram Job'",
        "threat_level": "medium",
    },
    "fake_investment": {
        "id": "fake_investment",
        "name": "Fake Investment Opportunities",
        "code": "TACTIC_FAKE_INVESTMENT",
        "description": "Promises unrealistic or guaranteed returns on cryptocurrency, forex, or stock market trading schemes.",
        "supported": False,
        "mapping_source": "UNAVAILABLE: No verified ground-truth training annotations exist in benchmark dataset. Model not fabricated.",
        "threat_level": "high",
    },
    "account_suspension": {
        "id": "account_suspension",
        "name": "Account Suspension Threats",
        "code": "TACTIC_ACCOUNT_SUSPENSION",
        "description": "Falsely claims that bank accounts, debit cards, PAN linkages, or SIM cards have been suspended or frozen.",
        "supported": True,
        "mapping_source": "ScamShield Head 2: 'Bank Account Freeze' OR ('Fake KYC' AND Head 1 fear == 1)",
        "threat_level": "high",
    },
    "prize_reward_scams": {
        "id": "prize_reward_scams",
        "name": "Prize and Reward Scams",
        "code": "TACTIC_REWARD_BAIT",
        "description": "Baits victims with unsolicited lottery winnings, cash rewards, free gifts, or prize giveaways.",
        "supported": True,
        "mapping_source": "ScamShield Head 1: reward_bait == 1 OR Head 2: 'Lottery / Prize'",
        "threat_level": "medium",
    },
    "refund_payment_manipulation": {
        "id": "refund_payment_manipulation",
        "name": "Refund and Payment Manipulation",
        "code": "TACTIC_PAYMENT_MANIPULATION",
        "description": "Exploits UPI Collect requests, fake refund processing, or parcel re-delivery payment fees to siphon funds.",
        "supported": True,
        "mapping_source": "ScamShield Head 2 in ['UPI Fraud', 'Courier Scam']",
        "threat_level": "high",
    },
}

# Supported trainable tactics (9 labels with genuine ground truth annotations)
SUPPORTED_TACTIC_KEYS: List[str] = [k for k, v in TACTIC_REGISTRY.items() if v["supported"]]

# All 10 labels for full taxonomy reporting
ALL_TACTIC_KEYS: List[str] = list(TACTIC_REGISTRY.keys())


def map_scamshield_annotations(item: Dict[str, Any]) -> Dict[str, int]:
    """
    Deterministically maps raw ScamShield multi-head annotations and metadata
    to the 10 target social engineering tactics.
    """
    se = item.get("head1_social_engineering", {})
    intent = item.get("head2_scam_intent", "")
    meta = item.get("metadata", {})

    return {
        "urgency_time_pressure": int(se.get("urgency", 0) == 1),
        "threats_intimidation": int(
            se.get("fear", 0) == 1 or intent in ["Electricity Disconnection", "Traffic e-Challan"]
        ),
        "otp_credential_requests": int(
            intent == "OTP / Credential Theft" or meta.get("has_otp", False) is True
        ),
        "financial_manipulation": int(
            se.get("financial_pressure", 0) == 1 or intent == "Loan Scam"
        ),
        "authority_impersonation": int(
            se.get("authority_impersonation", 0) == 1 or intent in ["Traffic e-Challan", "Fake KYC"]
        ),
        "fake_employment": int(intent == "Telegram Job"),
        "fake_investment": 0,  # Explicitly unavailable: zero verified ground-truth labels
        "account_suspension": int(
            intent == "Bank Account Freeze" or (intent == "Fake KYC" and se.get("fear", 0) == 1)
        ),
        "prize_reward_scams": int(
            se.get("reward_bait", 0) == 1 or intent == "Lottery / Prize"
        ),
        "refund_payment_manipulation": int(
            intent in ["UPI Fraud", "Courier Scam"]
        ),
    }
