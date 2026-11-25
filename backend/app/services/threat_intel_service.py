"""
TRUSTLENS AI - Real Threat Intelligence Ingestion Architecture
Documents and ingests verified threat intelligence feeds (PhishTank, URLhaus, OpenPhish,
abuse.ch ThreatFox, CISA KEV, CERT advisories) with:
- Explicit licensing, attribution, update frequency, reliability, and commercial-use gating
- Normalized IOC/advisory schema persisted to MongoDB `threat_indicators`
- Scheduled background polling & structured error handling
- Strict anti-fabrication rule: never fabricates live threat intelligence on feed failure
"""

import asyncio
import csv
import io
import os
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

import httpx

from backend.app.core.logging import logger
from backend.app.database.collections import get_indicators_collection
from backend.app.database.manager import db_manager

COLL_THREAT_INTEL_RUNS = "threat_intel_runs"

THREAT_INTEL_SOURCES: Dict[str, Dict[str, Any]] = {
    "phishtank_online_valid": {
        "source_id": "phishtank_online_valid",
        "name": "PhishTank Verified Online Phishing Feed",
        "provider": "PhishTank / Cisco Talos",
        "feed_url": "https://data.phishtank.com/data/online-valid.json",
        "format": "json",
        "licensing": "PhishTank Terms of Use (Data Feeds) — https://phishtank.org/terms.php",
        "attribution": "PhishTank (Cisco Talos)",
        "update_frequency": "Hourly (3600s)",
        "update_interval_seconds": 3600,
        "reliability": "high_community_verified",
        "permitted_commercial_use": {
            "allowed": True,
            "terms": "Commercial use of Data feeds permitted free of charge under PhishTank Terms of Use (AS-IS, descriptive User-Agent and rate-limit compliance required).",
        },
    },
    "urlhaus_recent": {
        "source_id": "urlhaus_recent",
        "name": "abuse.ch URLhaus Recent Malware URLs",
        "provider": "abuse.ch / Spamhaus Technology",
        "feed_url": "https://urlhaus.abuse.ch/downloads/csv_recent/",
        "format": "csv",
        "licensing": "abuse.ch Community Fair-Use / Spamhaus Terms of Service — https://urlhaus.abuse.ch/api/",
        "attribution": "abuse.ch URLhaus",
        "update_frequency": "Every 5 minutes (300s)",
        "update_interval_seconds": 300,
        "reliability": "high_curated",
        "permitted_commercial_use": {
            "allowed": False,
            "terms": "BLOCKED FOR COMMERCIAL USE: Free community feed is restricted to non-commercial/research/internal defense; commercial product use requires Spamhaus commercial API agreement.",
        },
    },
    "openphish_community": {
        "source_id": "openphish_community",
        "name": "OpenPhish Community Phishing Feed",
        "provider": "OpenPhish",
        "feed_url": "https://openphish.com/feed.txt",
        "format": "txt",
        "licensing": "OpenPhish Community Feed License (Non-Commercial) — https://openphish.com/phishing_feeds.html",
        "attribution": "OpenPhish",
        "update_frequency": "Every 12 hours (43200s)",
        "update_interval_seconds": 43200,
        "reliability": "high_automated_verified",
        "permitted_commercial_use": {
            "allowed": False,
            "terms": "BLOCKED FOR COMMERCIAL USE: Community feed is strictly non-commercial/academic; commercial use requires a paid OpenPhish Premium/Enterprise license.",
        },
    },
    "abusech_threatfox": {
        "source_id": "abusech_threatfox",
        "name": "abuse.ch ThreatFox Recent IOCs",
        "provider": "abuse.ch / Spamhaus Technology",
        "feed_url": "https://threatfox.abuse.ch/export/json/recent/",
        "format": "json",
        "licensing": "abuse.ch Community Fair-Use / Spamhaus Terms of Service — https://threatfox.abuse.ch/api/",
        "attribution": "abuse.ch ThreatFox",
        "update_frequency": "Hourly (3600s)",
        "update_interval_seconds": 3600,
        "reliability": "high_curated",
        "permitted_commercial_use": {
            "allowed": False,
            "terms": "BLOCKED FOR COMMERCIAL USE: Free community feed is non-commercial/research only; commercial integration requires Spamhaus commercial licensing.",
        },
    },
    "cisa_kev": {
        "source_id": "cisa_kev",
        "name": "CISA Known Exploited Vulnerabilities (KEV) Catalog",
        "provider": "U.S. Cybersecurity and Infrastructure Security Agency (CISA)",
        "feed_url": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
        "format": "json",
        "licensing": "CC0 1.0 Universal Public Domain Dedication — https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "U.S. CISA Known Exploited Vulnerabilities Catalog (no endorsement implied)",
        "update_frequency": "Daily (86400s)",
        "update_interval_seconds": 86400,
        "reliability": "high_authoritative",
        "permitted_commercial_use": {
            "allowed": True,
            "terms": "Public Domain (CC0 1.0); commercial use permitted without restriction without implying CISA/DHS endorsement.",
        },
    },
    "cert_advisories_cisa": {
        "source_id": "cert_advisories_cisa",
        "name": "CISA / US-CERT Cybersecurity Advisories RSS",
        "provider": "U.S. CISA (CERT Coordination)",
        "feed_url": "https://www.cisa.gov/cybersecurity-advisories/all.xml",
        "format": "rss",
        "licensing": "U.S. Government Public Domain Advisory Feed — https://www.cisa.gov/about/policies",
        "attribution": "CISA Cybersecurity Advisories",
        "update_frequency": "Every 6 hours (21600s)",
        "update_interval_seconds": 21600,
        "reliability": "high_authoritative",
        "permitted_commercial_use": {
            "allowed": True,
            "terms": "Permitted for defensive awareness and commercial correlation with attribution; no official endorsement implied.",
        },
    },
}


