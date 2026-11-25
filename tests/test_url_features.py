"""
TRUSTLENS AI - Unit Tests for Safe Zero-Hop URL Parsing & Feature Extraction
Verifies deterministic feature extraction, edge cases, and zero network resolution.
"""

import unittest
from unittest.mock import patch
import socket
from ml.url_detection.features import extract_url_features, FEATURE_COLUMNS


class TestURLFeatureExtraction(unittest.TestCase):
    def test_standard_https_legitimate_url(self):
        feats = extract_url_features("https://www.onlinesbi.sbi/personal/index.html")
        self.assertEqual(feats["https_flag"], 1)
        self.assertFalse(feats["has_ip_address"])
        self.assertGreater(feats["url_length"], 20)
        self.assertEqual(feats["encoded_char_count"], 0)
        for col in FEATURE_COLUMNS:
            self.assertIn(col, feats)

    def test_ip_port_phishing_url(self):
        feats = extract_url_features("http://192.168.1.50:8080/sbi-kyc/update.php?id=123")
        self.assertEqual(feats["https_flag"], 0)
        self.assertTrue(feats["has_ip_address"])
        self.assertEqual(feats["suspicious_file_extension"], 1)
        self.assertTrue(feats["has_suspicious_keywords"])
        self.assertGreater(feats["number_of_digits"], 8)

    def test_encoded_chars_and_subdomains(self):
        feats = extract_url_features("http://login.verify-account.sbi-portal.xyz/auth%20login%3Fuser%3D1")
        self.assertEqual(feats["encoded_char_count"], 3)
        self.assertGreaterEqual(feats["subdomain_count"], 1)
        self.assertEqual(feats["has_hyphen_in_domain"], 1)
        self.assertTrue(feats["is_suspicious_tld"])
        self.assertGreater(feats["path_entropy"], 0.0)

    def test_missing_scheme_handling(self):
        feats = extract_url_features("example.com/login")
        self.assertEqual(feats["https_flag"], 0)
        self.assertEqual(feats["tld_popularity"], 1)
        self.assertEqual(feats["tld_length"], 3)

    def test_zero_network_calls_enforced(self):
        with patch.object(socket, "getaddrinfo", side_effect=AssertionError("Network DNS resolution forbidden!")):
            feats = extract_url_features("http://never-resolve-this-malicious-host.xyz/payload.exe")
            self.assertEqual(feats["suspicious_file_extension"], 1)


if __name__ == "__main__":
    unittest.main()
