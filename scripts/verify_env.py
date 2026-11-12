"""
TRUSTLENS AI - System & Environment Verification Script
Validates directory integrity, Python runtimes, ML module loading, and API endpoints.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def verify():
    print("=" * 60)
    print("TRUSTLENS AI - ENVIRONMENT & ARCHITECTURE VERIFICATION")
    print("=" * 60)

    # 1. Directory Tree Check
    required_dirs = [
        "frontend",
        "backend/app/api/v1/routers",
        "backend/app/core",
        "backend/app/models",
        "backend/app/services",
        "ml/datasets",
        "ml/preprocessing",
        "ml/text_detection",
        "ml/url_detection",
        "ml/tactic_detection",
        "ml/campaign_detection",
        "ml/training",
        "ml/evaluation",
        "ml/explainability",
        "ml/artifacts",
        "ml/notebooks",
        "data/raw/scamshield",
        "data/raw/sms_phishing",
        "data/raw/legitphish",
        "data/processed",
        "data/external",
        "n8n/workflows",
        "n8n/documentation",
        "docs",
        "scripts",
        "tests",
    ]

    missing_dirs = [d for d in required_dirs if not Path(d).exists()]
    if missing_dirs:
        print(f"[FAIL] Missing directories: {missing_dirs}")
        return False
    print(f"[OK] All {len(required_dirs)} required project directories exist.")

    # 2. ML Engine Imports & Deterministic Validation
    try:
        from ml.url_detection.features import extract_url_features
        feats = extract_url_features("http://192.168.1.1/sbi-kyc/update.php?id=123")
        assert len(feats) == 17, f"Expected 17 features, got {len(feats)}"
        assert feats["has_ip_address"] is True
        print(f"[OK] Engine 2 (Phishing URL 17-feature extractor) functional.")

        from ml.text_detection.classifier import MultilingualScamClassifier
        txt_clf = MultilingualScamClassifier()
        lang = txt_clf.detect_language("Aapka SBI khata turant band ho jayega")
        assert "Hinglish" in lang
        print(f"[OK] Engine 1 (Multilingual Script Identifier) functional [{lang}].")

        from ml.tactic_detection.detector import ScamTacticDetector
        tac_det = ScamTacticDetector()
        tacs = tac_det.detect("URGENT: Submit OTP immediately to prevent account suspension")
        assert tacs["tactic_count"] >= 1
        print(f"[OK] Engine 3 (Scam Tactic Multi-Label Detector) functional.")

        from ml.campaign_detection.clusterer import CampaignClusterer
        clusterer = CampaignClusterer()
        clusters = clusterer.cluster_messages([
            "Payment request for Rs 5000 via UPI id admin@okhdfcbank",
            "Urgent deposit required to UPI handle admin@okhdfcbank"
        ])
        assert clusters["clusters_identified"] >= 1
        print(f"[OK] Engine 4 (Campaign Clustering & IOC Discovery) functional.")

    except Exception as exc:
        print(f"[FAIL] ML Module verification error: {exc}")
        return False

    # 3. FastAPI App Import Check
    try:
        from backend.app.main import app
        from backend.app.core.config import settings
        print(f"[OK] FastAPI application loaded: '{settings.APP_NAME}' v{settings.APP_VERSION}")
    except Exception as exc:
        print(f"[FAIL] Backend app loading error: {exc}")
        return False

    print("=" * 60)
    print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)
