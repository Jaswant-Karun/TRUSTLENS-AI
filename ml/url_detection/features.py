"""
TRUSTLENS AI - Phishing URL Feature Extractor
Extracts 17 lexical, structural, and cryptographic entropy features from URLs.
Strictly deterministic and does not make network requests to malicious targets.
"""

import math
import re
from urllib.parse import urlparse
from typing import Dict, Any


SUSPICIOUS_KEYWORDS = [
    "login", "verify", "update", "banking", "secure", "account",
    "kyc", "signin", "support", "wallet", "confirm", "service",
    "password", "auth", "billing", "free", "claim", "reward", "upi"
]

SUSPICIOUS_TLDS = {
    "xyz", "top", "work", "click", "buzz", "gq", "cf", "tk", "ml", "ga",
    "fit", "rest", "cam", "loan", "surf", "casa", "bar", "icu"
}

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "is.gd", "buff.ly",
    "ow.ly", "cutt.ly", "rb.gy", "v.gd", "tr.im"
}


def calculate_entropy(text: str) -> float:
    """Calculates Shannon entropy of a string."""
    if not text:
        return 0.0
    probabilities = [text.count(char) / len(text) for char in set(text)]
    return -sum(p * math.log2(p) for p in probabilities if p > 0)


def extract_url_features(url: str) -> Dict[str, Any]:
    """
    Extracts 17 structural and lexical features from a raw URL.
    Returns a dictionary of numerical and boolean features ready for ML inference.
    """
    clean_url = url.strip()
    if not re.match(r"^https?://", clean_url, re.IGNORECASE):
        # Prepend scheme for reliable URL parsing
        parsed = urlparse("http://" + clean_url)
    else:
        parsed = urlparse(clean_url)

    netloc = parsed.netloc.lower()
    path = parsed.path
    query = parsed.query

    # 1. Length features
    url_length = len(clean_url)
    domain_length = len(netloc)
    path_length = len(path)

    # 2. Structural counts
    count_dots = clean_url.count(".")
    count_hyphens = clean_url.count("-")
    
    # Subdomains count
    domain_parts = netloc.split(".")
    count_subdomains = max(0, len(domain_parts) - 2) if len(domain_parts) > 1 else 0

    # 3. Security flags
    # IP address in hostname (IPv4)
    has_ip = bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$", netloc))
    has_at = "@" in clean_url
    has_double_slash = "//" in path

    # Suspicious keywords
    has_suspicious_kw = any(kw in clean_url.lower() for kw in SUSPICIOUS_KEYWORDS)

    # 4. Entropy metrics
    url_entropy = round(calculate_entropy(clean_url), 4)
    domain_entropy = round(calculate_entropy(netloc), 4)

    # 5. Character ratios
    digits_count = sum(c.isdigit() for c in clean_url)
    digit_ratio = round(digits_count / max(1, url_length), 4)

    special_chars_count = len(re.findall(r"[^a-zA-Z0-9]", clean_url))
    special_char_ratio = round(special_chars_count / max(1, url_length), 4)

    # 6. TLD and Shortener analysis
    tld = domain_parts[-1] if domain_parts else ""
    is_suspicious_tld = tld in SUSPICIOUS_TLDS
    is_shortened = any(shortener in netloc for shortener in SHORTENER_DOMAINS)

    # 7. Query parameters count
    count_params = len(query.split("&")) if query else 0

    return {
        "url_length": url_length,
        "domain_length": domain_length,
        "path_length": path_length,
        "count_dots": count_dots,
        "count_hyphens": count_hyphens,
        "count_subdomains": count_subdomains,
        "has_ip_address": has_ip,
        "has_at_symbol": has_at,
        "has_double_slash": has_double_slash,
        "has_suspicious_keywords": has_suspicious_kw,
        "url_entropy": url_entropy,
        "domain_entropy": domain_entropy,
        "digit_ratio": digit_ratio,
        "special_char_ratio": special_char_ratio,
        "is_suspicious_tld": is_suspicious_tld,
        "is_shortened": is_shortened,
        "count_params": count_params,
    }
