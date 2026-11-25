# ADR-001: TRUSTLENS AI Android Application Architecture

- **Status:** Proposed (Decision Documented Prior to Implementation)
- **Date:** 2026-11-25
- **Scope:** Android mobile client for TRUSTLENS AI (Web + FastAPI backend unchanged)

---

## 1. Context & Current Codebase Assessment

An inspection of the existing TRUSTLENS AI codebase establishes the following architectural baseline:

### 1.1 Existing Frontend (`frontend/`)
- **Stack:** Next.js `^14.2.15` (App Router), React `^18.3.1`, TypeScript `^5.6.3`, Tailwind CSS `^3.4.14`, Framer Motion `^11.11.9`, Lucide React `^0.453.0` (`frontend/package.json`).
- **Build & Routing Configuration (`frontend/next.config.mjs`):**
  - Currently configured with `output: "standalone"` and Next.js `rewrites()` proxying `/api/v1/:path*` to `BACKEND_API_URL` (`http://127.0.0.1:8000`).
  - Contains 17+ routes (including `/dashboard`, `/analyze/text`, `/analyze/url`, `/analyze/image`, `/investigations`, `/investigations/[id]`, `/intelligence/*`, `/threat-library`, `/reports`, `/analytics`, `/models`, `/methodology`, `/settings`, `/profile`, `/history`, `/login`, `/register`) plus `frontend/app/manifest.ts` (PWA manifest).
- **API & Auth Layer (`frontend/lib/api.ts`):**
  - Centralized typed HTTP client `apiFetch<T>()` targeting `API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1"`.
  - Bearer JWT tokens are currently stored in browser `localStorage` (`trustlens_token`) via `getStoredToken()`, `setStoredToken()`, and `clearStoredToken()`.
- **Media & File Handling (`frontend/app/analyze/image/page.tsx`):**
  - Uses `<input type="file">` with client-side 10 MB limit, MIME filtering (`image/jpeg`, `image/png`, `image/webp`), and magic-byte header inspection (`hasValidImageSignature`) before calling `scanImage()` (`POST /api/v1/analyze/image`).

### 1.2 Existing Backend (`backend/`)
- **Stack:** FastAPI + MongoDB Atlas (`backend/app/main.py`, `backend/app/config/settings.py`).
- **Security & Middleware:**
  - HS256 JWT authentication (`ACCESS_TOKEN_EXPIRE_MINUTES = 1440`).
  - `CORSMiddleware` configured via `ALLOWED_ORIGINS` (`http://localhost:3000,http://127.0.0.1:3000,https://trustlens.vercel.app`).
  - `SecurityHeadersMiddleware` (`backend/app/middleware/security_headers.py`) enforcing `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`, and `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'` on non-docs API responses.
  - `RateLimitMiddleware` and `RequestLoggingMiddleware`.
- **Notifications (`backend/app/services/notification_service.py`):**
  - `NotificationService` already implements consent-aware, asynchronous notification queuing (`in_app_notifications`, `email_notifications`, `threat_alerts_opt_in`), but does not yet manage mobile device push tokens or Firebase Cloud Messaging (FCM) delivery.

---

## 2. Options Compared

| Criterion | Capacitor (Android + Next.js) | React Native (Expo / Bare) | Native Android (Kotlin + Jetpack Compose) |
| :--- | :--- | :--- | :--- |
| **Code & Logic Reuse** | **~90–95%** — Reuses `frontend/lib/api.ts`, all 17+ routes, state, and UI components without rewriting the web app. | **~15–25%** — Reuses TypeScript DTOs and `apiFetch` logic only; all DOM/Tailwind/Framer UI must be rewritten in RN primitives. | **0%** — Complete rewrite of UI, state, models, and networking in Kotlin. |
| **Security** | **Strong with hardening** — Must bridge token storage from `localStorage` to Android Keystore (`EncryptedSharedPreferences`), enforce TLS + Network Security Config, and add `https://localhost` / `capacitor://localhost` to CORS. | **Strong** — Uses `expo-secure-store` / Keystore natively; no WebView DOM surface. | **Best-in-class** — Direct Keystore, `BiometricPrompt`, certificate pinning, and zero WebView attack surface. |
| **Performance** | **Good** — All heavy ML inference, OCR, and graph correlation execute on FastAPI, not on-device. WebView adds ~80–150 MB RAM overhead; `KillChainGraph` needs responsive touch tuning. | **Very Good** — Native UI thread rendering and smooth list/gesture handling. | **Best-in-class** — Lowest memory footprint, fastest startup, and 60/120fps Compose rendering. |
| **Camera & File Access** | **Full Native Access** — `@capacitor/camera`, `@capacitor/filesystem`, and native Android Share Intent (`ACTION_SEND`) for sharing suspicious screenshots/SMS directly into TRUSTLENS AI. | **Full Native Access** — `expo-camera` / `react-native-vision-camera`, document picker, and native share extension. | **Full Native Access** — CameraX, Storage Access Framework, and native Share Target. |
| **Push Notifications** | **Full FCM Support** — `@capacitor/push-notifications` integrates with Firebase Cloud Messaging and wires into `NotificationService` consent flags. | **Full FCM Support** — `expo-notifications` or `@react-native-firebase/messaging`. | **Full FCM Support** — Direct `FirebaseMessagingService` and Android notification channels. |
| **Maintainability & Long-Term Dev** | **Highest efficiency** — Single frontend team ships features to Web and Android simultaneously; custom Kotlin plugins can be added incrementally inside `android/`. | **Moderate** — Requires maintaining two separate UI codebases (Next.js Web + RN Mobile). | **Lowest efficiency** — Every feature, endpoint change, and UI update must be implemented twice. |

