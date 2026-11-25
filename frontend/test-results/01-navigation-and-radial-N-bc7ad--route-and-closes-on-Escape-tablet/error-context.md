# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 01-navigation-and-radial.spec.ts >> Navigation, Radial Wheel & All Routes >> radial navigation opens, navigates to target route, and closes on Escape
- Location: e2e\01-navigation-and-radial.spec.ts:29:3

# Error details

```
Test timeout of 45000ms exceeded.
```

# Page snapshot

```yaml
- generic [ref=e1]:
  - generic [ref=e3]:
    - banner [ref=e4]:
      - generic [ref=e5]:
        - generic [ref=e6]:
          - generic [ref=e7]:
            - button "Open primary radial navigation" [expanded] [ref=e8] [cursor=pointer]
            - menu "TRUSTLENS AI Primary Navigation" [ref=e14]:
              - menuitem "Home" [active] [ref=e26] [cursor=pointer]:
                - generic [ref=e31]: HOME
              - menuitem "Message Scanner" [ref=e32] [cursor=pointer]:
                - generic [ref=e36]: MESSAGES
              - menuitem "URL Shield" [ref=e37] [cursor=pointer]:
                - generic [ref=e42]: URL SHIELD
              - menuitem "Screenshot Analyzer" [ref=e43] [cursor=pointer]:
                - generic [ref=e52]: OCR SCAN
              - menuitem "Threat Intelligence" [ref=e53] [cursor=pointer]:
                - generic [ref=e57]: THREATS
              - menuitem "Investigations" [ref=e58] [cursor=pointer]:
                - generic [ref=e64]: CASES
              - menuitem "Reports" [ref=e65] [cursor=pointer]:
                - generic [ref=e70]: REPORTS
              - menuitem "Profile" [ref=e71] [cursor=pointer]:
                - generic [ref=e76]: PROFILE
              - button "Close radial navigation" [ref=e77] [cursor=pointer]
          - generic [ref=e81]: NAV WHEEL
        - link "TRUSTLENS AI" [ref=e82] [cursor=pointer]:
          - /url: /
        - generic [ref=e92]:
          - link "SIGN IN" [ref=e93] [cursor=pointer]:
            - /url: /login
          - link "GET STARTED" [ref=e94] [cursor=pointer]:
            - /url: /register
    - main [ref=e95]:
      - generic [ref=e96]:
        - generic [ref=e97]:
          - generic [ref=e99]: "ML CORE: OPERATIONAL"
          - generic [ref=e100]: "|"
          - generic [ref=e101]: ZERO-HOP URL SAFETY
        - generic [ref=e102]:
          - generic [ref=e103]: TRUSTLENS AI
          - heading "INTELLIGENCE THAT STOPS DIGITAL FRAUD." [level=1] [ref=e113]
          - paragraph [ref=e114]: Detect suspicious messages, malicious URLs and emerging digital fraud campaigns using intelligent multilingual analysis and real-world threat intelligence.
          - generic [ref=e115]:
            - link [ref=e116] [cursor=pointer]:
              - /url: /register
              - button "GET STARTED" [ref=e117]
            - link [ref=e120] [cursor=pointer]:
              - /url: /login
              - button "SIGN IN" [ref=e121]
        - region "Interactive Radial Navigation" [ref=e122]:
          - button "Expand TRUSTLENS AI radial navigation" [ref=e127] [cursor=pointer]:
            - generic [ref=e131]: EXPLORE
            - generic [ref=e132]: CLICK HUB
          - paragraph [ref=e133]: CLICK CENTER HUB TO ACCESS WORKFLOWS • ESC OR CLICK OUTSIDE TO CLOSE
        - region "Core Capabilities" [ref=e134]:
          - generic [ref=e135]:
            - heading "Multilingual Message Analysis" [level=2] [ref=e139]
            - paragraph [ref=e140]: Evaluates SMS, WhatsApp, and email text across English, Hindi (Devanagari), and Hinglish with calibrated risk scores and social-engineering tactic attribution.
          - generic [ref=e141]:
            - heading "Zero-Hop URL Shield" [level=2] [ref=e146]
            - paragraph [ref=e147]: Inspects 16 lexical and structural URL features using XGBoost and SHAP without ever opening, fetching, or executing the submitted link.
          - generic [ref=e148]:
            - heading "Screenshot OCR & Case Trails" [level=2] [ref=e157]
            - paragraph [ref=e158]: Validates PNG, JPEG, and WebP screenshots, extracts embedded text, and lets authenticated users attach evidence to persistent investigations.
        - generic [ref=e160]:
          - paragraph [ref=e165]: "Security & Privacy Guarantees: Submitted URLs are never visited or executed. Private investigations are isolated per account via JWT/RBAC. Campaign clustering reflects linguistic and indicator similarity, not legal proof of common criminal origin."
          - generic [ref=e166]: FASTAPI + ML CORE
    - contentinfo [ref=e171]:
      - generic [ref=e172]:
        - generic [ref=e173]: TRUSTLENS AI — Multilingual Digital Fraud Intelligence
        - generic [ref=e174]:
          - link "Scanner" [ref=e175] [cursor=pointer]:
            - /url: /analyze/text
          - link "Investigations" [ref=e176] [cursor=pointer]:
            - /url: /investigations
          - link "Reports" [ref=e177] [cursor=pointer]:
            - /url: /reports
  - alert [ref=e178]
```