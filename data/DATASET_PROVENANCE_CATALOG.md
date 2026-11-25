# TRUSTLENS AI — Real-World Dataset Provenance & Licensing Catalog

All datasets in TRUSTLENS AI are governed by `ml/data_pipeline/registry.py` and `ml/data_pipeline/acquisition.py`, which enforce **commercial-use license gating**, **SHA-256 provenance tracking**, **PII masking**, **Zip Slip protection**, and **cross-dataset deduplication**.

> **Governance Rule:** Public availability does **not** imply commercial reuse permission. Non-commercial feeds (such as `urlhaus_community`) are explicitly blocked from commercial training ingestion unless `allow_non_commercial=True` is set for research-only storage under `data/external/`.

---

## Dataset Inventory (8-Point Provenance)

### 1. ScamShield (`scamshield`)
1. **Source:** Hugging Face (`sidzzz07/scamshield-dataset`) — `https://huggingface.co/datasets/sidzzz07/scamshield-dataset`
2. **License:** MIT License (`https://opensource.org/licenses/MIT`)
3. **Collection Date:** 2024–2025 (Dataset v1.0.0; acquired 2026-11-12)
4. **Language:** English, Hindi, Hinglish
5. **Label Definitions:** `is_scam` (`0` = Legitimate/Benign, `1` = Fraud/Smishing/Scam/Spam); `head1_social_engineering` (multi-label psychological cues); `head2_scam_intent` (fine-grained intent)
6. **Number of Records:** `85,680` (`69,286` train / `8,192` val / `8,202` test)
7. **Known Limitations:** Language imbalance (~89% English, ~7.4% Hindi, ~3.5% Hinglish); 0 Tamil/Bengali samples; `fake_investment` tactic has 0 verified annotations; 978 near-duplicate template groups.
8. **Permitted Commercial Usage:** **Yes** — Permitted under MIT License with copyright and permission notice preservation.

### 2. SMS Phishing Dataset (`sms_phishing`)
1. **Source:** Mendeley Data (`10.17632/f45bkkt8pr.1`, Sandhya Mishra & Devpriya Soni)
2. **License:** CC BY 4.0 (`https://creativecommons.org/licenses/by/4.0/`)
3. **Collection Date:** 2022 (Version 1; acquired 2026-11-12)
4. **Language:** English
5. **Label Definitions:** `ham` (legitimate SMS, 4,844), `Spam`/`spam` (unsolicited commercial SMS, 489), `Smishing`/`smishing` (SMS phishing lure, 638)
6. **Number of Records:** `5,971` raw (`215` novel after deduplication against ScamShield)
7. **Known Limitations:** `5,756` of `5,971` rows (`96.4%`) overlap with ScamShield; inconsistent label casing; English-only.
8. **Permitted Commercial Usage:** **Yes** — Permitted under CC BY 4.0 with author attribution and indication of changes.

### 3. LegitPhish (`legitphish`)
1. **Source:** Mendeley Data (`10.17632/hx4m73v2sf.2`, Rachana Potpelwar, Uday Kulkarni, Jaishri Waghmare)
2. **License:** CC BY 4.0 (`https://creativecommons.org/licenses/by/4.0/`)
3. **Collection Date:** 2024 (Version 2; acquired 2026-11-12)
4. **Language:** URL-Agnostic (Lexical/Structural)
5. **Label Definitions:** `0` = Phishing URL (`63,678`), `1` = Legitimate URL (`37,540`), empty = malformed (`1` dropped)
6. **Number of Records:** `101,219` raw (`100,872` clean across `63,962` unique domain groups)
7. **Known Limitations:** Domain repetition requires `StratifiedGroupKFold` (`domain_group_id`) to prevent leakage; 62.94% phishing imbalance; lexical features only; near-zero `has_ip_address` positives.
8. **Permitted Commercial Usage:** **Yes** — Permitted under CC BY 4.0 with author attribution.

