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
        - generic [ref=f1e6]:
          - button "Open primary radial navigation" [ref=f1e8] [cursor=pointer]
          - generic [ref=f1e12]: NAV WHEEL
        - link "TRUSTLENS AI" [ref=f1e13] [cursor=pointer]:
          - /url: /
        - generic [ref=f1e23]:
          - link "SIGN IN" [ref=f1e24] [cursor=pointer]:
            - /url: /login
          - link "GET STARTED" [ref=f1e25] [cursor=pointer]:
            - /url: /register
    - generic [ref=f1e27]:
      - banner [ref=f1e28]:
        - generic [ref=f1e29]:
          - link "TRUSTLENS AI Threat Intelligence" [ref=f1e30] [cursor=pointer]:
            - /url: /dashboard
            - generic [ref=f1e34]:
              - generic [ref=f1e35]:
                - generic [ref=f1e36]: TRUSTLENS
                - generic [ref=f1e37]: AI
              - generic [ref=f1e38]: Threat Intelligence
          - navigation [ref=f1e40]:
            - link "Home" [ref=f1e41] [cursor=pointer]:
              - /url: /dashboard
            - button "Threat Library" [ref=f1e44] [cursor=pointer]
            - link "Investigations" [ref=f1e48] [cursor=pointer]:
              - /url: /investigations
            - button "Analytics" [ref=f1e53] [cursor=pointer]
        - generic [ref=f1e57]:
          - button "Create" [ref=f1e58] [cursor=pointer]
          - button "Search threat intelligence..." [ref=f1e61] [cursor=pointer]
          - button "Recent Investigation Activity" [ref=f1e66] [cursor=pointer]
          - button "Cyber Threat Playbook & Help" [ref=f1e70] [cursor=pointer]
          - link "Platform & Engine Settings" [ref=f1e74] [cursor=pointer]:
            - /url: /settings
          - generic [ref=f1e78]: RS
      - generic [ref=f1e80]:
        - complementary [ref=f1e81]:
          - link "SOC Home" [ref=f1e82] [cursor=pointer]:
            - /url: /dashboard
          - link "Investigation Graph Directory" [ref=f1e88] [cursor=pointer]:
            - /url: /investigations
          - link "Threat Library" [ref=f1e94] [cursor=pointer]:
            - /url: /threat-library
          - link "Analyze New Threat" [ref=f1e98] [cursor=pointer]:
            - /url: /analyze/text
          - link "Analysis History" [ref=f1e101] [cursor=pointer]:
            - /url: /history
        - generic [ref=f1e106]:
          - generic [ref=f1e107]:
            - generic [ref=f1e108]:
              - textbox "Filter nodes..." [ref=f1e112]
              - generic [ref=f1e113]: /
            - generic [ref=f1e114]:
              - button "Reset Layout & Positions" [ref=f1e115] [cursor=pointer]
              - button "Refresh Graph from Backend" [ref=f1e119] [cursor=pointer]
            - generic [ref=f1e125]:
              - button "Zoom In" [ref=f1e126] [cursor=pointer]
              - button "Zoom Out" [active] [ref=f1e128] [cursor=pointer]
              - button "Fit to Screen" [ref=f1e130] [cursor=pointer]
            - generic [ref=f1e136]:
              - button "Toggle Bird's-Eye Minimap" [ref=f1e137] [cursor=pointer]
              - button "Filter Object Types" [ref=f1e141] [cursor=pointer]
          - generic:
            - generic:
              - generic: INV-2026-0011
              - generic: Active
            - generic: "Banking KYC Smishing Syndicate (Cluster #11)"
            - generic: "Created: Nov 22, 2026, 6:44 PM • Updated: Nov 24, 2026, 4:44 PM"
          - img [ref=f1e145]:
            - generic [ref=f1e146]:
              - generic [ref=f1e147] [cursor=pointer]
              - generic [ref=f1e149] [cursor=pointer]
              - generic [ref=f1e151] [cursor=pointer]
              - generic [ref=f1e153] [cursor=pointer]
              - generic [ref=f1e155] [cursor=pointer]
              - generic [ref=f1e157] [cursor=pointer]
              - generic [ref=f1e159] [cursor=pointer]
              - generic [ref=f1e161] [cursor=pointer]
              - generic [ref=f1e163] [cursor=pointer]
              - generic [ref=f1e165] [cursor=pointer]:
                - generic [ref=f1e168]: "254"
                - generic: "Campaign Cluster #11 (SBI ..."
              - generic [ref=f1e170] [cursor=pointer]: http://sbi-kyc-update.com
              - generic [ref=f1e172] [cursor=pointer]: sbi-kyc-update.com
              - generic [ref=f1e174] [cursor=pointer]: 194.168.20.14
              - generic [ref=f1e176] [cursor=pointer]: "SMS: 'SBI A/C blocked toda..."
              - generic [ref=f1e178] [cursor=pointer]:
                - generic: Urgency & Panic Coercion
                - generic: TACTIC_URGENCY_PANIC
              - generic [ref=f1e180] [cursor=pointer]:
                - generic: Bank Authority Spoofing
                - generic: TACTIC_AUTHORITY_IMPERSONATION
              - generic [ref=f1e182] [cursor=pointer]:
                - generic [ref=f1e184]: "4"
                - generic: +91-8712778108 (Dispatch P...
                - generic: phone
              - generic [ref=f1e186] [cursor=pointer]: "Community Report #07a380c7"
              - generic [ref=f1e188] [cursor=pointer]: CERT-In CIAD-2026 Advisory
        - complementary [ref=f1e190]:
          - generic [ref=f1e191]:
            - 'heading "Banking KYC Smishing Syndicate (Cluster #11)" [level=2] [ref=f1e196]'
            - button "Collapse Panel" [ref=f1e198] [cursor=pointer]
          - generic [ref=f1e201]:
            - generic [ref=f1e202]:
              - generic [ref=f1e203]:
                - generic [ref=f1e204]:
                  - text: Objects
                  - paragraph [ref=f1e205]: "10"
                - generic [ref=f1e206]:
                  - text: Tasks
                  - paragraph [ref=f1e207]: "2"
                - generic [ref=f1e208]:
                  - text: Comments
                  - paragraph [ref=f1e209]: "0"
              - generic [ref=f1e210]:
                - generic [ref=f1e211]:
                  - text: Severity
                  - paragraph [ref=f1e212]: CRITICAL
                - generic [ref=f1e213]:
                  - text: Visibility
                  - paragraph [ref=f1e214]: Organization
              - generic [ref=f1e215]:
                - generic [ref=f1e216]:
                  - text: Created
                  - paragraph [ref=f1e217]: Nov 22, 2026, 6:44 PM by Senior Analyst (RS)
                - generic [ref=f1e218]:
                  - text: Last Modified
                  - paragraph [ref=f1e219]: Nov 24, 2026, 4:44 PM by SOC Lead (TK)
              - generic [ref=f1e220]:
                - button "Description" [ref=f1e221] [cursor=pointer]
                - paragraph [ref=f1e225]: Multilingual Smishing campaign targeting State Bank of India customers with urgent account freeze alerts leading to credential harvesting.
              - generic [ref=f1e226]:
                - button "Sources (4)" [ref=f1e227] [cursor=pointer]
                - paragraph [ref=f1e231]: "TRUSTLENS ML Telemetry, ScamShield Corpus, Community Report #07a380c7, CERT-In"
              - generic [ref=f1e232]:
                - button "Tags (6)" [ref=f1e233] [cursor=pointer]
                - generic [ref=f1e237]:
                  - generic [ref=f1e238]: "#sbi_kyc"
                  - generic [ref=f1e239]: "#smishing"
                  - generic [ref=f1e240]: "#model1_bilstm"
                  - generic [ref=f1e241]: "#model2_xgboost"
                  - generic [ref=f1e242]: "#cluster_11"
                  - generic [ref=f1e243]: "#phishing_url"
              - generic [ref=f1e244]:
                - button "Attributes (5)" [ref=f1e245] [cursor=pointer]
                - generic [ref=f1e249]:
                  - generic [ref=f1e250]:
                    - generic [ref=f1e251]: "Targeted Institution:"
                    - generic [ref=f1e252]: State Bank of India (PSU Banking)
                  - generic [ref=f1e253]:
                    - generic [ref=f1e254]: "Campaign Hub:"
                    - generic [ref=f1e255]: "HDBSCAN Cluster #11"
                  - generic [ref=f1e256]:
                    - generic [ref=f1e257]: "Primary Attack Vector:"
                    - generic [ref=f1e258]: SMS Phishing with Urgency Coercion
                  - generic [ref=f1e259]:
                    - generic [ref=f1e260]: "Hosting Provider:"
                    - generic [ref=f1e261]: Offshore Bulletproof Ltd (AS49870)
                  - generic [ref=f1e262]:
                    - generic [ref=f1e263]: "Target Geography:"
                    - generic [ref=f1e264]: India (National Banking Sector)
            - generic [ref=f1e265]:
              - generic [ref=f1e266]: Analyst Notes (0)
              - generic [ref=f1e271]:
                - textbox "Add persistent investigation note (requires sign-in)..." [ref=f1e272]
                - button "Save Note" [disabled] [ref=f1e273]
              - generic [ref=f1e278]: No notes recorded for this investigation yet.
      - generic [ref=f1e279]:
        - generic [ref=f1e280]:
          - generic [ref=f1e281]:
            - generic [ref=f1e282]: Correlation Timeline
            - generic [ref=f1e287]: "|"
            - generic [ref=f1e288]:
              - generic [ref=f1e289]: Tasks & Mitigation
              - generic [ref=f1e292]: Situation & Pretexts
              - generic [ref=f1e295]: Detections & Indicators
          - generic [ref=f1e298]:
            - button "Refresh" [ref=f1e299] [cursor=pointer]
            - button "Minimize" [ref=f1e306] [cursor=pointer]
        - generic [ref=f1e310]:
          - generic [ref=f1e311]:
            - generic [ref=f1e312]: Tasks
            - generic [ref=f1e313]: Situation
            - generic [ref=f1e314]: Selected / IOC
          - generic [ref=f1e315]:
            - generic [ref=f1e316]:
              - 'button "Automated HDBSCAN Cluster #11 Formed" [ref=f1e317] [cursor=pointer]'
              - button "CERT-In & ISP Takedown Initiated" [ref=f1e319] [cursor=pointer]
            - generic [ref=f1e321]:
              - button "First Observed Smishing Wave" [ref=f1e322] [cursor=pointer]
              - button "Citizen Incident Report Received" [ref=f1e324] [cursor=pointer]
            - generic [ref=f1e326]:
              - button "Phishing FQDN sbi-kyc-update.com Registered" [ref=f1e327] [cursor=pointer]
              - button "A-Record Resolution to Bulletproof IP 194.168.20.14" [ref=f1e329] [cursor=pointer]
            - generic [ref=f1e331]:
              - generic [ref=f1e332]: NOV 22
              - generic [ref=f1e333]: NOV 23
              - generic [ref=f1e334]: NOV 24
  - alert [ref=f1e335]
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