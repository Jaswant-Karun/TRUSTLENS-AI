"""
TRUSTLENS AI - Phishing URL Preprocessor & Feature Extractor
Extracts lexical, structural, and cryptographic entropy indicators from URLs
deterministically without initiating network connections to target endpoints.
"""

import math
import re
from urllib.parse import urlparse
from typing import Dict, Any


SUSPICIOUS_KEYWORDS = [
    "login", "verify", "update", "banking", "secure", "account",
    "kyc", "signin", "support", "wallet", "confirm", "service",
    "password", "auth", "billing", "free", "claim", "reward", "upi",
    "netbanking", "card", "debit", "credit", "alert", "security"
]

SUSPICIOUS_TLDS = {
    "xyz", "top", "work", "click", "buzz", "gq", "cf", "tk", "ml", "ga",
    "fit", "rest", "cam", "loan", "surf", "casa", "bar", "icu", "club",
    "vip", "online", "site", "live", "link"
}

POPULAR_TLDS = {"com", "org", "net", "edu", "gov", "mil", "in", "io", "ai", "co"}

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "is.gd", "buff.ly",
    "ow.ly", "cutt.ly", "rb.gy", "v.gd", "tr.im", "tiny.cc"
}


class URLPreprocessor:
    """Extracts rich feature representations from URLs for machine learning."""

    @staticmethod
    def calculate_entropy(text: str) -> float:
        """Calculates Shannon entropy of a string."""
        if not text:
            return 0.0
        probabilities = [text.count(char) / len(text) for char in set(text)]
        return -sum(p * math.log2(p) for p in probabilities if p > 0)

    def extract_features(self, raw_url: str) -> Dict[str, Any]:
        """
        Parses raw URL and computes comprehensive structural and lexical indicators.
        """
        clean_url = str(raw_url).strip()
        
        # Prepend scheme if missing for standardized parsing
        if not re.match(r"^https?://", clean_url, re.IGNORECASE):
            parsed = urlparse("http://" + clean_url)
            scheme = "unspecified"
        else:
            parsed = urlparse(clean_url)
            scheme = parsed.scheme.lower()

        netloc = parsed.netloc.lower()
        path = parsed.path
        query = parsed.query

        # Basic lengths
        url_length = len(clean_url)
        domain_length = len(netloc)
        path_length = len(path)
        query_length = len(query)

        # Hostname and subdomain decomposition
        domain_parts = netloc.split(":")[0].split(".")
        subdomain_count = max(0, len(domain_parts) - 2) if len(domain_parts) > 1 else 0
        tld = domain_parts[-1] if len(domain_parts) > 1 else ""
        tld_length = len(tld)

        # Special character counts
        dot_count = clean_url.count(".")
        hyphen_count = clean_url.count("-")
        underscore_count = clean_url.count("_")
        slash_count = clean_url.count("/")
        question_count = clean_url.count("?")
        equal_count = clean_url.count("=")
        at_count = clean_url.count("@")
        special_chars_total = len(re.findall(r"[^a-zA-Z0-9]", clean_url))

        # Entropy calculations
        url_entropy = round(self.calculate_entropy(clean_url), 4)
        domain_entropy = round(self.calculate_entropy(netloc), 4)

        # Digit and symbol ratios
        digits_total = sum(c.isdigit() for c in clean_url)
        digit_ratio = round(digits_total / max(1, url_length), 4)
        special_char_ratio = round(special_chars_total / max(1, url_length), 4)

        # Structural & Security Flags
        has_ip = bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$", netloc))
        has_at_symbol = at_count > 0
        has_double_slash_path = "//" in path
        https_flag = 1 if scheme == "https" else 0
        is_shortened = any(shortener in netloc for shortener in SHORTENER_DOMAINS)
        is_suspicious_tld = 1 if tld in SUSPICIOUS_TLDS else 0
        tld_popularity = 1 if tld in POPULAR_TLDS else 0
        has_hyphen_in_domain = 1 if "-" in netloc else 0

        # Sensitive Keyword Detection
        found_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in clean_url.lower()]
        keyword_count = len(found_keywords)
        has_sensitive_keywords = 1 if keyword_count > 0 else 0

        # Query parameters count
        query_param_count = len(query.split("&")) if query else 0

        return {
            "url": clean_url,
            "url_length": url_length,
            "domain_length": domain_length,
            "path_length": path_length,
            "query_length": query_length,
            "subdomain_count": subdomain_count,
            "tld": tld,
            "tld_length": tld_length,
            "dot_count": dot_count,
            "hyphen_count": hyphen_count,
            "special_chars_total": special_chars_total,
            "url_entropy": url_entropy,
            "domain_entropy": domain_entropy,
            "digit_ratio": digit_ratio,
            "special_char_ratio": special_char_ratio,
            "number_of_digits": digits_total,
            "has_ip_address": 1 if has_ip else 0,
            "has_at_symbol": 1 if has_at_symbol else 0,
            "has_double_slash_path": 1 if has_double_slash_path else 0,
            "https_flag": https_flag,
            "is_shortened": 1 if is_shortened else 0,
            "is_suspicious_tld": is_suspicious_tld,
            "tld_popularity": tld_popularity,
            "has_hyphen_in_domain": has_hyphen_in_domain,
            "has_sensitive_keywords": has_sensitive_keywords,
            "keyword_count": keyword_count,
            "query_param_count": query_param_count,
        }


url_preprocessor = URLPreprocessor()