### 4. UCI SMS Spam Collection (`uci_sms_spam`)
1. **Source:** UCI Machine Learning Repository (`id=228`, Tiago A. Almeida & Jose Maria Gomez Hidalgo) — `https://archive.ics.uci.edu/dataset/228/sms+spam+collection`
2. **License:** CC BY 4.0 (`https://creativecommons.org/licenses/by/4.0/`)
3. **Collection Date:** 2012-06-22 (UCI publication; 2011 SMS corpus)
4. **Language:** English
5. **Label Definitions:** `ham` = Legitimate SMS (`4,827`), `spam` = Unsolicited commercial/fraudulent SMS (`747`)
6. **Number of Records:** `5,574`
7. **Known Limitations:** Historical 2011 UK/Singapore SMS corpus predating UPI/KYC/WhatsApp scams; 13.4% spam imbalance; partial overlap with Mendeley/ScamShield corpora.
8. **Permitted Commercial Usage:** **Yes** — Permitted under CC BY 4.0 with attribution.

### 5. PhishTank Verified Online Phishing Feed (`phishtank_feed`)
1. **Source:** PhishTank / Cisco Talos (`https://phishtank.org/developer_info.php`)
2. **License:** PhishTank Terms of Use (Data Feeds) (`https://phishtank.org/terms.php`)
3. **Collection Date:** Rolling live feed (snapshot timestamped at ingestion)
4. **Language:** URL-Agnostic (Global)
5. **Label Definitions:** `verified=yes, online=yes` = Community-verified active phishing URL at snapshot time
6. **Number of Records:** Dynamic rolling feed (~10,000–50,000 active verified URLs per snapshot)
7. **Known Limitations:** Positive-only class (requires paired legitimate URLs); strict HTTP 509 rate limits without registered `PHISHTANK_APP_KEY` and descriptive `User-Agent`; provided AS-IS without warranty.
8. **Permitted Commercial Usage:** **Yes** — PhishTank Terms of Use permit commercial use of Data feeds free of charge, subject to rate limits and `User-Agent` compliance.

### 6. abuse.ch URLhaus Malicious URL Feed (`urlhaus_community`)
1. **Source:** abuse.ch / Spamhaus Technology (`https://urlhaus.abuse.ch/api/`)
2. **License:** abuse.ch Community Fair-Use / Spamhaus Terms of Service
3. **Collection Date:** Rolling live feed (30-day window)
4. **Language:** URL-Agnostic (Global)
5. **Label Definitions:** `url_status` (`online`/`offline` malware distribution URL), `threat` (e.g., `malware_download`)
6. **Number of Records:** Dynamic rolling feed
7. **Known Limitations:** Malware distribution URLs rather than credential phishing; community feed is non-commercial/research-only.
8. **Permitted Commercial Usage:** **No (Blocked by default)** — Commercial/for-profit product use requires a paid abuse.ch/Spamhaus commercial API agreement.

### 7. CISA Known Exploited Vulnerabilities Catalog (`cisa_kev`)
1. **Source:** U.S. Cybersecurity and Infrastructure Security Agency (`https://www.cisa.gov/known-exploited-vulnerabilities-catalog`)
2. **License:** CC0 1.0 Universal Public Domain Dedication (`https://creativecommons.org/publicdomain/zero/1.0/`)
3. **Collection Date:** Rolling government catalog (snapshot timestamped at ingestion)
4. **Language:** English
5. **Label Definitions:** `cveID` (confirmed actively exploited CVE), `knownRansomwareCampaignUse` (`Known` / `Unknown`)
6. **Number of Records:** Dynamic authoritative catalog (~1,200+ CVEs)
7. **Known Limitations:** Vulnerability intelligence rather than SMS/URL phishing text; third-party links retain their own terms; no DHS/CISA endorsement implied.
8. **Permitted Commercial Usage:** **Yes** — Public Domain (CC0 1.0), commercial use permitted without restriction.
