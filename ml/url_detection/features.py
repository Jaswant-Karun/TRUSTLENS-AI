"""
TRUSTLENS AI - Production Phishing URL Feature Extractor
Extracts 16 structural, lexical, and cryptographic entropy indicators from raw URLs
matching the schema of the LegitPhish benchmark dataset.
Strictly deterministic and does not make network requests to malicious targets.
"""

import math
import re
from urllib.parse import urlparse
from typing import Dict, Any, List

POPULAR_TLDS = {"com", "org", "net", "edu", "gov", "mil", "in", "io", "ai", "co"}

SUSPICIOUS_EXTENSIONS = {
    ".exe", ".zip", ".rar", ".apk", ".bin", ".iso", ".scr", ".bat",
    ".cmd", ".php", ".sh", ".vbs", ".hta", ".jar", ".msi"
}


def calculate_entropy(text: str) -> float:
    """Calculates Shannon entropy of a string."""
    if not text:
        return 0.0
    probabilities = [text.count(char) / len(text) for char in set(text)]
    return -sum(p * math.log2(p) for p in probabilities if p > 0)


FEATURE_COLUMNS = [
    "url_length",
    "has_ip_address",
    "dot_count",
    "https_flag",
    "url_entropy",
    "token_count",
    "subdomain_count",
    "query_param_count",
    "tld_length",
    "path_length",
    "has_hyphen_in_domain",
    "number_of_digits",
    "tld_popularity",
    "suspicious_file_extension",
    "domain_name_length",
    "percentage_numeric_chars",
]


def extract_url_features(raw_url: str) -> Dict[str, Any]:
    """
    Parses a raw URL string and extracts all 16 numerical and structural indicators.
    Guarantees no outbound network connections.
    """
    clean_url = str(raw_url).strip()

    # Prepend scheme for reliable parsing if omitted
    if not re.match(r"^https?://", clean_url, re.IGNORECASE):
        parsed = urlparse("http://" + clean_url)
        https_flag = 0
    else:
        parsed = urlparse(clean_url)
        https_flag = 1 if parsed.scheme.lower() == "https" else 0

    netloc = parsed.netloc.lower()
    path = parsed.path
    query = parsed.query

    # Basic length features
    url_length = len(clean_url)
    domain_name_length = len(netloc)
    path_length = len(path)

    # Subdomain & TLD decomposition
    domain_clean = netloc.split(":")[0]  # strip port if present
    parts = domain_clean.split(".")
    subdomain_count = max(0, len(parts) - 2) if len(parts) > 1 else 0
    tld = parts[-1] if len(parts) > 1 else ""
    tld_length = len(tld)
    tld_popularity = 1 if tld in POPULAR_TLDS else 0

    # Counts
    dot_count = clean_url.count(".")
    has_hyphen_in_domain = 1 if "-" in domain_clean else 0
    query_param_count = len(query.split("&")) if query else 0

    # Digits and numeric character percentage
    digits_total = sum(c.isdigit() for c in clean_url)
    percentage_numeric_chars = round(digits_total / max(1, url_length), 4)

    # IP address in hostname (IPv4)
    has_ip = 1 if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$", netloc) else 0

    # Lexical tokens count
    tokens = re.split(r"[\W_]+", clean_url)
    token_count = len([t for t in tokens if t])

    # Entropy
    url_entropy = round(calculate_entropy(clean_url), 4)

    # Suspicious file extension
    suspicious_file_extension = 1 if any(path.lower().endswith(ext) for ext in SUSPICIOUS_EXTENSIONS) else 0

    return {
        "url_length": url_length,
        "has_ip_address": has_ip,
        "dot_count": dot_count,
        "https_flag": https_flag,
        "url_entropy": url_entropy,
        "token_count": token_count,
        "subdomain_count": subdomain_count,
        "query_param_count": query_param_count,
        "tld_length": tld_length,
        "path_length": path_length,
        "has_hyphen_in_domain": has_hyphen_in_domain,
        "number_of_digits": digits_total,
        "tld_popularity": tld_popularity,
        "suspicious_file_extension": suspicious_file_extension,
        "domain_name_length": domain_name_length,
        "percentage_numeric_chars": percentage_numeric_chars,
    }
