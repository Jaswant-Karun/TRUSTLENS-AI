# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 02-auth-forms-and-profile.spec.ts >> Authentication, Form Validation, Profile & Notifications >> login, profile update, notification preferences, and logout persist properly
- Location: e2e\02-auth-forms-and-profile.spec.ts:22:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('#profile-name')
Expected: visible
Timeout: 12000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" locator('#profile-name') with timeout 12000ms
  - waiting for locator('#profile-name')

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
- main:
  - img
  - heading "Authentication Required" [level=1]
  - paragraph: Sign in to view and manage your TRUSTLENS AI profile, preferences, and active sessions.
  - link "SIGN IN":
    - /url: /login?next=/profile
    - button "SIGN IN"
  - link "SIGN UP":
    - /url: /register
    - button "SIGN UP"
- contentinfo:
  - text: TRUSTLENS AI — Multilingual Digital Fraud Intelligence
  - link "Scanner":
    - /url: /analyze/text
  - link "Investigations":
    - /url: /investigations
  - link "Reports":
    - /url: /reports
- alert
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
> 41 |     await expect(nameInput).toBeVisible();
     |                             ^ Error: expect(locator).toBeVisible() failed
  42 |     const originalName = await nameInput.inputValue();
  43 | 
  44 |     await nameInput.fill("TrustLens QA Analyst");
  45 |     const threatOptIn = page.getByLabel(/Consented emerging scam campaign advisories/i);
  46 |     await threatOptIn.check();
  47 |     await page.getByRole("button", { name: /save profile/i }).click();
  48 |     await expect(page.getByText(/Profile and preferences saved/i)).toBeVisible();
  49 | 
  50 |     // Reload and verify persisted in backend
  51 |     await page.reload({ waitUntil: "domcontentloaded" });
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