# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 02-auth-forms-and-profile.spec.ts >> Authentication, Form Validation, Profile & Notifications >> login, profile update, notification preferences, and logout persist properly
- Location: e2e\02-auth-forms-and-profile.spec.ts:22:3

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: page.reload: Test timeout of 45000ms exceeded.
Call log:
  - waiting for navigation until "load"
    - navigated to "http://127.0.0.1:3000/profile"

```

# Page snapshot

```yaml
- generic [ref=f3e3]:
  - banner [ref=f3e4]:
    - generic [ref=f3e5]:
      - button "Open primary radial navigation" [ref=f3e8] [cursor=pointer]
      - link "TRUSTLENS AI" [ref=f3e12] [cursor=pointer]:
        - /url: /
  - main [ref=f3e24]:
    - generic [ref=f3e25]: Loading authenticated profile...
  - contentinfo [ref=f3e26]:
    - generic [ref=f3e27]:
      - generic [ref=f3e28]: TRUSTLENS AI — Multilingual Digital Fraud Intelligence
      - generic [ref=f3e29]:
        - link "Scanner" [ref=f3e30] [cursor=pointer]:
          - /url: /analyze/text
        - link "Investigations" [ref=f3e31] [cursor=pointer]:
          - /url: /investigations
        - link "Reports" [ref=f3e32] [cursor=pointer]:
          - /url: /reports
  - navigation "Mobile primary navigation" [ref=f3e33]:
    - link "Text" [ref=f3e34] [cursor=pointer]:
      - /url: /analyze/text
    - link "URL" [ref=f3e38] [cursor=pointer]:
      - /url: /analyze/url
    - link "Image" [ref=f3e43] [cursor=pointer]:
      - /url: /analyze/image
    - link "Cases" [ref=f3e49] [cursor=pointer]:
      - /url: /investigations
    - link "Reports" [ref=f3e55] [cursor=pointer]:
      - /url: /reports
    - link "Profile" [ref=f3e59] [cursor=pointer]:
      - /url: /profile
```

# Test source

```ts
  1  | import { test, expect } from "@playwright/test";
  2  | 
  3  | test.describe("Authentication, Form Validation, Profile & Notifications", () => {
  4  |   test("login form validates invalid email and empty password", async ({ page }) => {
  5  |     await page.goto("/login");
  6  | 
  7  |     // Empty submit
  8  |     await page.getByRole("button", { name: /sign in/i }).click();
  9  |     await expect(page.getByText(/Please enter a valid email address/i)).toBeVisible();
  10 | 
  11 |     // Invalid email format
  12 |     await page.getByLabel(/email/i).fill("not-an-email");
  13 |     await page.getByRole("button", { name: /sign in/i }).click();
  14 |     await expect(page.getByText(/Please enter a valid email address/i)).toBeVisible();
  15 | 
  16 |     // Valid email but empty password
  17 |     await page.getByLabel(/email/i).fill("admin@trustlens.ai");
  18 |     await page.getByRole("button", { name: /sign in/i }).click();
  19 |     await expect(page.getByText(/Please enter your password/i)).toBeVisible();
  20 |   });
  21 | 
  22 |   test("login, profile update, notification preferences, and logout persist properly", async ({
  23 |     page,
  24 |   }) => {
  25 |     await page.goto("/login");
  26 |     await page.getByLabel(/email/i).fill("admin@trustlens.ai");
  27 |     await page.locator('input[type="password"]').fill("Admin@TrustLens2026!");
  28 |     await page.getByRole("button", { name: /sign in/i }).click();
  29 | 
  30 |     await expect(page).toHaveURL(/\/analyze\/text/);
  31 |     const token = await page.evaluate(() => localStorage.getItem("trustlens_token"));
  32 |     expect(token).toBeTruthy();
  33 | 
  34 |     // Verify /history is unlocked once authenticated
  35 |     await page.goto("/history");
  36 |     await expect(page.getByText(/Authentication Required/i)).toHaveCount(0);
  37 | 
  38 |     // Profile management + Notification preferences
  39 |     await page.goto("/profile");
  40 |     const nameInput = page.locator("#profile-name");
  41 |     await expect(nameInput).toBeVisible();
  42 |     const originalName = await nameInput.inputValue();
  43 | 
  44 |     await nameInput.fill("TrustLens QA Analyst");
  45 |     const threatOptIn = page.getByLabel(/Consented emerging scam campaign advisories/i);
  46 |     await threatOptIn.check();
  47 |     await page.getByRole("button", { name: /save profile/i }).click();
  48 |     await expect(page.getByText(/Profile and preferences saved/i)).toBeVisible();
  49 | 
  50 |     // Reload and verify persisted in backend
> 51 |     await page.reload();
     |                ^ Error: page.reload: Test timeout of 45000ms exceeded.
  52 |     await expect(page.locator("#profile-name")).toHaveValue("TrustLens QA Analyst");
  53 |     await expect(
  54 |       page.getByLabel(/Consented emerging scam campaign advisories/i)
  55 |     ).toBeChecked();
  56 | 
  57 |     // Restore original name
  58 |     if (originalName) {
  59 |       await page.locator("#profile-name").fill(originalName);
  60 |       await page.getByRole("button", { name: /save profile/i }).click();
  61 |     }
  62 | 
  63 |     // Logout clears token and re-locks /history
  64 |     await page.getByRole("button", { name: /sign out/i }).click();
  65 |     await expect.poll(async () =>
  66 |       page.evaluate(() => localStorage.getItem("trustlens_token"))
  67 |     ).toBeNull();
  68 | 
  69 |     await page.goto("/history");
  70 |     await expect(page.getByText(/Authentication Required/i)).toBeVisible();
  71 |   });
  72 | });
  73 | 
```