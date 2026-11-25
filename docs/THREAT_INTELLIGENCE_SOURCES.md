# TRUSTLENS AI — Threat Intelligence Sources & Licensing Governance

Implemented in `backend/app/services/threat_intel_service.py` and exposed via `/api/v1/threat-intel/*`.

> **Anti-Fabrication & License Policy:** Live threat intelligence is **never** fabricated on network failure or rate-limiting. Sources whose terms forbid commercial/for-profit product use are **blocked by default** (`commercial_use=False`) unless explicitly overridden for research-only evaluation.

| Source ID | Provider | Licensing | Attribution | Update Frequency | Reliability | Permitted Commercial Use |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `phishtank_online_valid` | PhishTank / Cisco Talos | PhishTank Terms of Use (Data Feeds) | PhishTank (Cisco Talos) | Hourly (`3600s`) | `high_community_verified` | **Yes** (free under Data Feeds ToU; descriptive User-Agent & rate limits required) |
| `urlhaus_recent` | abuse.ch / Spamhaus | Community Fair-Use / Spamhaus ToS | abuse.ch URLhaus | Every 5 min (`300s`) | `high_curated` | **No (Blocked)** — non-commercial/research only without Spamhaus commercial agreement |
| `openphish_community` | OpenPhish | OpenPhish Community Feed License | OpenPhish | Every 12h (`43200s`) | `high_automated_verified` | **No (Blocked)** — non-commercial/academic only; commercial use requires paid license |
| `abusech_threatfox` | abuse.ch / Spamhaus | Community Fair-Use / Spamhaus ToS | abuse.ch ThreatFox | Hourly (`3600s`) | `high_curated` | **No (Blocked)** — non-commercial/research only without Spamhaus commercial agreement |
| `cisa_kev` | U.S. CISA | CC0 1.0 Public Domain | U.S. CISA KEV Catalog | Daily (`86400s`) | `high_authoritative` | **Yes** (Public Domain, no endorsement implied) |
| `cert_advisories_cisa` | U.S. CISA (CERT) | U.S. Gov Public Domain Advisory | CISA Advisories | Every 6h (`21600s`) | `high_authoritative` | **Yes** (with attribution, no endorsement implied) |