class ThreatIntelIngestionService:
    """Ingests, normalizes, and schedules real threat intelligence feeds with license gating."""

    def __init__(self):
        self._scheduler_task: Optional[asyncio.Task] = None
        self._last_run_by_source: Dict[str, float] = {}

    def list_sources(self, commercial_only: Optional[bool] = None) -> List[Dict[str, Any]]:
        sources = list(THREAT_INTEL_SOURCES.values())
        if commercial_only is True:
            sources = [s for s in sources if s["permitted_commercial_use"]["allowed"]]
        elif commercial_only is False:
            sources = [s for s in sources if not s["permitted_commercial_use"]["allowed"]]
        return sources

    def check_commercial_gate(self, source_id: str, allow_non_commercial: bool = False) -> Dict[str, Any]:
        if source_id not in THREAT_INTEL_SOURCES:
            raise KeyError(f"Unknown threat intel source '{source_id}'")
        spec = THREAT_INTEL_SOURCES[source_id]
        if not spec["permitted_commercial_use"]["allowed"] and not allow_non_commercial:
            raise PermissionError(
                f"Source '{source_id}' blocked by commercial license gate: {spec['permitted_commercial_use']['terms']}"
            )
        return spec

    def normalize_payload(self, source_id: str, raw_body: str, max_items: int = 500) -> List[Dict[str, Any]]:
        """Normalizes raw JSON/CSV/TXT/RSS feed payloads into unified threat_indicators documents."""
        spec = THREAT_INTEL_SOURCES[source_id]
        now_utc = datetime.now(timezone.utc).isoformat()
        normalized: List[Dict[str, Any]] = []

        def _base_record(val: str, itype: str, threat_type: str, severity: str, summary: str, updated: Optional[str] = None) -> Dict[str, Any]:
            return {
                "indicator_id": f"ti-{source_id}-{uuid.uuid5(uuid.NAMESPACE_URL, f'{source_id}:{val}').hex[:12]}",
                "value": val.strip(),
                "indicator_type": itype,
                "threat_type": threat_type,
                "severity": severity,
                "summary": summary[:300],
                "source": spec["attribution"],
                "source_id": source_id,
                "license": spec["licensing"],
                "reliability": spec["reliability"],
                "commercial_permitted": bool(spec["permitted_commercial_use"]["allowed"]),
                "provenance": "threat_intel",
                "verification_status": "verified",
                "source_updated_at": updated or now_utc,
                "ingested_at_utc": now_utc,
            }

        if source_id == "phishtank_online_valid":
            import json
            rows = json.loads(raw_body)
            for item in rows[:max_items]:
                u = str(item.get("url", "")).strip()
                if not u:
                    continue
                target = item.get("target") or "Unknown"
                normalized.append(
                    _base_record(u, "url", "phishing", "high", f"PhishTank verified phishing targeting {target}", item.get("verification_time"))
                )
        elif source_id == "openphish_community":
            for line in raw_body.splitlines()[:max_items]:
                u = line.strip()
                if u.startswith(("http://", "https://")):
                    normalized.append(_base_record(u, "url", "phishing", "high", "OpenPhish community phishing URL"))
        elif source_id == "urlhaus_recent":
            lines = [ln for ln in raw_body.splitlines() if ln.strip() and not ln.startswith("#")]
            reader = csv.reader(io.StringIO("\n".join(lines)))
            for row in reader:
                if len(row) >= 6:
                    u = row[2].strip()
                    threat = row[5].strip() or "malware_download"
                    if u.startswith(("http://", "https://")):
                        normalized.append(_base_record(u, "url", threat, "critical", f"URLhaus {threat}", row[1].strip()))
                if len(normalized) >= max_items:
                    break
        elif source_id == "cisa_kev":
            import json
            data = json.loads(raw_body)
            for v in data.get("vulnerabilities", [])[:max_items]:
                cve = str(v.get("cveID", "")).strip()
                if not cve:
                    continue
                sev = "critical" if v.get("knownRansomwareCampaignUse") == "Known" else "high"
                summary = f"{v.get('vendorProject', '')} {v.get('product', '')}: {v.get('vulnerabilityName', '')}".strip()
                normalized.append(_base_record(cve, "cve", "exploited_vulnerability", sev, summary, v.get("dateAdded")))
        elif source_id == "cert_advisories_cisa":
            root = ET.fromstring(raw_body)
            for item in root.findall(".//item")[:max_items]:
                link = (item.findtext("link") or "").strip()
                title = (item.findtext("title") or "Cybersecurity Advisory").strip()
                pub = (item.findtext("pubDate") or "").strip()
                if link:
                    normalized.append(_base_record(link, "advisory", "security_advisory", "medium", title, pub))
        elif source_id == "abusech_threatfox":
            import json
            data = json.loads(raw_body)
            items = data.values() if isinstance(data, dict) else data
            for entry in list(items)[:max_items]:
                rec = entry[0] if isinstance(entry, list) and entry else entry
                if isinstance(rec, dict) and rec.get("ioc_value"):
                    normalized.append(
                        _base_record(
                            str(rec["ioc_value"]),
                            str(rec.get("ioc_type", "indicator")),
                            str(rec.get("threat_type", "malware")),
                            "high",
                            f"ThreatFox: {rec.get('malware_printable', 'Unknown')}",
                            rec.get("first_seen_utc"),
                        )
                    )

        return normalized

    async def ingest_source(
        self,
        source_id: str,
        allow_non_commercial: bool = False,
        max_items: int = 250,
    ) -> Dict[str, Any]:
        """Fetches, normalizes, and upserts a live feed. Never fabricates data on failure."""
        spec = self.check_commercial_gate(source_id, allow_non_commercial=allow_non_commercial)
        run_id = f"tirun-{uuid.uuid4().hex[:10]}"
        started = datetime.now(timezone.utc).isoformat()
        headers = {"User-Agent": os.getenv("TRUSTLENS_TI_UA", "TRUSTLENS-AI-ThreatIntel/1.0")}
        url = spec["feed_url"]
        if source_id == "phishtank_online_valid" and os.getenv("PHISHTANK_APP_KEY"):
            url = f"https://data.phishtank.com/data/{os.getenv('PHISHTANK_APP_KEY')}/online-valid.json"

        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                raw_body = resp.text

            records = self.normalize_payload(source_id, raw_body, max_items=max_items)
            ind_coll = get_indicators_collection()
            upserted = 0
            for rec in records:
                existing = await ind_coll.find_one({"indicator_id": rec["indicator_id"]})
                if existing:
                    await ind_coll.update_one({"indicator_id": rec["indicator_id"]}, {"$set": rec})
                else:
                    await ind_coll.insert_one(dict(rec))
                upserted += 1

            run_doc = {
                "run_id": run_id,
                "source_id": source_id,
                "status": "success",
                "records_normalized": len(records),
                "records_persisted": upserted,
                "started_at_utc": started,
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                "error": None,
            }
        except Exception as exc:
            logger.error(f"Threat intel ingestion failed for {source_id}: {exc}")
            run_doc = {
                "run_id": run_id,
                "source_id": source_id,
                "status": "error",
                "records_normalized": 0,
                "records_persisted": 0,
                "started_at_utc": started,
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                "error": str(exc),
            }

        runs_coll = db_manager.get_collection(COLL_THREAT_INTEL_RUNS)
        await runs_coll.insert_one(dict(run_doc))
        return run_doc

    async def get_status(self, limit: int = 20) -> Dict[str, Any]:
        runs_coll = db_manager.get_collection(COLL_THREAT_INTEL_RUNS)
        ind_coll = get_indicators_collection()
        recent_runs = await runs_coll.find({}, {"_id": 0}).sort("started_at_utc", -1).limit(limit).to_list(length=limit)
        total_indicators = await ind_coll.count_documents({"provenance": "threat_intel"})
        return {
            "total_threat_intel_indicators": total_indicators,
            "recent_runs": recent_runs,
            "scheduler_running": bool(self._scheduler_task and not self._scheduler_task.done()),
        }

    async def run_scheduled_cycle(self, allow_non_commercial: bool = False) -> List[Dict[str, Any]]:
        """Runs due feeds based on their configured update_interval_seconds."""
        import time
        now_mono = time.monotonic()
        results: List[Dict[str, Any]] = []
        for sid, spec in THREAT_INTEL_SOURCES.items():
            if not spec["permitted_commercial_use"]["allowed"] and not allow_non_commercial:
                continue
            last = self._last_run_by_source.get(sid, 0.0)
            if (now_mono - last) >= spec["update_interval_seconds"] or last == 0.0:
                res = await self.ingest_source(sid, allow_non_commercial=allow_non_commercial)
                self._last_run_by_source[sid] = now_mono
                results.append(res)
        return results


threat_intel_service = ThreatIntelIngestionService()
