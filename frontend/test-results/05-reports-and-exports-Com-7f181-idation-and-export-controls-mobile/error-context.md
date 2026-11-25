# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 05-reports-and-exports.spec.ts >> Community Reports & Report Exports >> reports page search, filter, submission validation, and export controls
- Location: e2e\05-reports-and-exports.spec.ts:4:3

# Error details

```
Error: expect(page).toHaveURL(expected) failed

Expected pattern: /\/analyze\/text/
Received string:  "http://127.0.0.1:3000/login"
Timeout: 12000ms

Call log:
  - Expect "toHaveURL" with timeout 12000ms
    27 × locator resolved to <html lang="en">…</html>
       - unexpected value "http://127.0.0.1:3000/login"

```

```yaml
- banner:
  - button "Open primary radial navigation":
    - img
  - link "TRUSTLENS AI":
    - /url: /
  - link "SIGN IN":
    - /url: /login
- main:
  - heading "Sign In" [level=1]
  - paragraph: Access your TRUSTLENS AI intelligence workspace
  - alert:
    - img
    - text: Too many authentication attempts. Limit is 20 per minute.
  - text: Email Address
  - img
  - textbox "Email Address":
    - /placeholder: analyst@organization.com
    - text: admin@trustlens.ai
  - text: Password
  - link "Forgot password?":
    - /url: /forgot-password
  - img
  - textbox "Password":
    - /placeholder: ••••••••••••
    - text: Admin@TrustLens2026!
  - button "Show password":
    - img
  - button "SIGN IN TO TRUSTLENS"
  - paragraph:
    - text: New to TRUSTLENS AI?
    - link "Create an account":
      - /url: /register
- contentinfo:
  - text: TRUSTLENS AI — Multilingual Digital Fraud Intelligence
  - link "Scanner":
    - /url: /analyze/text
  - link "Investigations":
    - /url: /investigations
  - link "Reports":
    - /url: /reports
- navigation "Mobile primary navigation":
  - link "Text":
    - /url: /analyze/text
    - img
    - text: Text
  - link "URL":
    - /url: /analyze/url
    - img
    - text: URL
  - link "Image":
    - /url: /analyze/image
    - img
    - text: Image
  - link "Cases":
    - /url: /investigations
    - img
    - text: Cases
  - link "Reports":
    - /url: /reports
    - img
    - text: Reports
  - link "Profile":
    - /url: /profile
    - img
    - text: Profile
- alert
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
  25 |     await page.goto("/login", { waitUntil: "networkidle" });
  26 |     await page.locator('input[type="email"]').fill("admin@trustlens.ai");
  27 |     await page.locator('input[type="password"]').fill("Admin@TrustLens2026!");
  28 |     await page.locator('form button[type="submit"]').click();
> 29 |     await expect(page).toHaveURL(/\/analyze\/text/);
     |                        ^ Error: expect(page).toHaveURL(expected) failed
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