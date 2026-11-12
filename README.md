# TRUSTLENS AI — Advanced Multilingual Digital Fraud Intelligence & Prevention Platform

> **"Detect the deception before people lose their money."**

TRUSTLENS AI is an enterprise-grade cybersecurity and fraud intelligence platform designed to identify, dissect, and attribute malicious digital communications across languages (English, Hindi, Hinglish), URLs, and screenshots.

---

## 🛡️ Core Capabilities

- **Multilingual Scam Classification:** Detects smishing, phishing, spam, and legitimate communications across English, Hindi, and code-mixed Hinglish using calibrated statistical baselines and compact multilingual transformers.
- **Phishing URL Detection Engine:** Analyzes 17 structural, lexical, and cryptographic entropy indicators with XGBoost & Random Forest, explainable via SHAP feature attribution.
- **Scam Tactic Multi-Label Identification:** Pinpoints social engineering vectors: artificial urgency, credential harvesting, fake job offers, and financial manipulation.
- **Scam Campaign & IOC Intelligence Graph:** Uses semantic sentence embeddings and density-based clustering (HDBSCAN) to link isolated incidents into coordinated campaigns.
- **Optical Evidence Ingestion:** Extracts text from fraudulent screenshots and payment receipts via OCR.
- **Enterprise SOC Dashboard:** Dark-mode tactical UI featuring live kill-chain graphs, telemetry logs, and explainability cards.

---

## 📁 Repository Structure

```
TRUSTLENS AI/
├── data/
│   ├── raw/                  # Immutable source datasets
│   │   ├── scamshield/       # Multilingual social engineering corpus
│   │   ├── sms_phishing/     # Labelled smishing & spam dataset
│   │   └── legitphish/       # 101k labelled phishing and legitimate URLs
│   ├── processed/            # Cleaned, deduplicated, reproducible parquet splits
│   ├── external/             # Cached threat intelligence feeds (URLhaus, etc.)
│   └── README.md
├── ml/
│   ├── text_detection/       # Multilingual scam message models (TF-IDF, LinearSVC, MuRIL)
│   ├── url_detection/        # 17-feature extractor & XGBoost/Random Forest models
│   ├── tactic_detection/     # Multi-label social engineering tactic classifiers
│   ├── campaign_detection/   # SentenceTransformers + HDBSCAN clustering engine
│   ├── evaluation/           # Calibration, PR-AUC, Confusion Matrix, and metrics
│   └── artifacts/            # Serialized models (.joblib, .onnx)
├── backend/
│   ├── app/
│   │   ├── api/v1/           # FastAPI routers (scan, url, tactics, campaigns, ocr)
│   │   ├── core/             # Configuration, database connection, security
│   │   ├── models/           # Pydantic schemas & MongoDB document models
│   │   ├── services/         # ML inference orchestrators & threat extractors
│   │   └── utils/            # Helper utilities and text normalizers
│   └── tests/                # Unit and integration test suite
├── frontend/                 # Next.js 14/15, Tailwind CSS, Framer Motion SOC UI
├── n8n/
│   └── workflows/            # Automation templates for incident alerts and threat sync
└── docs/                     # Architectural specs, API documentation & research notes
```

---

## ⚡ Quick Start

### 1. Environment Setup (Python 3.12)
```bash
# Virtual environment with uv (recommended) or py -3.12
uv venv --python 3.12 .venv
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Run the FastAPI Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 3. Run the Next.js Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 📄 License
MIT License. Built for rigorous fraud intelligence and research.
