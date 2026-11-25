"""
TRUSTLENS AI - Phase 3.1: Unified Fraud Risk & Evidence Engine Test Suite
Tests all 6 required scenarios:
1. All models available (CRITICAL & LOW)
2. One model unavailable -> INCONCLUSIVE
3. Conflicting model predictions
4. Missing threat-intelligence data (unknown URL never labeled safe)
5. Unverified community report (does not inflate score)
6. Inconclusive assessment
"""

import unittest
from ml.risk_engine.aggregator import UnifiedRiskEngine


class TestUnifiedRiskEngine(unittest.TestCase):
    def setUp(self):
        self.engine = UnifiedRiskEngine()

    def test_01_all_models_available_critical_scam(self):
        res = self.engine.assess(
            text_result={"is_threat": True, "confidence": 0.94, "model_version": "trustlens-model1-v1.0", "detected_language": "English"},
            url_result={"is_phishing": True, "risk_score": 0.99, "model_version": "trustlens-model2-xgboost-v1.0"},
            tactic_result={"tactics": [{"tactic_name": "Urgency"}, {"tactic_name": "Bank Impersonation"}], "model_version": "v1.0"},
            campaign_result={"matched": True, "campaign_id": 11, "similarity_score": 0.88},
            input_type="text",
        )
        self.assertEqual(res["risk_status"], "CRITICAL")
        self.assertGreaterEqual(res["aggregated_risk_score"], 0.85)
        self.assertFalse(res["is_safety_guarantee"])
        self.assertEqual(res["evidence_count"], 4)

    def test_02_primary_model_unavailable_returns_inconclusive(self):
        res = self.engine.assess(
            text_result={"status": "unavailable", "is_threat": None, "error": "Checksum mismatch"},
            tactic_result={"status": "unavailable", "tactics": []},
            input_type="text",
        )
        self.assertEqual(res["risk_status"], "INCONCLUSIVE")
        self.assertIsNone(res["aggregated_risk_score"])
        self.assertIn("Primary model unavailable", res["conflicts_detected"])

    def test_03_conflicting_predictions_url_vs_text_and_tactic_conflict(self):
        # Case A: Text says benign, embedded URL says phishing -> HIGH/CRITICAL + conflict flagged
        res_a = self.engine.assess(
            text_result={"is_threat": False, "confidence": 0.90, "model_version": "v1.0"},
            url_result={"is_phishing": True, "risk_score": 0.92, "model_version": "v1.0"},
            input_type="text",
        )
        self.assertEqual(res_a["risk_status"], "CRITICAL")
        self.assertTrue(len(res_a["conflicts_detected"]) > 0)

        # Case B: Borderline text (0.24) + 2 coercion tactics -> INCONCLUSIVE
        res_b = self.engine.assess(
            text_result={"is_threat": False, "confidence": 0.76, "model_version": "v1.0"},
            tactic_result={"tactics": [{"tactic_name": "Urgency"}, {"tactic_name": "Fear"}], "model_version": "v1.0"},
            input_type="text",
        )
        self.assertEqual(res_b["risk_status"], "INCONCLUSIVE")

    def test_04_missing_threat_intel_never_guarantees_safe(self):
        res = self.engine.assess(
            url_result={"is_phishing": False, "risk_score": 0.05, "model_version": "v1.0"},
            threat_intel_match={"matched": False, "feed_name": "URLhaus"},
            input_type="url",
        )
        self.assertEqual(res["risk_status"], "LOW")
        self.assertFalse(res["is_safety_guarantee"])
        self.assertIn("not a guarantee of safety", res["rationale"].lower())
        ti_ev = [e for e in res["evidence_records"] if e["source"] == "URLhaus"][0]
        self.assertEqual(ti_ev["prediction"], "no_match_found")

    def test_05_unverified_community_report_does_not_inflate_score(self):
        res = self.engine.assess(
            text_result={"is_threat": False, "confidence": 0.95, "model_version": "v1.0"},
            community_report={"report_id": "rep-123", "review_status": "unverified"},
            input_type="text",
        )
        self.assertEqual(res["risk_status"], "LOW")
        self.assertLess(res["aggregated_risk_score"], 0.20)
        rep_ev = [e for e in res["evidence_records"] if "rep-123" in e["source"]][0]
        self.assertEqual(rep_ev["verification_state"], "unverified")

    def test_06_human_benign_vs_high_ml_returns_inconclusive(self):
        res = self.engine.assess(
            text_result={"is_threat": True, "confidence": 0.92, "model_version": "v1.0"},
            community_report={"report_id": "rep-456", "review_status": "benign"},
            input_type="text",
        )
        self.assertEqual(res["risk_status"], "INCONCLUSIVE")
        self.assertTrue(len(res["conflicts_detected"]) > 0)


if __name__ == "__main__":
    unittest.main()
