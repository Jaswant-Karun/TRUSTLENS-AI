# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 05-reports-and-exports.spec.ts >> Community Reports & Report Exports >> reports page search, filter, submission validation, and export controls
- Location: e2e\05-reports-and-exports.spec.ts:4:3

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: 200
Received: 429
```

# Page snapshot

```yaml
- generic [ref=e1]:
  - generic [ref=e3]:
    - banner [ref=e4]:
      - generic [ref=e5]:
        - generic [ref=e6]:
          - button "Open primary radial navigation" [ref=e8] [cursor=pointer]
          - generic [ref=e12]: NAV WHEEL
        - link "TRUSTLENS AI" [ref=e13] [cursor=pointer]:
          - /url: /
        - generic [ref=e23]:
          - link "SIGN IN" [ref=e24] [cursor=pointer]:
            - /url: /login
          - link "GET STARTED" [ref=e25] [cursor=pointer]:
            - /url: /register
    - main [ref=e26]:
      - generic [ref=e27]:
        - generic [ref=e28]:
          - navigation "Breadcrumb" [ref=e29]:
            - link "Home" [ref=e30] [cursor=pointer]:
              - /url: /
            - generic [ref=e36]: Records
            - generic [ref=e39]: Reports
          - heading "Community Threat Reports & Review" [level=1] [ref=e40]
        - navigation "Quick workflow navigation" [ref=e41]:
          - link "Messages" [ref=e42] [cursor=pointer]:
            - /url: /analyze/text
          - link "URLs" [ref=e43] [cursor=pointer]:
            - /url: /analyze/url
          - link "OCR" [ref=e44] [cursor=pointer]:
            - /url: /analyze/image
          - link "History" [ref=e45] [cursor=pointer]:
            - /url: /history
          - link "Investigations" [ref=e46] [cursor=pointer]:
            - /url: /investigations
          - link "Reports" [ref=e47] [cursor=pointer]:
            - /url: /reports
      - generic [ref=e48]:
        - generic [ref=e49]:
          - generic [ref=e51]:
            - generic [ref=e52]:
              - heading "Community Threat Reporting & Review Hub" [level=1] [ref=e53]
              - generic [ref=e54]: Crowd Intelligence Feed
            - paragraph [ref=e55]: Contribute suspicious lures, fraudulent UPI IDs, and phishing domains to collective defensive intelligence.
          - button "Submit Scam Report" [ref=e56] [cursor=pointer]
        - generic [ref=e59]:
          - generic [ref=e60]: Public Contributor Mode — Anyone can submit reports. Sign in as SOC Analyst to access verification controls.
          - button "Sign in as Analyst" [ref=e65] [cursor=pointer]
        - generic [ref=e70]:
          - generic [ref=e71]:
            - generic [ref=e72]: Total Submissions
            - generic [ref=e80]:
              - generic [ref=e81]: "9"
              - generic [ref=e83]: Crowd-sourced signals logged
          - generic [ref=e85]:
            - generic [ref=e86]: Verified Scams
            - generic [ref=e91]:
              - generic [ref=e92]: "1"
              - generic [ref=e94]: Confirmed malicious campaigns
          - generic [ref=e96]:
            - generic [ref=e97]: Under Review
            - generic [ref=e103]:
              - generic [ref=e104]: "0"
              - generic [ref=e106]: Awaiting analyst triage
          - generic [ref=e108]:
            - generic [ref=e109]: Benign Submissions
            - generic [ref=e115]:
              - generic [ref=e116]: "0"
              - generic [ref=e118]: Legitimate communications
        - generic [ref=e120]:
          - generic [ref=e121]:
            - heading "Community Incident Intelligence Feed" [level=3] [ref=e128]
            - generic [ref=e129]: 9 Active Records • 1 Verified Malicious
          - generic [ref=e130]:
            - textbox "Search reports by content, sender, or ID..." [active] [ref=e135]
            - combobox [ref=e136]:
              - option "All Statuses" [selected]
              - option "Verified Scam"
              - option "Under Review"
              - option "Pending"
              - option "Benign"
          - table [ref=e139]:
            - rowgroup [ref=e140]:
              - row [ref=e141]:
                - columnheader "Report ID" [ref=e142]
                - columnheader "Vector" [ref=e143]
                - columnheader "Identifier / Origin" [ref=e144]
                - columnheader "Reported Content Excerpt" [ref=e145]
                - columnheader "Tactics" [ref=e146]
                - columnheader "Status & Verification" [ref=e147]
                - columnheader "Action" [ref=e148]
            - rowgroup [ref=e149]:
              - row [ref=e150] [cursor=pointer]:
                - cell "26ee4fc4-9ce8-4abc-af99-d6616ed65d6c" [ref=e151]
                - cell "url" [ref=e152]
                - cell "http://instant-cash-loan-approval.top" [ref=e153]
                - 'cell "Reported fake loan verification link: http://instant-cash-loan-approval.top Note: Scam WhatsApp loan offer" [ref=e154]':
                  - generic [ref=e155]:
                    - generic [ref=e156]: "Reported fake loan verification link: http://instant-cash-loan-approval.top"
                    - generic [ref=e157]: "Note: Scam WhatsApp loan offer"
                - cell "Unassigned" [ref=e158]
                - cell "Unverified Submission" [ref=e161]
                - cell [ref=e166]:
                  - button "Analyst Login" [ref=e167]
              - row [ref=e168] [cursor=pointer]:
                - cell "006e7b53-bf77-4365-a298-edaa7c408431" [ref=e169]
                - cell "url" [ref=e170]
                - cell "http://instant-cash-loan-approval.top" [ref=e171]
                - 'cell "Reported fake loan verification link: http://instant-cash-loan-approval.top Note: Scam WhatsApp loan offer" [ref=e172]':
                  - generic [ref=e173]:
                    - generic [ref=e174]: "Reported fake loan verification link: http://instant-cash-loan-approval.top"
                    - generic [ref=e175]: "Note: Scam WhatsApp loan offer"
                - cell "Unassigned" [ref=e176]
                - cell "Unverified Submission" [ref=e179]
                - cell [ref=e184]:
                  - button "Analyst Login" [ref=e185]
              - row [ref=e186] [cursor=pointer]:
                - cell "6b303dbe-e4e9-4a5a-a7bb-ca0d225583c9" [ref=e187]
                - cell "url" [ref=e188]
                - cell "http://instant-cash-loan-approval.top" [ref=e189]
                - 'cell "Reported fake loan verification link: http://instant-cash-loan-approval.top Note: Scam WhatsApp loan offer" [ref=e190]':
                  - generic [ref=e191]:
                    - generic [ref=e192]: "Reported fake loan verification link: http://instant-cash-loan-approval.top"
                    - generic [ref=e193]: "Note: Scam WhatsApp loan offer"
                - cell "Unassigned" [ref=e194]
                - cell "Unverified Submission" [ref=e197]
                - cell [ref=e202]:
                  - button "Analyst Login" [ref=e203]
              - row [ref=e204] [cursor=pointer]:
                - cell "2e01e47a-8ff7-4c9e-8aef-d47a4f61b2fc" [ref=e205]
                - cell "url" [ref=e206]
                - cell "http://instant-cash-loan-approval.top" [ref=e207]
                - 'cell "Reported fake loan verification link: http://instant-cash-loan-approval.top Note: Scam WhatsApp loan offer" [ref=e208]':
                  - generic [ref=e209]:
                    - generic [ref=e210]: "Reported fake loan verification link: http://instant-cash-loan-approval.top"
                    - generic [ref=e211]: "Note: Scam WhatsApp loan offer"
                - cell "Unassigned" [ref=e212]
                - cell "Unverified Submission" [ref=e215]
                - cell [ref=e220]:
                  - button "Analyst Login" [ref=e221]
              - row [ref=e222] [cursor=pointer]:
                - cell "342726b8-ec23-4231-96bf-f57b5551be7f" [ref=e223]
                - cell "sms" [ref=e224]
                - cell "+919999900000" [ref=e225]
                - cell "Test urgent KYC link http://test-kyc.xyz" [ref=e226]
                - cell "bank impersonation" [ref=e229]
                - cell "Verified Scam" [ref=e232]
                - cell [ref=e237]:
                  - button "Analyst Login" [ref=e238]
              - row [ref=e239] [cursor=pointer]:
                - cell "ff74880d-17fc-44ab-86f1-e80a58882609" [ref=e240]
                - cell "url" [ref=e241]
                - cell "http://instant-cash-loan-approval.top" [ref=e242]
                - 'cell "Reported fake loan verification link: http://instant-cash-loan-approval.top Note: Scam WhatsApp loan offer" [ref=e243]':
                  - generic [ref=e244]:
                    - generic [ref=e245]: "Reported fake loan verification link: http://instant-cash-loan-approval.top"
                    - generic [ref=e246]: "Note: Scam WhatsApp loan offer"
                - cell "Unassigned" [ref=e247]
                - cell "Unverified Submission" [ref=e250]
                - cell [ref=e255]:
                  - button "Analyst Login" [ref=e256]
              - row [ref=e257] [cursor=pointer]:
                - cell "b99e12af-2f14-4c2a-9c04-7d585f130432" [ref=e258]
                - cell "url" [ref=e259]
                - cell "http://instant-cash-loan-approval.top" [ref=e260]
                - 'cell "Reported fake loan verification link: http://instant-cash-loan-approval.top Note: Scam WhatsApp loan offer" [ref=e261]':
                  - generic [ref=e262]:
                    - generic [ref=e263]: "Reported fake loan verification link: http://instant-cash-loan-approval.top"
                    - generic [ref=e264]: "Note: Scam WhatsApp loan offer"
                - cell "Unassigned" [ref=e265]
                - cell "Unverified Submission" [ref=e268]
                - cell [ref=e273]:
                  - button "Analyst Login" [ref=e274]
              - row [ref=e275] [cursor=pointer]:
                - cell "07a380c7-7322-4dbf-8c1e-f63d8810a3a3" [ref=e276]
                - cell "url" [ref=e277]
                - cell "http://power-bill-disconnection.xyz" [ref=e278]
                - 'cell "Phishing site spoofing state electricity board bill collection: http://power-bill-disconnection.xyz Note: Received via SMS warning of power cut at 9 PM" [ref=e279]':
                  - generic [ref=e280]:
                    - generic [ref=e281]: "Phishing site spoofing state electricity board bill collection: http://power-bill-disconnection.xyz"
                    - generic [ref=e282]: "Note: Received via SMS warning of power cut at 9 PM"
                - cell "Unassigned" [ref=e283]
                - cell "Unverified Submission" [ref=e286]
                - cell [ref=e291]:
                  - button "Analyst Login" [ref=e292]
              - row [ref=e293] [cursor=pointer]:
                - cell "93b30c5b-7a93-4b09-ba59-c883fcb7161e" [ref=e294]
                - cell "url" [ref=e295]
                - cell "http://power-bill-disconnection.xyz" [ref=e296]
                - 'cell "Phishing site spoofing state electricity board bill collection: http://power-bill-disconnection.xyz Note: Received via SMS warning of power cut at 9 PM" [ref=e297]':
                  - generic [ref=e298]:
                    - generic [ref=e299]: "Phishing site spoofing state electricity board bill collection: http://power-bill-disconnection.xyz"
                    - generic [ref=e300]: "Note: Received via SMS warning of power cut at 9 PM"
                - cell "Unassigned" [ref=e301]
                - cell "Unverified Submission" [ref=e304]
                - cell [ref=e309]:
                  - button "Analyst Login" [ref=e310]
          - generic [ref=e311]:
            - generic [ref=e313]:
              - heading "Investigation Report Generator & STIX 2.1 / JSON Exports" [level=2] [ref=e314]
              - paragraph [ref=e319]: Generate auditable intelligence dossiers with model versions, evidence provenance, review status, and explicit limitations.
            - generic [ref=e320]:
              - generic [ref=e321]:
                - generic [ref=e322]: Report Type
                - combobox [ref=e323]:
                  - option "Comprehensive Investigation" [selected]
                  - option "Campaign Similarity Cluster"
                  - option "Model Evaluation Summary"
                  - option "Individual Message Analysis"
                  - option "URL Analysis"
              - generic [ref=e324]:
                - generic [ref=e325]: Target Identifier
                - textbox "INV-2026-0011" [ref=e326]
              - button "Generate Report" [ref=e327] [cursor=pointer]
              - generic [ref=e332]:
                - button "JSON" [ref=e333] [cursor=pointer]
                - button "STIX 2.1" [ref=e338] [cursor=pointer]
  - alert [ref=e343]
