# TRUSTLENS AI — Google Play Store Submission Guide

- **Application ID:** `ai.trustlens.mobile`
- **Target SDK / Compile SDK:** Android 16 (API 36) (`frontend/android/variables.gradle`)
- **Minimum SDK:** Android 7.0 (API 24)
- **Status:** Prepared for **Internal Testing** upload (not yet submitted or approved by Google Play)

---

## 1. Policy & Target API Verification
- **Target API Level:** `targetSdkVersion = 36` and `compileSdkVersion = 36` satisfy Google Play's requirement targeting Android 15/16 (API 35/36+) for 2025/2026 releases.
- **16 KB Memory Page Size:** App uses pure Java/Kotlin + system WebView + `androidx.security:security-crypto` with no custom native `.so` binaries.
- **No Debug Endpoints or Secrets in Release:**
  - `frontend/android/app/src/main/res/xml/network_security_config.xml` strictly sets `cleartextTrafficPermitted="false"` globally.
  - Localhost/emulator cleartext rules (`10.0.2.2`, `127.0.0.1`, `localhost`) are isolated to `src/debug/res/xml/network_security_config.xml` and excluded from release `.aab` builds.
  - `buildTypes.release` sets `debuggable false`, `minifyEnabled true`, `shrinkResources true`.

---

## 2. Release Build, Signing & Android App Bundle (`.aab`)

### 2.1 Generate Upload Keystore (Once, Outside Git)
```powershell
keytool -genkey -v -keystore frontend/android/release-upload-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias trustlens-upload
```
Copy `frontend/android/keystore.properties.example` to `frontend/android/keystore.properties` (gitignored) and populate `storeFile`, `storePassword`, `keyAlias`, `keyPassword`.

### 2.2 Build Signed Release `.aab`
```powershell
cd frontend
$env:CAPACITOR_BUILD="true"
$env:NEXT_PUBLIC_API_URL="https://api.trustlens.ai/api/v1"
npx next build
npx cap sync android
cd android
.\gradlew.bat bundleRelease -PTRUSTLENS_VERSION_CODE=1 -PTRUSTLENS_VERSION_NAME=1.0.0
```
Output bundle: `frontend/android/app/build/outputs/bundle/release/app-release.aab`.
Use **Google Play App Signing** in Play Console (Google manages the app signing key; you upload with your upload key).

---

## 3. Privacy Policy URL
- **URL:** `https://trustlens.vercel.app/privacy-policy` (implemented in `frontend/app/privacy-policy/page.tsx`, backed by `GET /api/v1/privacy/policy`).
- **Transparent AI Methodology URL:** `https://trustlens.vercel.app/methodology`.

---

## 4. Google Play Data Safety Disclosures

| Data Category | Data Type | Collected | Shared | Purpose | Encryption & Deletion |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Personal info** | Name, Email address, User IDs | Yes | No | Account management, authentication | Encrypted in transit (TLS) & at rest; user can delete account via `/profile` or `/api/v1/privacy/account` |
| **Messages / Files** | User-submitted suspicious text, URLs, or screenshots | Yes (user-initiated only) | No (redacted before community intelligence) | Fraud/phishing analysis & OCR | Encrypted in transit (TLS); individual scans deletable via `/history` |
| **App activity** | App interactions, scan history | Yes | No | Security audit trail & user history | Encrypted in transit; deletable |
| **Device or other IDs** | FCM push token (optional, opt-in) | Only if user enables push | No | Consented investigation/threat alerts | Revocable anytime via `DELETE /api/v1/notifications/device-token` |

- **Data Encrypted in Transit:** Yes (HTTPS/TLS enforced in release `network_security_config.xml`).
- **Users Can Request Data Deletion:** Yes (self-service in Profile / Privacy settings and `security@trustlens.ai`).

---

## 5. Content Rating (IARC) Preparation
- **Category:** Tools / Security / Utilities
- **Violence, Sexual Content, Profanity, Gambling:** None
- **User-Generated Content (UGC):** Users can submit suspicious fraud reports to moderators; reports undergo moderation/verification before publication and are not publicly broadcast unmoderated.
- **Expected Rating:** Everyone / PEGI 3 / IARC 3+.

---

## 6. Permission Declarations
Only permissions tied to active user-triggered features are declared in `AndroidManifest.xml`:
- `INTERNET`, `ACCESS_NETWORK_STATE`: Communicating with TRUSTLENS AI API and displaying offline banners.
- `CAMERA` (`required="false"`): Capturing a photo of a suspicious SMS/notice only when the user taps **Take Photo (Camera)** (preceded by an in-app rationale modal).
- `READ_MEDIA_IMAGES` (API 33+) & `READ_EXTERNAL_STORAGE` (`maxSdkVersion="32"`): Selecting a screenshot from Gallery only when the user taps **Choose from Gallery** (preceded by an in-app rationale modal).
- `POST_NOTIFICATIONS` (API 33+): Delivering consented investigation/threat notifications (preceded by an in-app rationale modal).

---

## 7. Store Listing Assets & Copy
- **App Name:** `TRUSTLENS AI`
- **Short Description (<=80 chars):** `Analyze suspicious messages, URLs, and screenshots for digital fraud signals.`
- **Full Description Guidelines:** Clearly state decision-support scope (`English`, `Hindi`, `Hinglish`), OCR limitations, and human review requirements. Never claim 100% accuracy or universal fraud detection.
- **Graphic Assets Generated:**
  - `docs/play_store/assets/ic_launcher_512.png` (512x512 Hi-Res Icon)
  - `docs/play_store/assets/feature_graphic_1024x500.png` (1024x500 Feature Graphic)
- **Support / Security Contact:** `security@trustlens.ai`

---

## 8. Internal Testing Release Checklist
1. Enable **Play App Signing** in Google Play Console.
2. Upload `app-release.aab` to **Testing -> Internal testing**.
3. Complete **Data safety**, **App content / Content rating**, **Privacy policy URL**, and **Store listing**.
4. Add internal tester Gmail accounts and verify:
   - Login, registration, logout, and Android Keystore persistence across app restarts.
   - Message, URL, and Camera/Gallery screenshot analysis.
   - Android Share-Sheet (`ACTION_SEND`) handoff from SMS/WhatsApp.
   - Hardware back-button behavior and offline connectivity banner.
5. Review Google Play **Pre-launch report** before promoting to Closed/Production testing.
6. **Do not claim Play Store approval until Google Play Console explicitly marks the release as Approved/Published.**
