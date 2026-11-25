# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 05-reports-and-exports.spec.ts >> Community Reports & Report Exports >> reports page search, filter, submission validation, and export controls
- Location: e2e\05-reports-and-exports.spec.ts:4:3

# Error details

```
Error: locator.fill: Error: strict mode violation: getByLabel(/password/i) resolved to 2 elements:
    1) <input value="" required="" type="password" id="login-password" placeholder="••••••••••••" autocomplete="current-password" class="cyber-input pl-10 pr-10"/> aka getByRole('textbox', { name: 'Password' })
    2) <button type="button" aria-label="Show password" class="absolute right-3 top-1/2 -translate-y-1/2 text-[#A1A1AA] hover:text-white">…</button> aka getByRole('button', { name: 'Show password' })

Call log:
  - waiting for getByLabel(/password/i)

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
    - main [ref=f1e26]:
      - generic [ref=f1e28]:
        - generic [ref=f1e29]:
          - heading "Sign In" [level=1] [ref=f1e37]
          - paragraph [ref=f1e38]: Access your TRUSTLENS AI intelligence workspace
        - generic [ref=f1e39]:
          - generic [ref=f1e40]:
            - generic [ref=f1e41]: Email Address
            - textbox "Email Address" [active] [ref=f1e43]:
              - /placeholder: analyst@organization.com
              - text: admin@trustlens.ai
          - generic [ref=f1e44]:
            - generic [ref=f1e45]:
              - generic [ref=f1e46]: Password
              - link "Forgot password?" [ref=f1e47] [cursor=pointer]:
                - /url: /forgot-password
            - generic [ref=f1e48]:
              - textbox "Password" [ref=f1e49]:
                - /placeholder: ••••••••••••
              - button "Show password" [ref=f1e50] [cursor=pointer]
          - button "SIGN IN TO TRUSTLENS" [ref=f1e54] [cursor=pointer]
        - paragraph [ref=f1e55]:
          - text: New to TRUSTLENS AI?
          - link "Create an account" [ref=f1e56] [cursor=pointer]:
            - /url: /register
    - contentinfo [ref=f1e57]:
      - generic [ref=f1e58]:
        - generic [ref=f1e59]: TRUSTLENS AI — Multilingual Digital Fraud Intelligence
        - generic [ref=f1e60]:
          - link "Scanner" [ref=f1e61] [cursor=pointer]:
            - /url: /analyze/text
          - link "Investigations" [ref=f1e62] [cursor=pointer]:
            - /url: /investigations
          - link "Reports" [ref=f1e63] [cursor=pointer]:
            - /url: /reports
  - alert [ref=f1e64]
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
  18 |     // Test Intelligence Report / Export triggers if present on /reports
  19 |     const exportBtn = page.getByRole("button", { name: /export|generate report|stix|json/i }).first();
  20 |     if (await exportBtn.isVisible()) {
  21 |       await exportBtn.click();
  22 |     }
  23 | 
  24 |     // Verify backend STIX & JSON export endpoints directly with authenticated session
  25 |     await page.goto("/login");
  26 |     await page.getByLabel(/email/i).fill("admin@trustlens.ai");
> 27 |     await page.getByLabel(/password/i).fill("Admin@TrustLens2026!");
     |                                        ^ Error: locator.fill: Error: strict mode violation: getByLabel(/password/i) resolved to 2 elements:
  28 |     await page.getByRole("button", { name: /sign in/i }).click();
  29 |     await expect(page).toHaveURL(/\/analyze\/text/);
  30 | 
  31 |     const exportCheck = await page.evaluate(async () => {
  32 |       const token = localStorage.getItem("trustlens_token");
  33 |       const res = await fetch(
  34 |         "/api/v1/exports/stix?target_type=investigation&target_id=INV-2026-0011",
  35 |         { headers: { Authorization: `Bearer ${token}` } }
  36 |       );
  37 |       return { status: res.status, ok: res.ok };
  38 |     });
  39 |     expect(exportCheck.status).toBeLessThan(500);
  40 |   });
  41 | });
  42 | 
```