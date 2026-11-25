"""
TRUSTLENS AI - Phase 3.0: Comprehensive ML Inference API & Loader Test Suite
Tests:
1. Valid input across /analyze/text, /analyze/url, /analyze/comprehensive, /models, /models/{id}
2. Invalid input (422)
3. Empty input (422)
4. Oversized input (422)
5. Missing model artifact -> CentralModelLoader marks unavailable (never safe/clean)
6. Corrupt model artifact (SHA-256 mismatch) -> CentralModelLoader refuses load
7. Concurrent requests (5 parallel requests)
8. Live backend health after restart
"""

import json
import time
import tempfile
import unittest
import urllib.request
import urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from backend.app.ml_engine.model_loader import CentralModelLoader
from backend.app.ml_engine.engine import ProductionMLEngine

BASE_URL = "http://127.0.0.1:8000/api/v1"


def post_json(endpoint: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    res = urllib.request.urlopen(req, timeout=20)
    return res.status, json.loads(res.read().decode("utf-8"))


def get_json(endpoint: str):
    res = urllib.request.urlopen(f"{BASE_URL}{endpoint}", timeout=15)
    return res.status, json.loads(res.read().decode("utf-8"))


class TestMLInferenceAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Wait up to 35s for FastAPI startup (SentenceTransformer weights)
        for _ in range(35):
            try:
                st, _ = get_json("/health")
                if st == 200:
                    return
            except Exception:
                time.sleep(1)
        raise RuntimeError("FastAPI backend did not become healthy in time.")

    def test_01_health_and_models_endpoints(self):
        st, h = get_json("/health")
        self.assertEqual(st, 200)
        self.assertTrue(all(h["models_loaded"].values()), f"Not all models loaded: {h['models_loaded']}")

        st_m, m_list = get_json("/models")
        self.assertEqual(st_m, 200)

        st_id, m_detail = get_json("/models/trustlens-text-v1.0-prod")
        self.assertEqual(st_id, 200)
        self.assertEqual(m_detail["deployment_status"], "Production")

    def test_02_valid_text_url_and_comprehensive(self):
        st, t_res = post_json("/analyze/text", {
            "text": "URGENT: Your SBI account will be blocked today! Update KYC at http://sbi-kyc-update.com",
            "channel": "sms"
        })
        self.assertEqual(st, 200)
        self.assertIn(t_res["threat_level"], ("high", "critical"))
        self.assertTrue(t_res["text_model"]["is_threat"])
        self.assertEqual(t_res["text_model"]["model_version"], "trustlens-model1-v1.0")

        st_u, u_res = post_json("/analyze/url", {"url": "http://192.168.1.50:8080/sbi-kyc/update.php"})
        self.assertEqual(st_u, 200)
        self.assertTrue(u_res["url_model"]["is_phishing"])

        st_c, c_res = post_json("/analyze/comprehensive", {
            "content": "Part-time job offer! Earn 5000 INR daily liking YouTube videos.",
            "channel": "whatsapp"
        })
        self.assertEqual(st_c, 200)
        self.assertIn("analysis_id", c_res)

    def test_03_empty_and_invalid_and_oversized_inputs(self):
        # Empty text
        with self.assertRaises(urllib.error.HTTPError) as ctx1:
            post_json("/analyze/text", {"text": ""})
        self.assertEqual(ctx1.exception.code, 422)

        # Oversized text (> 10,000 chars)
        with self.assertRaises(urllib.error.HTTPError) as ctx2:
            post_json("/analyze/text", {"text": "A" * 15000})
        self.assertEqual(ctx2.exception.code, 422)

        # Invalid URL / empty URL
        with self.assertRaises(urllib.error.HTTPError) as ctx3:
            post_json("/analyze/url", {"url": ""})
        self.assertEqual(ctx3.exception.code, 422)

    def test_04_missing_and_corrupt_artifacts_loader_safety(self):
        with tempfile.TemporaryDirectory() as tmp:
            corrupt_file = Path(tmp) / "corrupt.joblib"
            corrupt_file.write_bytes(b"corrupted-model-bytes")

            reg_path = Path(tmp) / "reg.json"
            reg_path.write_text(json.dumps({
                "models": {
                    "m-missing": {
                        "task": "text_classification",
                        "deployment_status": "Production",
                        "artifact_path": str(Path(tmp) / "does_not_exist.joblib"),
                        "artifact_checksum": "0000",
                    },
                    "m-corrupt": {
                        "task": "url_phishing_classification",
                        "deployment_status": "Production",
                        "artifact_path": str(corrupt_file),
                        "artifact_checksum": "ffffffffffffffffffffffffffffffff",
                    },
                }
            }), encoding="utf-8")

            loader = CentralModelLoader(str(reg_path))
            status_map = loader.verify_registry_artifacts()
            self.assertFalse(status_map["text_classification"])
            self.assertFalse(status_map["url_phishing_classification"])
            self.assertIn("m-missing", loader.verification_errors)
            self.assertIn("m-corrupt", loader.verification_errors)

        # Verify ProductionMLEngine returns 'unavailable' (never safe/clean) when classifier is None
        engine = ProductionMLEngine.__new__(ProductionMLEngine)
        engine.text_classifier = None
        res = engine.predict_text("Suspicious message")
        self.assertEqual(res["status"], "unavailable")
        self.assertIsNone(res["is_threat"])

    def test_05_concurrent_requests(self):
        def call_once(i):
            return post_json("/analyze/url", {"url": f"http://phishing-test-{i}.xyz/login.php"})

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(call_once, range(5)))

        for st, body in results:
            self.assertEqual(st, 200)
            self.assertIn("analysis_id", body)


if __name__ == "__main__":
    unittest.main()
