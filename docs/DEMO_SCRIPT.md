# TRUSTLENS AI — 3-MINUTE LIVE DEMONSTRATION SCRIPT

> **Target Environment:** `http://localhost:3000` (Next.js Production) + `http://127.0.0.1:8000` (FastAPI)  
> **Rule:** Only demonstrate live, verified features; state limitations honestly.

---

### **0:00–0:20 — The Digital Fraud Problem**
- **Visual:** Open `/dashboard` or `/investigations`.
- **Narration:** "Digital fraud in India and globally increasingly combines multilingual SMS/WhatsApp lures with short-lived lookalike URLs. Static blocklists miss new domains, and opaque 'scam scores' give SOC analysts zero evidence to act on. TRUSTLENS AI connects multilingual ML, zero-hop URL forensics, and an evidence-backed investigation graph."

### **0:20–0:45 — Submit a Suspicious Message**
- **Visual:** Navigate to `/analyze/text`. Paste a realistic KYC smishing lure (e.g., *"URGENT: Your SBI KYC is suspended today. Update immediately at http://sbi-kyc-update.com or account will be blocked."*). Click **Analyze**.
- **Narration:** "We submit an untrusted message. Behind the Next.js proxy, FastAPI runs our SHA-256 verified Feature Union + Calibrated LinearSVC text classifier without touching any external links."

### **0:45–1:10 — Show Text Model Prediction & Provenance**
- **Visual:** Point to `AnalysisResultPanel` showing `threat_level`, calibrated `risk_score`, `model_version` (`trustlens-model1-v1.0`), and the distinct provenance badges (**ML Model**, **Threat Intel**, **Human Review**).
- **Narration:** "Notice we never fabricate default confidence values and we explicitly separate automated ML inference from threat-intel matches and human-reviewed evidence."

### **1:10–1:30 — Analyze a Suspicious URL (Zero-Hop)**
- **Visual:** Navigate to `/analyze/url` and submit `http://sbi-kyc-update.com/login.php`.
- **Narration:** "Our XGBoost URL engine extracts 16 lexical features offline—zero-hop, never visiting the target—and returns SHAP feature attributions explaining why the path length and domain tokens flagged high risk."

### **1:30–1:50 — Social-Engineering Tactic Detection**
- **Visual:** Show detected tactics from the scan or open `/intelligence/tactics`.
- **Narration:** "Model 3 classifies messages across 9 verified social-engineering tactics like urgency, bank impersonation, and account suspension threats—while transparently omitting unsupported categories like fake investment where verified ground-truth data was absent."

### **1:50–2:20 — Investigation Graph & 1-Hop Expansion**
- **Visual:** Open `/investigations/INV-2026-0011`. Click a node to open the Object Inspector (`EvidencePanel.tsx`), inspect its source provenance, and switch to the synchronized Timeline.
- **Narration:** "Here in the ThreatQ-inspired investigation workspace, analysts inspect connected messages, URLs, domains, and IPs, expand 1-hop relationships from MongoDB, and export validated STIX 2.1 bundles from `/reports`."

### **2:20–2:40 — Campaign Similarity & Model Evaluation**
- **Visual:** Briefly show `/intelligence/campaigns` (47 HDBSCAN clusters) and `/models` (held-out benchmarks) or `/analytics` (live DB counts).
- **Narration:** "Unsupervised HDBSCAN clustering groups 47 recurring campaign patterns, while `/analytics` and `/models` report only real database counts and held-out test metrics."

### **2:40–3:00 — Impact, Limitations & Next Steps**
- **Narration:** "TRUSTLENS AI gives analysts auditable, zero-hop fraud triage. We are transparent about current limits—such as 54.5% recall on Devanagari Hindi and a 15.3% false-positive rate on complex benign URLs—and our roadmap focuses on expanding regional language data, upgrading Next.js dependencies, and deploying the prepared Render/Vercel manifests."
