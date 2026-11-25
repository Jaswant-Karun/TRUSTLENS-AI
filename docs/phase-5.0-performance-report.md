# TRUSTLENS AI — PHASE 5.0: PERFORMANCE BENCHMARK REPORT

> **Measurement Script:** [`test_phase5_audit.py`](file:///c:/Users/jaswant%20karun/TRUSTLENS%20AI/test_phase5_audit.py)  
> **Environment:** Local Windows Host (`127.0.0.1:8000` FastAPI + `localhost:3000` Next.js 14 Production Build)  
> **Date:** November 25, 2026

---

## 1. Frontend SSR Load Times (17 Routes)

- **Minimum:** `5.63 ms` (`/analytics`)
- **Median (p50):** `8.33 ms`
- **Maximum:** `57.49 ms` (`/investigations/INV-2026-0011` dynamic route)
- **Status:** **PASSED**

---

## 2. Backend API Latency & Pagination

| Endpoint | p50 Latency | Max Latency | Status |
| :--- | :--- | :--- | :--- |
| `GET /api/v1/health` | `3.05 ms` | `5.38 ms` | **PASSED** |
| `GET /api/v1/threat-library?page=1&page_size=20` | `37.55 ms` | `39.01 ms` | **PASSED** |
| `GET /api/v1/analytics/overview` | `40.45 ms` | `54.33 ms` | **PASSED** |
| `GET /api/v1/investigations/INV-2026-0011/graph` | `6.29 ms` | `8.05 ms` | **PASSED** |

---

## 3. ML Inference Latency & Memory Footprint

| Metric | Measured Value | Status |
| :--- | :--- | :--- |
| **Text Classifier (`ml_service.scan_text`, n=300)** | `p50 = 104.81 ms`, `p95 = 145.83 ms` | **PASSED** |
| **URL Classifier (`ml_service.scan_url`, n=300)** | `p50 = 2.64 ms`, `p95 = 5.26 ms` | **PASSED** |
| **Python ML Process RSS Memory** | `958.96 MB` (includes SentenceTransformer + Torch weights) | **PASSED** |

---

## 4. Concurrency

- **10 Parallel `GET /api/v1/health` Requests (`ThreadPoolExecutor(max_workers=10)`):**
  - `all_200 = True` (`10/10` succeeded)
  - Total wall time: `3,063.38 ms`
  - **Status:** **PASSED**
