"""
TRUSTLENS AI - Privacy-Preserving IOC Enrichment Service
Supports: domains, URLs, IP addresses, file hashes (MD5/SHA1/SHA256), phone numbers, email addresses.
Enforces:
- Deterministic normalization & deduplication
- Source provenance, confidence, timestamps, and verification status
- TTL caching, strict timeouts, and per-provider rate limits
- Privacy & consent gate: never exposes PII (phone/email/private IPs) or unconsented data externally
"""

import hashlib
import ipaddress
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, urlunparse

import httpx

from backend.app.core.logging import logger
from backend.app.database.collections import get_indicators_collection
from backend.app.database.manager import db_manager

COLL_IOC_CACHE = "ioc_enrichment_cache"

HASH_PATTERNS = {
    "md5": re.compile(r"^[a-fA-F0-9]{32}$"),
    "sha1": re.compile(r"^[a-fA-F0-9]{40}$"),
    "sha256": re.compile(r"^[a-fA-F0-9]{64}$"),
}
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
PHONE_PATTERN = re.compile(r"^\+?[0-9\-\s()]{7,18}$")
DOMAIN_PATTERN = re.compile(r"^(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}$")


class IOCEnrichmentService:
    """Normalizes, deduplicates, caches, and safely enriches IOCs."""

    CACHE_TTL_SECONDS = 3600
    EXTERNAL_TIMEOUT_SECONDS = 5.0
    PROVIDER_MAX_PER_MIN = 4

    def __init__(self):
        self._provider_timestamps: Dict[str, List[float]] = {}

    @staticmethod
    def detect_and_normalize(value: str, explicit_type: Optional[str] = None) -> Tuple[str, str, Dict[str, Any]]:
        """Detects IOC type (if not provided) and returns (ioc_type, normalized_value, metadata)."""
        raw = str(value).strip()
        if not raw:
            raise ValueError("Indicator value cannot be empty.")

        meta: Dict[str, Any] = {"is_private_pii": False, "is_private_network": False}
        t = explicit_type.lower().strip() if explicit_type else None

        # 1. File Hash
        if t == "file_hash" or any(pat.match(raw) for pat in HASH_PATTERNS.values()):
            norm = raw.lower()
            algo = next((k for k, pat in HASH_PATTERNS.items() if pat.match(norm)), "unknown")
            if algo == "unknown":
                raise ValueError(f"Unsupported file hash format: {raw}")
            meta["hash_algorithm"] = algo
            return "file_hash", norm, meta

        # 2. IP Address
        if t == "ip":
            ip_obj = ipaddress.ip_address(raw)
            meta["ip_version"] = ip_obj.version
            meta["is_private_network"] = bool(ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved)
            return "ip", str(ip_obj), meta
        try:
            ip_obj = ipaddress.ip_address(raw)
            meta["ip_version"] = ip_obj.version
            meta["is_private_network"] = bool(ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved)
            return "ip", str(ip_obj), meta
        except ValueError:
            pass

        # 3. Email Address (PII)
        if t == "email" or EMAIL_PATTERN.match(raw):
            if not EMAIL_PATTERN.match(raw):
                raise ValueError(f"Invalid email indicator: {raw}")
            local, dom = raw.rsplit("@", 1)
            norm = f"{local.lower()}@{dom.lower()}"
            meta["is_private_pii"] = True
            meta["domain_part"] = dom.lower()
            return "email", norm, meta

        # 4. URL
        if t == "url" or raw.lower().startswith(("http://", "https://")) or ("/" in raw and "." in raw.split("/")[0]):
            candidate = raw if "://" in raw else f"http://{raw}"
            parsed = urlparse(candidate)
            if not parsed.netloc:
                raise ValueError(f"Invalid URL indicator: {raw}")
            norm_url = urlunparse((
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path or "/",
                parsed.params,
                parsed.query,
                "",  # strip fragment
            ))
            meta["host"] = parsed.netloc.lower().split(":")[0]
            return "url", norm_url, meta

        # 5. Domain
        dom_cand = raw.lower().rstrip(".").split(":")[0]
        if t == "domain" or DOMAIN_PATTERN.match(dom_cand):
            if not DOMAIN_PATTERN.match(dom_cand):
                raise ValueError(f"Invalid domain indicator: {raw}")
            return "domain", dom_cand, meta

        # 6. Phone Number (PII)
        if t == "phone" or PHONE_PATTERN.match(raw):
            digits = re.sub(r"[^\d+]", "", raw)
            if len(re.sub(r"\D", "", digits)) < 7:
                raise ValueError(f"Invalid phone indicator: {raw}")
            if not digits.startswith("+") and len(digits) == 10:
                digits = "+91" + digits
            meta["is_private_pii"] = True
            return "phone", digits, meta

        raise ValueError(f"Unable to classify indicator '{raw}' into supported types.")

    def _check_provider_rate_limit(self, provider: str) -> bool:
        now = time.monotonic()
        window = [ts for ts in self._provider_timestamps.get(provider, []) if (now - ts) < 60.0]
        if len(window) >= self.PROVIDER_MAX_PER_MIN:
            self._provider_timestamps[provider] = window
            return False
        window.append(now)
        self._provider_timestamps[provider] = window
        return True

    async def _query_external_rdap(self, ioc_type: str, norm_value: str) -> Dict[str, Any]:
        """Safe external RDAP lookup (only for public domains/IPs when consented)."""
        provider = "rdap_public"
        if not self._check_provider_rate_limit(provider):
            return {"status": "rate_limited", "provider": provider}

        target_url = None
        if ioc_type == "domain":
            target_url = f"https://rdap.org/domain/{norm_value}"
        elif ioc_type == "ip":
            target_url = f"https://rdap.org/ip/{norm_value}"
        else:
            return {"status": "unsupported_for_provider", "provider": provider}

        try:
            async with httpx.AsyncClient(timeout=self.EXTERNAL_TIMEOUT_SECONDS, follow_redirects=False) as client:
                resp = await client.get(target_url, headers={"User-Agent": "TRUSTLENS-AI-Enrichment/1.0"})
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "status": "ok",
                        "provider": provider,
                        "handle": data.get("handle"),
                        "ldhName": data.get("ldhName"),
                    }
                return {"status": f"http_{resp.status_code}", "provider": provider}
        except httpx.TimeoutException:
            return {"status": "timeout", "provider": provider}
        except Exception as exc:
            logger.warning(f"External RDAP enrichment error for {ioc_type}: {exc}")
            return {"status": "error", "provider": provider, "error": str(exc)}

    async def enrich_indicator(
        self,
        value: str,
        indicator_type: Optional[str] = None,
        allow_external: bool = False,
        external_consent: bool = False,
    ) -> Dict[str, Any]:
        """Normalizes, checks cache & local threat_indicators, and safely enriches if consented."""
        ioc_type, norm_value, meta = self.detect_and_normalize(value, indicator_type)
        dedup_key = hashlib.sha256(f"{ioc_type}:{norm_value}".encode("utf-8")).hexdigest()
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()

        cache_coll = db_manager.get_collection(COLL_IOC_CACHE)
        cached = await cache_coll.find_one({"dedup_key": dedup_key})
        if cached:
            cached.pop("_id", None)
            exp_str = cached.get("cache_expires_at_utc")
            if exp_str and datetime.fromisoformat(exp_str) > now_dt:
                # Respect privacy: if cached had no external call and external is now requested, continue only if needed
                cached["cache_hit"] = True
                return cached

        # 1. Local MongoDB threat_indicators lookup
        ind_coll = get_indicators_collection()
        search_vals = [norm_value]
        if ioc_type == "url" and meta.get("host"):
            search_vals.append(meta["host"])
        local_matches = await ind_coll.find({"value": {"$in": search_vals}}, {"_id": 0}).limit(10).to_list(length=10)

        provenance: List[Dict[str, Any]] = []
        max_conf = 0.0
        verification_status = "no_local_match"

        for m in local_matches:
            sev = str(m.get("severity", "medium")).lower()
            conf = 0.95 if sev == "critical" else (0.85 if sev == "high" else 0.65)
            max_conf = max(max_conf, conf)
            verification_status = m.get("verification_status", "verified")
            provenance.append({
                "source": m.get("source", "threat_indicators"),
                "source_id": m.get("source_id", "local"),
                "reliability": m.get("reliability", "verified"),
                "observed_at_utc": m.get("ingested_at_utc") or m.get("created_at") or now_iso,
            })

        # 2. Safe External Enrichment (strict consent + privacy gate)
        external_result: Dict[str, Any]
        if not allow_external or not external_consent:
            external_result = {"status": "skipped_no_consent"}
        elif meta.get("is_private_pii") or meta.get("is_private_network"):
            external_result = {"status": "skipped_privacy_policy", "reason": "PII and private-network IOCs are never sent externally."}
        else:
            external_result = await self._query_external_rdap(ioc_type, norm_value)
            if external_result.get("status") == "ok":
                provenance.append({
                    "source": "RDAP Public Registry",
                    "source_id": "rdap_public",
                    "reliability": "authoritative_registry",
                    "observed_at_utc": now_iso,
                })

        record = {
            "indicator_id": f"ioc-{dedup_key[:12]}",
            "dedup_key": dedup_key,
            "indicator_type": ioc_type,
            "normalized_value": norm_value if not meta.get("is_private_pii") else f"sha256:{dedup_key[:16]}",
            "is_private_pii": bool(meta.get("is_private_pii")),
            "metadata": meta,
            "confidence": round(max_conf, 4),
            "verification_status": verification_status,
            "source_provenance": provenance,
            "external_enrichment": external_result,
            "first_seen_utc": now_iso,
            "last_enriched_utc": now_iso,
            "cache_expires_at_utc": (now_dt + timedelta(seconds=self.CACHE_TTL_SECONDS)).isoformat(),
            "cache_hit": False,
        }

        if cached:
            await cache_coll.update_one({"dedup_key": dedup_key}, {"$set": record})
        else:
            await cache_coll.insert_one(dict(record))

        return record

    async def enrich_batch(
        self,
        indicators: List[Dict[str, Optional[str]]],
        allow_external: bool = False,
        external_consent: bool = False,
    ) -> Dict[str, Any]:
        """Normalizes, deduplicates, and enriches a batch of indicators."""
        seen_keys: set = set()
        results: List[Dict[str, Any]] = []
        duplicates_skipped = 0

        for item in indicators:
            val = item.get("value") or ""
            itype = item.get("indicator_type")
            norm_type, norm_val, _ = self.detect_and_normalize(val, itype)
            dkey = hashlib.sha256(f"{norm_type}:{norm_val}".encode("utf-8")).hexdigest()
            if dkey in seen_keys:
                duplicates_skipped += 1
                continue
            seen_keys.add(dkey)
            results.append(
                await self.enrich_indicator(
                    val,
                    indicator_type=norm_type,
                    allow_external=allow_external,
                    external_consent=external_consent,
                )
            )

        return {
            "submitted_count": len(indicators),
            "unique_enriched_count": len(results),
            "duplicates_deduplicated": duplicates_skipped,
            "results": results,
        }


ioc_enrichment_service = IOCEnrichmentService()
