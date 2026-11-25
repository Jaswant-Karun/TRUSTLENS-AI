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
          - generic [ref=f1e78]:
            - generic [ref=f1e79]: RS
            - generic [ref=f1e80]:
              - generic [ref=f1e81]: Senior Analyst
              - generic [ref=f1e82]: SOC Lead
      - generic [ref=f1e83]:
        - complementary [ref=f1e84]:
          - link "SOC Home" [ref=f1e85] [cursor=pointer]:
            - /url: /dashboard
          - link "Investigation Graph Directory" [ref=f1e91] [cursor=pointer]:
            - /url: /investigations
          - link "Threat Library" [ref=f1e97] [cursor=pointer]:
            - /url: /threat-library
          - link "Analyze New Threat" [ref=f1e101] [cursor=pointer]:
            - /url: /analyze/text
          - link "Analysis History" [ref=f1e104] [cursor=pointer]:
            - /url: /history
        - generic [ref=f1e109]:
          - generic [ref=f1e110]:
            - generic [ref=f1e111]:
              - textbox "Filter nodes..." [ref=f1e115]
              - generic [ref=f1e116]: /
            - generic [ref=f1e117]:
              - button "Reset Layout & Positions" [ref=f1e118] [cursor=pointer]
              - button "Refresh Graph from Backend" [ref=f1e122] [cursor=pointer]
            - generic [ref=f1e128]:
              - button "Zoom In" [ref=f1e129] [cursor=pointer]
              - button "Zoom Out" [active] [ref=f1e131] [cursor=pointer]
              - button "Fit to Screen" [ref=f1e133] [cursor=pointer]
            - generic [ref=f1e139]:
              - button "Toggle Bird's-Eye Minimap" [ref=f1e140] [cursor=pointer]
              - button "Filter Object Types" [ref=f1e144] [cursor=pointer]
            - generic [ref=f1e147]: Live Intelligence Sync Active
          - generic:
            - generic:
              - generic: INV-2026-0011
              - generic: Active
            - generic: "Banking KYC Smishing Syndicate (Cluster #11)"
            - generic: "Created: Nov 22, 2026, 6:44 PM • Updated: Nov 24, 2026, 4:44 PM"
          - generic [ref=f1e150]:
            - generic [ref=f1e151]: Radar
            - generic [ref=f1e164]:
              - generic [ref=f1e165]:
                - generic [ref=f1e166]: Legend
                - generic [ref=f1e167]: 10 nodes
              - generic [ref=f1e168]:
                - button "Campaign 1" [ref=f1e169] [cursor=pointer]:
                  - generic [ref=f1e170]: Campaign
                  - generic [ref=f1e176]: "1"
                - button "URL 1" [ref=f1e177] [cursor=pointer]:
                  - generic [ref=f1e178]: URL
                  - generic [ref=f1e185]: "1"
                - button "Domain 1" [ref=f1e186] [cursor=pointer]:
                  - generic [ref=f1e187]: Domain
                  - generic [ref=f1e194]: "1"
                - button "IP Address 1" [ref=f1e195] [cursor=pointer]:
                  - generic [ref=f1e196]: IP Address
                  - generic [ref=f1e203]: "1"
                - button "Message 1" [ref=f1e204] [cursor=pointer]:
                  - generic [ref=f1e205]: Message
                  - generic [ref=f1e212]: "1"
                - button "Tactic 2" [ref=f1e213] [cursor=pointer]:
                  - generic [ref=f1e214]: Tactic
                  - generic [ref=f1e220]: "2"
                - button "Indicator 1" [ref=f1e221] [cursor=pointer]:
                  - generic [ref=f1e222]: Indicator
                  - generic [ref=f1e235]: "1"
                - button "Report 1" [ref=f1e236] [cursor=pointer]:
                  - generic [ref=f1e237]: Report
                  - generic [ref=f1e245]: "1"
                - button "Source 1" [ref=f1e246] [cursor=pointer]:
                  - generic [ref=f1e247]: Source
                  - generic [ref=f1e255]: "1"
          - img [ref=f1e257]:
            - generic [ref=f1e258]:
              - generic [ref=f1e259] [cursor=pointer]
              - generic [ref=f1e261] [cursor=pointer]
              - generic [ref=f1e263] [cursor=pointer]
              - generic [ref=f1e265] [cursor=pointer]
              - generic [ref=f1e267] [cursor=pointer]
              - generic [ref=f1e269] [cursor=pointer]
              - generic [ref=f1e271] [cursor=pointer]
              - generic [ref=f1e273] [cursor=pointer]
              - generic [ref=f1e275] [cursor=pointer]
              - generic [ref=f1e277] [cursor=pointer]:
                - generic [ref=f1e280]: "254"
                - generic: "Campaign Cluster #11 (SBI ..."
              - generic [ref=f1e282] [cursor=pointer]: http://sbi-kyc-update.com
              - generic [ref=f1e284] [cursor=pointer]: sbi-kyc-update.com
              - generic [ref=f1e286] [cursor=pointer]: 194.168.20.14
              - generic [ref=f1e288] [cursor=pointer]: "SMS: 'SBI A/C blocked toda..."
              - generic [ref=f1e290] [cursor=pointer]:
                - generic: Urgency & Panic Coercion
                - generic: TACTIC_URGENCY_PANIC
              - generic [ref=f1e292] [cursor=pointer]:
                - generic: Bank Authority Spoofing
                - generic: TACTIC_AUTHORITY_IMPERSONATION
              - generic [ref=f1e294] [cursor=pointer]:
                - generic [ref=f1e296]: "4"
                - generic: +91-8712778108 (Dispatch P...
                - generic: phone
              - generic [ref=f1e298] [cursor=pointer]: "Community Report #07a380c7"
              - generic [ref=f1e300] [cursor=pointer]: CERT-In CIAD-2026 Advisory
        - complementary [ref=f1e302]:
          - generic [ref=f1e303]:
            - 'heading "Banking KYC Smishing Syndicate (Cluster #11)" [level=2] [ref=f1e308]'
            - button "Collapse Panel" [ref=f1e310] [cursor=pointer]
          - generic [ref=f1e313]:
            - generic [ref=f1e314]:
              - generic [ref=f1e315]:
                - generic [ref=f1e316]:
                  - text: Objects
                  - paragraph [ref=f1e317]: "10"
                - generic [ref=f1e318]:
                  - text: Tasks
                  - paragraph [ref=f1e319]: "2"
                - generic [ref=f1e320]:
                  - text: Comments
                  - paragraph [ref=f1e321]: "0"
              - generic [ref=f1e322]:
                - generic [ref=f1e323]:
                  - text: Severity
                  - paragraph [ref=f1e324]: CRITICAL
                - generic [ref=f1e325]:
                  - text: Visibility
                  - paragraph [ref=f1e326]: Organization
              - generic [ref=f1e327]:
                - generic [ref=f1e328]:
                  - text: Created
                  - paragraph [ref=f1e329]: Nov 22, 2026, 6:44 PM by Senior Analyst (RS)
                - generic [ref=f1e330]:
                  - text: Last Modified
                  - paragraph [ref=f1e331]: Nov 24, 2026, 4:44 PM by SOC Lead (TK)
              - generic [ref=f1e332]:
                - button "Description" [ref=f1e333] [cursor=pointer]
                - paragraph [ref=f1e337]: Multilingual Smishing campaign targeting State Bank of India customers with urgent account freeze alerts leading to credential harvesting.
              - generic [ref=f1e338]:
                - button "Sources (4)" [ref=f1e339] [cursor=pointer]
                - paragraph [ref=f1e343]: "TRUSTLENS ML Telemetry, ScamShield Corpus, Community Report #07a380c7, CERT-In"
              - generic [ref=f1e344]:
                - button "Tags (6)" [ref=f1e345] [cursor=pointer]
                - generic [ref=f1e349]:
                  - generic [ref=f1e350]: "#sbi_kyc"
                  - generic [ref=f1e351]: "#smishing"
                  - generic [ref=f1e352]: "#model1_bilstm"
                  - generic [ref=f1e353]: "#model2_xgboost"
                  - generic [ref=f1e354]: "#cluster_11"
                  - generic [ref=f1e355]: "#phishing_url"
              - generic [ref=f1e356]:
                - button "Attributes (5)" [ref=f1e357] [cursor=pointer]
                - generic [ref=f1e361]:
                  - generic [ref=f1e362]:
                    - generic [ref=f1e363]: "Targeted Institution:"
                    - generic [ref=f1e364]: State Bank of India (PSU Banking)
                  - generic [ref=f1e365]:
                    - generic [ref=f1e366]: "Campaign Hub:"
                    - generic [ref=f1e367]: "HDBSCAN Cluster #11"
                  - generic [ref=f1e368]:
                    - generic [ref=f1e369]: "Primary Attack Vector:"
                    - generic [ref=f1e370]: SMS Phishing with Urgency Coercion
                  - generic [ref=f1e371]:
                    - generic [ref=f1e372]: "Hosting Provider:"
                    - generic [ref=f1e373]: Offshore Bulletproof Ltd (AS49870)
                  - generic [ref=f1e374]:
                    - generic [ref=f1e375]: "Target Geography:"
                    - generic [ref=f1e376]: India (National Banking Sector)
            - generic [ref=f1e377]:
              - generic [ref=f1e378]: Analyst Notes (0)
              - generic [ref=f1e383]:
                - textbox "Add persistent investigation note (requires sign-in)..." [ref=f1e384]
                - button "Save Note" [disabled] [ref=f1e385]
              - generic [ref=f1e390]: No notes recorded for this investigation yet.
      - generic [ref=f1e391]:
        - generic [ref=f1e392]:
          - generic [ref=f1e393]:
            - generic [ref=f1e394]: Correlation Timeline
            - generic [ref=f1e399]: "|"
            - generic [ref=f1e400]:
              - generic [ref=f1e401]: Tasks & Mitigation
              - generic [ref=f1e404]: Situation & Pretexts
              - generic [ref=f1e407]: Detections & Indicators
          - generic [ref=f1e410]:
            - button "Refresh" [ref=f1e411] [cursor=pointer]
            - button "Minimize" [ref=f1e418] [cursor=pointer]
        - generic [ref=f1e422]:
          - generic [ref=f1e423]:
            - generic [ref=f1e424]: Tasks
            - generic [ref=f1e425]: Situation
            - generic [ref=f1e426]: Selected / IOC
          - generic [ref=f1e427]:
            - generic [ref=f1e428]:
              - 'button "Automated HDBSCAN Cluster #11 Formed" [ref=f1e429] [cursor=pointer]'
              - button "CERT-In & ISP Takedown Initiated" [ref=f1e431] [cursor=pointer]
            - generic [ref=f1e433]:
              - button "First Observed Smishing Wave" [ref=f1e434] [cursor=pointer]
              - button "Citizen Incident Report Received" [ref=f1e436] [cursor=pointer]
            - generic [ref=f1e438]:
              - button "Phishing FQDN sbi-kyc-update.com Registered" [ref=f1e439] [cursor=pointer]
              - button "A-Record Resolution to Bulletproof IP 194.168.20.14" [ref=f1e441] [cursor=pointer]
            - generic [ref=f1e443]:
              - generic [ref=f1e444]: NOV 22
              - generic [ref=f1e445]: NOV 23
              - generic [ref=f1e446]: NOV 24
  - alert [ref=f1e447]
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