```

# Test source

```ts
  1  | import { test, expect } from "@playwright/test";
  2  | 
  3  | test.describe("Community Reports & Report Exports", () => {
  4  |   test("reports page search, filter, submission validation, and export controls", async ({
  5  |     page,
  6  |   }) => {
  7  |     await page.goto("/reports");
  8  |     await expect(page.getByText(/Community Threat Reports/i).first()).toBeVisible();
  9  | 
  10 |     // Search/filter reports table
  11 |     const searchBox = page.getByPlaceholder(/search/i).first();
  12 |     if (await searchBox.isVisible()) {
  13 |       await searchBox.fill("HDFC");
  14 |       await expect(searchBox).toHaveValue("HDFC");
  15 |       await searchBox.fill("");
  16 |     }
  17 | 
  18 |     // Authenticate via /api/v1/auth/login inside browser context to test protected STIX/JSON exports
  19 |     const exportCheck = await page.evaluate(async () => {
  20 |       const loginRes = await fetch("/api/v1/auth/login", {
  21 |         method: "POST",
  22 |         headers: { "Content-Type": "application/json" },
  23 |         body: JSON.stringify({
  24 |           email: "admin@trustlens.ai",
  25 |           password: "Admin@TrustLens2026!",
  26 |         }),
  27 |       });
  28 |       if (!loginRes.ok) {
  29 |         return { loginStatus: loginRes.status, stixStatus: 0, jsonStatus: 0 };
  30 |       }
  31 |       const { access_token } = await loginRes.json();
  32 |       localStorage.setItem("trustlens_token", access_token);
  33 | 
  34 |       const stixRes = await fetch(
  35 |         "/api/v1/exports/stix?target_type=investigation&target_id=INV-2026-0011",
  36 |         { headers: { Authorization: `Bearer ${access_token}` } }
  37 |       );
  38 |       const jsonRes = await fetch(
  39 |         "/api/v1/exports/json?target_type=investigation&target_id=INV-2026-0011",
  40 |         { headers: { Authorization: `Bearer ${access_token}` } }
  41 |       );
  42 |       return {
  43 |         loginStatus: loginRes.status,
  44 |         stixStatus: stixRes.status,
  45 |         jsonStatus: jsonRes.status,
  46 |       };
  47 |     });
  48 | 
> 49 |     expect(exportCheck.loginStatus).toBe(200);
     |                                     ^ Error: expect(received).toBe(expected) // Object.is equality
  50 |     expect(exportCheck.stixStatus).toBeLessThan(500);
  51 |     expect(exportCheck.jsonStatus).toBeLessThan(500);
  52 | 
  53 |     // Reload /reports authenticated and verify Intelligence Report / Export UI controls if present
  54 |     await page.reload();
  55 |     const exportBtn = page.getByRole("button", { name: /export|generate report|stix|json/i }).first();
  56 |     if (await exportBtn.isVisible()) {
  57 |       await exportBtn.click();
  58 |     }
  59 |   });
  60 | });
  61 | 
```