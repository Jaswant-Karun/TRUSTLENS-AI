# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 04-investigations-graph-timeline.spec.ts >> Investigations, Graph Interactions, Filters, Search & Timeline Sync >> investigations directory search and workspace interactive controls
- Location: e2e\04-investigations-graph-timeline.spec.ts:4:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText(/Investigation Timeline/i).first()
Expected: visible
Timeout: 12000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByText(/Investigation Timeline/i).first() with timeout 12000ms
  - waiting for getByText(/Investigation Timeline/i).first()

```

```yaml
- banner:
  - button "Open primary radial navigation":
    - img
  - text: NAV WHEEL
  - link "TRUSTLENS AI":
    - /url: /
  - link "SIGN IN":
    - /url: /login
  - link "GET STARTED":
    - /url: /register
- banner:
  - link "TRUSTLENS AI Threat Intelligence":
    - /url: /dashboard
    - img
    - text: TRUSTLENS AI Threat Intelligence
  - navigation:
    - link "Home":
      - /url: /dashboard
    - button "Threat Library":
      - text: Threat Library
      - img
    - link "Investigations":
      - /url: /investigations
    - button "Analytics":
      - text: Analytics
      - img
  - button "Create":
    - img
    - text: Create
  - button "Search threat intelligence...":
    - img
  - button "Recent Investigation Activity":
    - img
  - button "Cyber Threat Playbook & Help":
    - img
  - link "Platform & Engine Settings":
    - /url: /settings
    - img
  - text: RS Senior Analyst SOC Lead
- complementary:
  - link "SOC Home":
    - /url: /dashboard
    - img
  - link "Investigation Graph Directory":
    - /url: /investigations
    - img
  - link "Threat Library":
    - /url: /threat-library
    - img
  - link "Analyze New Threat":
    - /url: /analyze/text
    - img
  - link "Analysis History":
    - /url: /history
    - img
- img
- textbox "Filter nodes..."
- text: /
- button "Reset Layout & Positions":
  - img
- button "Refresh Graph from Backend":
  - img
- button "Zoom In":
  - img
- button "Zoom Out":
  - img
- button "Fit to Screen":
  - img
- button "Toggle Bird's-Eye Minimap":
  - img
- button "Filter Object Types":
  - img
- text: "Live Intelligence Sync Active INV-2026-0011 Active Banking KYC Smishing Syndicate (Cluster #11) Created: Nov 22, 2026, 6:44 PM • Updated: Nov 24, 2026, 4:44 PM"
- img
- text: Radar Legend 10 nodes
- button "Campaign 1":
  - img
  - text: Campaign 1
- button "URL 1":
  - img
  - text: URL 1
- button "Domain 1":
  - img
  - text: Domain 1
- button "IP Address 1":
  - img
  - text: IP Address 1
- button "Message 1":
  - img
  - text: Message 1
- button "Tactic 2":
  - img
  - text: Tactic 2
- button "Indicator 1":
  - img
  - text: Indicator 1
- button "Report 1":
  - img
  - text: Report 1
- button "Source 1":
  - img
  - text: Source 1
- img
- img:
  - img
  - text: "254 Campaign Cluster #11 (SBI ..."
  - img
  - text: http://sbi-kyc-update.com
  - img
  - text: sbi-kyc-update.com
  - img
  - text: 194.168.20.14
  - img
  - text: "SMS: 'SBI A/C blocked toda..."
  - img
  - text: Urgency & Panic Coercion TACTIC_URGENCY_PANIC
  - img
  - text: Bank Authority Spoofing TACTIC_AUTHORITY_IMPERSONATION
  - img
  - text: 4 +91-8712778108 (Dispatch P... phone
  - img
  - text: "Community Report #07a380c7"
  - img
  - text: CERT-In CIAD-2026 Advisory
- complementary:
  - img
  - 'heading "Banking KYC Smishing Syndicate (Cluster #11)" [level=2]'
  - button "Collapse Panel":
    - img
  - text: Objects
  - paragraph: "10"
  - text: Tasks
  - paragraph: "2"
  - text: Comments
  - paragraph: "0"
  - text: Severity
  - paragraph: CRITICAL
  - text: Visibility
  - paragraph: Organization
  - text: Created
  - paragraph: Nov 22, 2026, 6:44 PM by Senior Analyst (RS)
  - text: Last Modified
  - paragraph: Nov 24, 2026, 4:44 PM by SOC Lead (TK)
  - button "Description":
    - text: Description
    - img
  - paragraph: Multilingual Smishing campaign targeting State Bank of India customers with urgent account freeze alerts leading to credential harvesting.
  - button "Sources (4)":
    - text: Sources (4)
    - img
  - paragraph: "TRUSTLENS ML Telemetry, ScamShield Corpus, Community Report #07a380c7, CERT-In"
  - button "Tags (6)":
    - text: Tags (6)
    - img
  - text: "#sbi_kyc #smishing #model1_bilstm #model2_xgboost #cluster_11 #phishing_url"
  - button "Attributes (5)":
    - text: Attributes (5)
    - img
  - text: "Targeted Institution: State Bank of India (PSU Banking) Campaign Hub: HDBSCAN Cluster #11 Primary Attack Vector: SMS Phishing with Urgency Coercion Hosting Provider: Offshore Bulletproof Ltd (AS49870) Target Geography: India (National Banking Sector)"
  - img
  - text: Analyst Notes (0)
  - textbox "Add persistent investigation note (requires sign-in)..."
  - button "Save Note" [disabled]:
    - img
    - text: Save Note
  - text: No notes recorded for this investigation yet.
- img
- text: Correlation Timeline | Tasks & Mitigation Situation & Pretexts Detections & Indicators
- button "Refresh":
  - img
  - text: Refresh
- button "Minimize":
  - text: Minimize
  - img
- text: Tasks Situation Selected / IOC
- 'button "Automated HDBSCAN Cluster #11 Formed"'
- button "CERT-In & ISP Takedown Initiated"
- button "First Observed Smishing Wave"
- button "Citizen Incident Report Received"
- button "Phishing FQDN sbi-kyc-update.com Registered"
- button "A-Record Resolution to Bulletproof IP 194.168.20.14"
- text: NOV 22 NOV 23 NOV 24
- alert
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
  27 |     await page.getByTitle("Fit to Screen").click();
  28 |     await page.getByTitle("Reset Layout & Positions").click();
  29 | 
  30 |     // Minimap toggle
  31 |     const minimapBtn = page.getByTitle("Toggle Bird's-Eye Minimap");
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
> 54 |     await expect(timelineHeader).toBeVisible();
     |                                  ^ Error: expect(locator).toBeVisible() failed
  55 |     const refreshTimelineBtn = page.getByTitle(/refresh timeline/i).first();
  56 |     if (await refreshTimelineBtn.isVisible()) {
  57 |       await refreshTimelineBtn.click();
  58 |     }
  59 |   });
  60 | });
  61 | 
```