---

## 3. Architecture Decision

### Recommended Architecture: **Capacitor-Based Android Application (Hybrid Web + Native Kotlin Bridge)**

TRUSTLENS AI will adopt **Capacitor** wrapping the existing Next.js frontend, paired with targeted native Android plugins and a thin platform-abstraction layer in `frontend/lib/`.

#### Rationale
1. **Maximum Reuse Without Rewriting:** Preserves all existing Next.js pages, `ScanWorkbench`, `KillChainGraph`, `TelemetryCards`, and `frontend/lib/api.ts` without rewriting the web application.
2. **Backend-Heavy Compute Fit:** Because fraud detection, OCR, IOC enrichment, and campaign graph clustering run on the FastAPI backend, native UI rendering speed is not a bottleneck for core intelligence workflows.
3. **Full Native Capabilities Where Needed:** Camera capture, gallery access, Android Share Target (for instant "Share to TRUSTLENS AI" from WhatsApp/SMS), Android Keystore token storage, and FCM push notifications are all natively supported via Capacitor plugins and custom Kotlin bridges.
4. **Incremental Native Escape Hatch:** If future versions require background Android OS integrations (e.g., `CallScreeningService` or `NotificationListenerService`), those can be built as native Kotlin services/plugins inside the Capacitor `android/` project without discarding the app.

---

## 4. Required Pre-Implementation Adaptations (Non-Breaking)

Before generating the `android/` Capacitor project, the following targeted adaptations are required — **none of which rewrite the web app**:

1. **Next.js Dual-Mode Build (`frontend/next.config.mjs`):**
   - Retain `output: "standalone"` for web/Docker deployments, and support a conditional static export mode (e.g., `CAPACITOR_BUILD=true` -> `output: "export"`, `images: { unoptimized: true }`) with `NEXT_PUBLIC_API_URL` pointing directly to the HTTPS FastAPI backend (`https://api.trustlens.ai/api/v1`) instead of relying on Next.js server `rewrites()`.
   - Ensure dynamic routes such as `frontend/app/investigations/[id]/page.tsx` work cleanly with static export / client-side parameter reading.
2. **Secure Token Storage Adapter (`frontend/lib/api.ts`):**
   - Keep `localStorage` for standard web browsers, and use Capacitor's native secure storage plugin (backed by Android Keystore / `EncryptedSharedPreferences`) when `Capacitor.isNativePlatform()` is true, so JWTs are never exposed in WebView `localStorage`.
3. **Native Capabilities & Share Intent:**
   - Add `@capacitor/camera` + `@capacitor/filesystem` integration as an optional native source feeding `scanImage()` in `frontend/app/analyze/image/page.tsx` while keeping `<input type="file">` intact for web.
   - Register an Android `ACTION_SEND` Share Target in `AndroidManifest.xml` so users can share suspicious text, URLs, or screenshots directly from messaging apps into `/analyze/text`, `/analyze/url`, or `/analyze/image`.
4. **Push Notifications (`backend/app/services/notification_service.py` + FCM):**
   - Add `@capacitor/push-notifications` on Android to obtain the FCM registration token.
   - Add a backend endpoint to register/revoke device tokens per user and extend `NotificationService` to dispatch FCM push payloads only when `in_app_notifications` / `threat_alerts_opt_in` consent flags permit, without leaking raw sensitive message text in push previews.
5. **Backend CORS & Android Network Security:**
   - Add Capacitor origins (`https://localhost`, `capacitor://localhost`) to `ALLOWED_ORIGINS` in `backend/app/config/settings.py`.
   - Configure Android `network_security_config.xml` to disallow cleartext HTTP in production and pin/enforce TLS 1.2+.

---

## 5. When to Revisit This Decision

Re-evaluate **Native Kotlin (Jetpack Compose)** only if product requirements expand to require:
- Always-on background SMS/call interception (`CallScreeningService`, `NotificationListenerService`), or
- Heavy on-device ML inference (TFLite / ONNX Runtime) running offline in background services.
