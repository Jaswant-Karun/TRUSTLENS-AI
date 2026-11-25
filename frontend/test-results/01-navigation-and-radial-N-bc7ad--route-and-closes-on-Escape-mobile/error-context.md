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
        - link "TRUSTLENS AI" [ref=e81] [cursor=pointer]:
          - /url: /
        - link "SIGN IN" [ref=e92] [cursor=pointer]:
          - /url: /login
    - main [ref=e93]:
      - generic [ref=e94]:
        - generic [ref=e95]:
          - generic [ref=e97]: "ML CORE: OPERATIONAL"
          - generic [ref=e98]: "|"
          - generic [ref=e99]: ZERO-HOP URL SAFETY
        - generic [ref=e100]:
          - generic [ref=e101]: TRUSTLENS AI
          - heading "INTELLIGENCE THAT STOPS DIGITAL FRAUD." [level=1] [ref=e111]
          - paragraph [ref=e112]: Detect suspicious messages, malicious URLs and emerging digital fraud campaigns using intelligent multilingual analysis and real-world threat intelligence.
          - generic [ref=e113]:
            - link [ref=e114] [cursor=pointer]:
              - /url: /register
              - button "GET STARTED" [ref=e115]
            - link [ref=e118] [cursor=pointer]:
              - /url: /login
              - button "SIGN IN" [ref=e119]
        - region "Interactive Radial Navigation" [ref=e120]:
          - button "Expand TRUSTLENS AI radial navigation" [ref=e125] [cursor=pointer]:
            - generic [ref=e129]: EXPLORE
            - generic [ref=e130]: CLICK HUB
          - paragraph [ref=e131]: CLICK CENTER HUB TO ACCESS WORKFLOWS • ESC OR CLICK OUTSIDE TO CLOSE
        - region "Core Capabilities" [ref=e132]:
          - generic [ref=e133]:
            - heading "Multilingual Message Analysis" [level=2] [ref=e137]
            - paragraph [ref=e138]: Evaluates SMS, WhatsApp, and email text across English, Hindi (Devanagari), and Hinglish with calibrated risk scores and social-engineering tactic attribution.
          - generic [ref=e139]:
            - heading "Zero-Hop URL Shield" [level=2] [ref=e144]
            - paragraph [ref=e145]: Inspects 16 lexical and structural URL features using XGBoost and SHAP without ever opening, fetching, or executing the submitted link.
          - generic [ref=e146]:
            - heading "Screenshot OCR & Case Trails" [level=2] [ref=e155]
            - paragraph [ref=e156]: Validates PNG, JPEG, and WebP screenshots, extracts embedded text, and lets authenticated users attach evidence to persistent investigations.
        - generic [ref=e158]:
          - paragraph [ref=e163]: "Security & Privacy Guarantees: Submitted URLs are never visited or executed. Private investigations are isolated per account via JWT/RBAC. Campaign clustering reflects linguistic and indicator similarity, not legal proof of common criminal origin."
          - generic [ref=e164]: FASTAPI + ML CORE
    - contentinfo [ref=e169]:
      - generic [ref=e170]:
        - generic [ref=e171]: TRUSTLENS AI — Multilingual Digital Fraud Intelligence
        - generic [ref=e172]:
          - link "Scanner" [ref=e173] [cursor=pointer]:
            - /url: /analyze/text
          - link "Investigations" [ref=e174] [cursor=pointer]:
            - /url: /investigations
          - link "Reports" [ref=e175] [cursor=pointer]:
            - /url: /reports
    - navigation "Mobile primary navigation" [ref=e176]:
      - link "Text" [ref=e177] [cursor=pointer]:
        - /url: /analyze/text
      - link "URL" [ref=e181] [cursor=pointer]:
        - /url: /analyze/url
      - link "Image" [ref=e186] [cursor=pointer]:
        - /url: /analyze/image
      - link "Cases" [ref=e192] [cursor=pointer]:
        - /url: /investigations
      - link "Reports" [ref=e198] [cursor=pointer]:
        - /url: /reports
      - link "Profile" [ref=e202] [cursor=pointer]:
        - /url: /profile
  - alert [ref=e207]
```