# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 04-investigations-graph-timeline.spec.ts >> Investigations, Graph Interactions, Filters, Search & Timeline Sync >> investigations directory search and workspace interactive controls
- Location: e2e\04-investigations-graph-timeline.spec.ts:4:3

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByTitle('Fit Screen')

```

# Page snapshot

```yaml
- generic [ref=f1e1]:
  - generic [ref=f1e3]:
    - banner [ref=f1e4]:
      - generic [ref=f1e5]:
        - button "Open primary radial navigation" [ref=f1e8] [cursor=pointer]
        - link "TRUSTLENS AI" [ref=f1e12] [cursor=pointer]:
          - /url: /
        - link "SIGN IN" [ref=f1e23] [cursor=pointer]:
          - /url: /login
    - generic [ref=f1e25]:
      - banner [ref=f1e26]:
        - generic [ref=f1e27]:
          - link "TRUSTLENS AI Threat Intelligence" [ref=f1e28] [cursor=pointer]:
            - /url: /dashboard
            - generic [ref=f1e32]:
              - generic [ref=f1e33]:
                - generic [ref=f1e34]: TRUSTLENS
                - generic [ref=f1e35]: AI
              - generic [ref=f1e36]: Threat Intelligence
          - navigation [ref=f1e38]:
            - link "Home" [ref=f1e39] [cursor=pointer]:
              - /url: /dashboard
            - button "Threat Library" [ref=f1e42] [cursor=pointer]
            - link "Investigations" [ref=f1e46] [cursor=pointer]:
              - /url: /investigations
            - button "Analytics" [ref=f1e51] [cursor=pointer]
        - generic [ref=f1e55]:
          - button "Create" [ref=f1e56] [cursor=pointer]
          - button "Search threat intelligence..." [ref=f1e59] [cursor=pointer]
          - button "Recent Investigation Activity" [ref=f1e64] [cursor=pointer]
          - button "Cyber Threat Playbook & Help" [ref=f1e68] [cursor=pointer]
          - link "Platform & Engine Settings" [ref=f1e72] [cursor=pointer]:
            - /url: /settings
          - generic [ref=f1e76]: RS
      - generic [ref=f1e78]:
        - generic [ref=f1e79]:
          - generic [ref=f1e80]:
            - textbox "Filter nodes..." [ref=f1e85]
            - generic [ref=f1e86]:
              - button "Reset Layout & Positions" [ref=f1e87] [cursor=pointer]
              - button "Refresh Graph from Backend" [ref=f1e91] [cursor=pointer]
            - generic [ref=f1e97]:
              - button "Zoom In" [ref=f1e98] [cursor=pointer]
              - button "Zoom Out" [active] [ref=f1e100] [cursor=pointer]
              - button "Fit to Screen" [ref=f1e102] [cursor=pointer]
            - generic [ref=f1e108]:
              - button "Toggle Bird's-Eye Minimap" [ref=f1e109] [cursor=pointer]
              - button "Filter Object Types" [ref=f1e113] [cursor=pointer]
          - img [ref=f1e117]:
            - generic [ref=f1e118]:
              - generic [ref=f1e119] [cursor=pointer]
              - generic [ref=f1e121] [cursor=pointer]
              - generic [ref=f1e123] [cursor=pointer]
              - generic [ref=f1e125] [cursor=pointer]
              - generic [ref=f1e127] [cursor=pointer]
              - generic [ref=f1e129] [cursor=pointer]
              - generic [ref=f1e131] [cursor=pointer]
              - generic [ref=f1e133] [cursor=pointer]
              - generic [ref=f1e135] [cursor=pointer]
              - generic [ref=f1e137] [cursor=pointer]:
                - generic [ref=f1e140]: "254"
                - generic: "Campaign Cluster #11 (SBI ..."
              - generic [ref=f1e142] [cursor=pointer]: http://sbi-kyc-update.com
              - generic [ref=f1e144] [cursor=pointer]: sbi-kyc-update.com
              - generic [ref=f1e146] [cursor=pointer]: 194.168.20.14
              - generic [ref=f1e148] [cursor=pointer]: "SMS: 'SBI A/C blocked toda..."
              - generic [ref=f1e150] [cursor=pointer]:
                - generic: Urgency & Panic Coercion
                - generic: TACTIC_URGENCY_PANIC
              - generic [ref=f1e152] [cursor=pointer]:
                - generic: Bank Authority Spoofing
                - generic: TACTIC_AUTHORITY_IMPERSONATION
              - generic [ref=f1e154] [cursor=pointer]:
                - generic [ref=f1e156]: "4"
                - generic: +91-8712778108 (Dispatch P...
                - generic: phone
              - generic [ref=f1e158] [cursor=pointer]: "Community Report #07a380c7"
              - generic [ref=f1e160] [cursor=pointer]: CERT-In CIAD-2026 Advisory
        - complementary [ref=f1e162]:
          - generic [ref=f1e163]:
            - 'heading "Banking KYC Smishing Syndicate (Cluster #11)" [level=2] [ref=f1e168]'
            - button "Collapse Panel" [ref=f1e170] [cursor=pointer]
          - generic [ref=f1e173]:
            - generic [ref=f1e174]:
              - generic [ref=f1e175]:
                - generic [ref=f1e176]:
                  - text: Objects
                  - paragraph [ref=f1e177]: "10"
                - generic [ref=f1e178]:
                  - text: Tasks
                  - paragraph [ref=f1e179]: "2"
                - generic [ref=f1e180]:
                  - text: Comments
                  - paragraph [ref=f1e181]: "0"
              - generic [ref=f1e182]:
                - generic [ref=f1e183]:
                  - text: Severity
                  - paragraph [ref=f1e184]: CRITICAL
                - generic [ref=f1e185]:
                  - text: Visibility
                  - paragraph [ref=f1e186]: Organization
              - generic [ref=f1e187]:
                - generic [ref=f1e188]:
                  - text: Created
                  - paragraph [ref=f1e189]: Nov 22, 2026, 6:44 PM by Senior Analyst (RS)
                - generic [ref=f1e190]:
                  - text: Last Modified
                  - paragraph [ref=f1e191]: Nov 24, 2026, 4:44 PM by SOC Lead (TK)
              - generic [ref=f1e192]:
                - button "Description" [ref=f1e193] [cursor=pointer]
                - paragraph [ref=f1e197]: Multilingual Smishing campaign targeting State Bank of India customers with urgent account freeze alerts leading to credential harvesting.
              - generic [ref=f1e198]:
                - button "Sources (4)" [ref=f1e199] [cursor=pointer]
                - paragraph [ref=f1e203]: "TRUSTLENS ML Telemetry, ScamShield Corpus, Community Report #07a380c7, CERT-In"
              - generic [ref=f1e204]:
                - button "Tags (6)" [ref=f1e205] [cursor=pointer]
                - generic [ref=f1e209]:
                  - generic [ref=f1e210]: "#sbi_kyc"
                  - generic [ref=f1e211]: "#smishing"
                  - generic [ref=f1e212]: "#model1_bilstm"
                  - generic [ref=f1e213]: "#model2_xgboost"
                  - generic [ref=f1e214]: "#cluster_11"
                  - generic [ref=f1e215]: "#phishing_url"
              - generic [ref=f1e216]:
                - button "Attributes (5)" [ref=f1e217] [cursor=pointer]
                - generic [ref=f1e221]:
                  - generic [ref=f1e222]:
                    - generic [ref=f1e223]: "Targeted Institution:"
                    - generic [ref=f1e224]: State Bank of India (PSU Banking)
                  - generic [ref=f1e225]:
                    - generic [ref=f1e226]: "Campaign Hub:"
                    - generic [ref=f1e227]: "HDBSCAN Cluster #11"
                  - generic [ref=f1e228]:
                    - generic [ref=f1e229]: "Primary Attack Vector:"
                    - generic [ref=f1e230]: SMS Phishing with Urgency Coercion
                  - generic [ref=f1e231]:
                    - generic [ref=f1e232]: "Hosting Provider:"
                    - generic [ref=f1e233]: Offshore Bulletproof Ltd (AS49870)
                  - generic [ref=f1e234]:
                    - generic [ref=f1e235]: "Target Geography:"
                    - generic [ref=f1e236]: India (National Banking Sector)
            - generic [ref=f1e237]:
              - generic [ref=f1e238]: Analyst Notes (0)
              - generic [ref=f1e243]:
                - textbox "Add persistent investigation note (requires sign-in)..." [ref=f1e244]
                - button "Save Note" [disabled] [ref=f1e245]
              - generic [ref=f1e250]: No notes recorded for this investigation yet.
      - generic [ref=f1e251]:
        - generic [ref=f1e252]:
          - generic [ref=f1e253]:
            - generic [ref=f1e254]: Correlation Timeline
            - generic [ref=f1e259]: "|"
            - generic [ref=f1e260]:
              - generic [ref=f1e261]: Tasks & Mitigation
              - generic [ref=f1e264]: Situation & Pretexts
              - generic [ref=f1e267]: Detections & Indicators
          - generic [ref=f1e270]:
            - button "Refresh" [ref=f1e271] [cursor=pointer]
            - button "Minimize" [ref=f1e278] [cursor=pointer]
        - generic [ref=f1e282]:
          - generic [ref=f1e283]:
            - generic [ref=f1e284]: Tasks
            - generic [ref=f1e285]: Situation
            - generic [ref=f1e286]: Selected / IOC
          - generic [ref=f1e287]:
            - generic [ref=f1e288]:
              - 'button "Automated HDBSCAN Cluster #11 Formed" [ref=f1e289] [cursor=pointer]'
              - button "CERT-In & ISP Takedown Initiated" [ref=f1e291] [cursor=pointer]
            - generic [ref=f1e293]:
              - button "First Observed Smishing Wave" [ref=f1e294] [cursor=pointer]
              - button "Citizen Incident Report Received" [ref=f1e296] [cursor=pointer]
            - generic [ref=f1e298]:
              - button "Phishing FQDN sbi-kyc-update.com Registered" [ref=f1e299] [cursor=pointer]
              - button "A-Record Resolution to Bulletproof IP 194.168.20.14" [ref=f1e301] [cursor=pointer]
            - generic [ref=f1e303]:
              - generic [ref=f1e304]: NOV 22
              - generic [ref=f1e305]: NOV 23
              - generic [ref=f1e306]: NOV 24
    - navigation "Mobile primary navigation" [ref=f1e307]:
      - link "Text" [ref=f1e308] [cursor=pointer]:
        - /url: /analyze/text
      - link "URL" [ref=f1e312] [cursor=pointer]:
        - /url: /analyze/url
      - link "Image" [ref=f1e317] [cursor=pointer]:
        - /url: /analyze/image
      - link "Cases" [ref=f1e323] [cursor=pointer]:
        - /url: /investigations
      - link "Reports" [ref=f1e329] [cursor=pointer]:
        - /url: /reports
      - link "Profile" [ref=f1e333] [cursor=pointer]:
        - /url: /profile
  - alert [ref=f1e338]
```

# Test source

```ts
  1  | import { test, expect } from "@playwright/test";
  2  | 
  3  | test.describe("Investigations, Graph Interactions, Filters, Search & Timeline Sync", () => {
  4  |   test("investigations directory search and workspace interactive controls", async ({
  5  |     page,
  6  |   }) => {
  7  |     await page.goto("/investigations");
  8  |     const dirSearch = page.getByPlaceholder(/search/i).first();
  9  |     await expect(dirSearch).toBeVisible();
  10 |     await dirSearch.fill("KYC");
  11 | 
  12 |     // Open investigation dossier
  13 |     await page.goto("/investigations/INV-2026-0011");
  14 | 
  15 |     // Wait for workspace toolbar & graph to finish loading
  16 |     const nodeSearch = page.getByPlaceholder("Filter nodes...");
  17 |     await expect(nodeSearch).toBeVisible({ timeout: 20_000 });
  18 | 
  19 |     // Search nodes
  20 |     await nodeSearch.fill("sbi");
  21 |     await expect(nodeSearch).toHaveValue("sbi");
  22 |     await nodeSearch.fill("");
  23 | 
  24 |     // Graph zoom & layout controls
  25 |     await page.getByTitle("Zoom In").click();
  26 |     await page.getByTitle("Zoom Out").click();
> 27 |     await page.getByTitle("Fit Screen").click();
     |                                         ^ Error: locator.click: Test timeout of 45000ms exceeded.
  28 |     await page.getByTitle("Reset Layout & Positions").click();
  29 | 
  30 |     // Minimap toggle
  31 |     const minimapBtn = page.getByTitle(/minimap/i).first();
  32 |     await minimapBtn.click();
  33 |     await minimapBtn.click();
  34 | 
  35 |     // Graph Filter Panel
  36 |     const filterBtn = page.getByRole("button", { name: /filter/i }).first();
  37 |     await filterBtn.click();
  38 |     const clearBtn = page.getByRole("button", { name: /clear all/i }).first();
  39 |     if (await clearBtn.isVisible()) {
  40 |       await clearBtn.click();
  41 |       await page.getByRole("button", { name: /select all/i }).first().click();
  42 |     }
  43 | 
  44 |     // ObjectInspector collapse & expand
  45 |     const collapseBtn = page.getByTitle("Collapse Panel");
  46 |     if (await collapseBtn.isVisible()) {
  47 |       await collapseBtn.click();
  48 |       await expect(page.getByTitle("Expand Details Panel")).toBeVisible();
  49 |       await page.getByTitle("Expand Details Panel").click();
  50 |     }
  51 | 
  52 |     // Timeline collapse/expand & event selection synchronization
  53 |     const timelineHeader = page.getByText(/Investigation Timeline/i).first();
  54 |     await expect(timelineHeader).toBeVisible();
  55 |     const refreshTimelineBtn = page.getByTitle(/refresh timeline/i).first();
  56 |     if (await refreshTimelineBtn.isVisible()) {
  57 |       await refreshTimelineBtn.click();
  58 |     }
  59 |   });
  60 | });
  61 | 
```