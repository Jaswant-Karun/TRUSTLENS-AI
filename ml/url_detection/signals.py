"""
TRUSTLENS AI - Offline Zero-Hop URL Security Signals
Evaluates brand impersonation, homograph/IDN Punycode, typosquatting (edit distance),
open-redirect query parameters, threat-feed correlation (offline cache), and
verified official-domain false-positive calibration.
Guarantees ZERO outbound network requests.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from urllib.parse import urlparse, parse_qs

# Protected brands -> set of official registrable domains
PROTECTED_BRAND_DOMAINS: Dict[str, Set[str]] = {
    "sbi": {"onlinesbi.sbi", "sbi.co.in", "sbi.co", "bank.sbi"},
    "onlinesbi": {"onlinesbi.sbi", "sbi.co.in"},
    "hdfc": {"hdfcbank.com", "hdfc.com"},
    "icici": {"icicibank.com"},
    "axis": {"axisbank.com"},
    "paytm": {"paytm.com", "paytmbank.com"},
    "phonepe": {"phonepe.com"},
    "paypal": {"paypal.com"},
    "google": {"google.com", "google.co.in", "accounts.google.com"},
    "microsoft": {"microsoft.com", "live.com", "office.com", "microsoftonline.com"},
    "apple": {"apple.com", "icloud.com"},
    "amazon": {"amazon.com", "amazon.in", "aws.amazon.com"},
    "uidai": {"uidai.gov.in"},
    "npci": {"npci.org.in"},
    "incometax": {"incometax.gov.in"},
}

VERIFIED_OFFICIAL_DOMAINS: Set[str] = set().union(*PROTECTED_BRAND_DOMAINS.values()) | {
    "github.com",
    "python.org",
    "stackoverflow.com",
    "wikipedia.org",
    "mozilla.org",
    "cloudflare.com",
    "icann.org",
}

REDIRECT_PARAM_KEYS = {"redirect", "redirect_uri", "redirect_url", "next", "url", "return", "return_url", "goto", "dest", "target", "continue"}


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i]
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost))
        prev = curr
    return prev[-1]


def _registrable_domain(host: str) -> str:
    parts = [p for p in host.lower().split(".") if p]
    if len(parts) <= 2:
        return ".".join(parts)
    # Handle common two-label ccTLDs like .co.in, .gov.in, .org.in, .co.uk
    if parts[-2] in {"co", "gov", "org", "ac", "net", "edu"} and len(parts[-1]) == 2 and len(parts) >= 3:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def _is_official_match(host: str, official_set: Set[str]) -> bool:
    reg = _registrable_domain(host)
    if reg in official_set or host in official_set:
        return True
    return any(host.endswith("." + off) for off in official_set)


def check_offline_threat_feed(raw_url: str, host: str) -> Optional[str]:
    """Checks local offline threat feed parquet caches under data/external/ without network calls."""
    ext_dir = Path("data/external")
    if not ext_dir.exists():
        return None
    try:
        import pandas as pd
        for pq in ext_dir.glob("*.parquet"):
            df = pd.read_parquet(pq)
            if "sanitized_content" in df.columns:
                vals = set(df["sanitized_content"].astype(str).str.lower())
                if raw_url.strip().lower() in vals:
                    return pq.stem
    except Exception:
        pass
    return None


def evaluate_url_security_signals(raw_url: str, features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produces deterministic zero-hop intelligence for brand impersonation, homographs,
    typosquatting, redirect parameters, DNS/cert/domain-age policy, threat feeds, and FP guarding.
    """
    clean_url = str(raw_url).strip()
    parsed = urlparse(clean_url if "://" in clean_url else "http://" + clean_url)
    host = parsed.netloc.lower().split(":")[0]
    reg_domain = _registrable_domain(host)
    sld = reg_domain.split(".")[0] if reg_domain else ""

    # 1. Homograph / IDN Punycode / Non-ASCII Unicode check
    has_punycode = any(lbl.startswith("xn--") for lbl in host.split("."))
    has_non_ascii_host = any(ord(ch) > 127 for ch in host)
    homograph_detected = bool(has_punycode or has_non_ascii_host)

    # 2. Brand impersonation & typosquatting check (inspect host and path, not query search terms)
    impersonated_brands: List[str] = []
    typosquat_targets: List[Tuple[str, int]] = []
    host_and_path = f"{host}{parsed.path.lower()}"
    for brand, official_domains in PROTECTED_BRAND_DOMAINS.items():
        if _is_official_match(host, official_domains):
            continue
        if len(brand) >= 4 and brand in host:
            impersonated_brands.append(brand)
        elif len(brand) >= 3 and re.search(rf"\b{re.escape(brand)}\b", re.sub(r"[-_./]", " ", host_and_path)):
            impersonated_brands.append(brand)
        elif len(brand) >= 5 and sld and not _is_official_match(host, official_domains):
            dist = _levenshtein(sld, brand)
            if 1 <= dist <= 2:
                typosquat_targets.append((brand, dist))

    # 3. Redirect parameter inspection (isolated/offline lexical check)
    qs = parse_qs(parsed.query)
    open_redirect_params = []
    for k, vals in qs.items():
        if k.lower() in REDIRECT_PARAM_KEYS:
            if any("http://" in v.lower() or "https://" in v.lower() or "//" in v for v in vals):
                open_redirect_params.append(k)
    open_redirect_detected = bool(open_redirect_params or features.get("has_double_slash"))

    # 4. Offline threat-feed correlation
    feed_match = check_offline_threat_feed(clean_url, host)

    # 5. Verified official domain false-positive guard
    is_official = _is_official_match(host, VERIFIED_OFFICIAL_DOMAINS)
    fp_guard_eligible = bool(
        is_official
        and features.get("https_flag", 0) == 1
        and not features.get("has_at_symbol", False)
        and not open_redirect_detected
        and not homograph_detected
        and not impersonated_brands
        and not typosquat_targets
        and features.get("suspicious_file_extension", 0) == 0
        and feed_match is None
    )

    return {
        "host": host,
        "registrable_domain": reg_domain,
        "brand_impersonation": {
            "detected": bool(impersonated_brands),
            "brands": sorted(set(impersonated_brands)),
        },
        "homograph_and_typosquatting": {
            "homograph_detected": homograph_detected,
            "has_punycode": has_punycode,
            "has_non_ascii_host": has_non_ascii_host,
            "typosquatting_detected": bool(typosquat_targets),
            "typosquat_matches": [{"brand": b, "edit_distance": d} for b, d in typosquat_targets],
        },
        "redirect_behavior": {
            "open_redirect_param_detected": open_redirect_detected,
            "suspicious_params": open_redirect_params,
            "live_redirect_followed": False,
            "analysis_environment": "zero_hop_offline_only",
        },
        "domain_age": {
            "status": "unavailable_zero_hop_offline",
            "days": None,
            "policy": "Live WHOIS/RDAP disabled in zero-hop production mode to avoid target signaling.",
        },
        "dns_certificate_evidence": {
            "https_scheme_present": bool(features.get("https_flag", 0) == 1),
            "live_dns_resolved": False,
            "live_tls_inspected": False,
            "policy": "zero_hop_offline_only",
        },
        "threat_feed_correlation": {
            "matched": feed_match is not None,
            "feed_source": feed_match,
        },
        "fp_guard_eligible": fp_guard_eligible,
    }
