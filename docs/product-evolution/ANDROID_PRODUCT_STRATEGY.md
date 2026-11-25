# TRUSTLENS AI — ANDROID PRODUCT STRATEGY (GOOGLE PLAY STORE)

> **Phase:** 3.0 Strategy (Do Not Start Mobile Development Yet)

---

## 1. Framework Comparison & Recommendation

| Criteria | **React Native (Expo)** *(Recommended)* | **Capacitor (Web Wrapper)** | **Native Android (Kotlin/Compose)** |
| :--- | :--- | :--- | :--- |
| **Code & Team Alignment** | High — shares TypeScript, API client patterns, and Zod/schema types with Next.js 14 frontend | High — wraps web bundle directly | Low — requires separate Kotlin/Jetpack Compose codebase |
| **Native Android Capabilities** | Strong — Share Sheet (`ACTION_SEND`), Camera/OCR picker, SecureStore (Android Keystore), FCM push notifications | Moderate — plugin-dependent WebView | Maximum — full native APIs |
| **UX & Performance** | Native UI primitives, smooth 60fps animations, offline queue | WebView feel, slower cold start | Best native performance |
| **Maintenance Cost** | Single TypeScript/Python engineering stack | Lowest, but Play Store WebView quality scrutiny | Highest (2x frontend maintenance) |

**Decision:** **React Native with Expo (Managed Workflow + Dev Client)** in TypeScript. It preserves a unified TypeScript client stack alongside Next.js 14, supports Android Keystore (`expo-secure-store`), Android Share Intent (so users can share a suspicious SMS/WhatsApp message directly to TRUSTLENS AI), and clean Play Store compliance.

---

## 2. Shared Backend & Mobile API Readiness

The Android app will consume the **exact same FastAPI backend (`/api/v1/*`)**:
- `POST /api/v1/auth/login`, `/register`, `/refresh` (token rotation), `/logout`
- `POST /api/v1/analyze/text`, `/url`, `/image`, `/comprehensive`
- `GET /api/v1/analyses`, `GET /api/v1/investigations`, `POST /api/v1/reports`
- **No business logic or ML weights duplicated on-device initially** (server-side inference guarantees consistent SHA-256 model governance and zero-hop URL safety).

---

## 3. Google Play Store Compliance Requirements

1. **Data Safety Form & Privacy Policy:**
   - Disclose collection of user-submitted text, URLs, and screenshots for fraud analysis.
   - Link to hosted public Privacy Policy (`/privacy`) and Terms.
2. **Mandatory Account Deletion (Play Store Policy):**
   - Provide **in-app account deletion** AND a **public web deletion request URL** (`/account/delete`) that deletes/anonymizes `users`, personal `analyses`, and `Private` investigations.
3. **Permissions Minimization:**
   - Request **only** `INTERNET`, optional `READ_MEDIA_IMAGES` / Photo Picker (for screenshot scan), and optional `POST_NOTIFICATIONS` (Android 13+ runtime opt-in only for consented threat alerts). **Never** request `READ_SMS` or `CALL_LOG` (high-risk restricted permissions that trigger Play Store rejection unless acting as default SMS app).
4. **Release Testing Track:**
   - Internal Testing -> Closed Testing (minimum Play Console tester requirement) -> Production staged rollout (`10% -> 50% -> 100%`) with crash/ANR monitoring.
