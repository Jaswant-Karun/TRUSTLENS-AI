# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 02-auth-forms-and-profile.spec.ts >> Authentication, Form Validation, Profile & Notifications >> login, profile update, notification preferences, and logout persist properly
- Location: e2e\02-auth-forms-and-profile.spec.ts:22:3

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
      - generic [ref=e28]:
        - generic [ref=e29]:
          - heading "Sign In" [level=1] [ref=e37]
          - paragraph [ref=e38]: Access your TRUSTLENS AI intelligence workspace
        - generic [ref=e39]:
          - generic [ref=e40]:
            - generic [ref=e41]: Email Address
            - textbox "Email Address" [active] [ref=e43]:
              - /placeholder: analyst@organization.com
              - text: admin@trustlens.ai
          - generic [ref=e44]:
            - generic [ref=e45]:
              - generic [ref=e46]: Password
              - link "Forgot password?" [ref=e47] [cursor=pointer]:
                - /url: /forgot-password
            - generic [ref=e48]:
              - textbox "Password" [ref=e49]:
                - /placeholder: ••••••••••••
              - button "Show password" [ref=e50] [cursor=pointer]
          - button "SIGN IN TO TRUSTLENS" [ref=e54] [cursor=pointer]
        - paragraph [ref=e55]:
          - text: New to TRUSTLENS AI?
          - link "Create an account" [ref=e56] [cursor=pointer]:
            - /url: /register
    - contentinfo [ref=e57]:
      - generic [ref=e58]:
        - generic [ref=e59]: TRUSTLENS AI — Multilingual Digital Fraud Intelligence
        - generic [ref=e60]:
          - link "Scanner" [ref=e61] [cursor=pointer]:
            - /url: /analyze/text
          - link "Investigations" [ref=e62] [cursor=pointer]:
            - /url: /investigations
          - link "Reports" [ref=e63] [cursor=pointer]:
            - /url: /reports
  - alert [ref=e64]
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
  9  |     await expect(page.getByRole("alert")).toContainText(/valid email/i);
  10 | 
  11 |     // Invalid email format
  12 |     await page.getByLabel(/email/i).fill("not-an-email");
  13 |     await page.getByRole("button", { name: /sign in/i }).click();
  14 |     await expect(page.getByRole("alert")).toContainText(/valid email/i);
  15 | 
  16 |     // Valid email but empty password
  17 |     await page.getByLabel(/email/i).fill("admin@trustlens.ai");
  18 |     await page.getByRole("button", { name: /sign in/i }).click();
  19 |     await expect(page.getByRole("alert")).toContainText(/password/i);
  20 |   });
  21 | 
  22 |   test("login, profile update, notification preferences, and logout persist properly", async ({
  23 |     page,
  24 |   }) => {
  25 |     await page.goto("/login");
  26 |     await page.getByLabel(/email/i).fill("admin@trustlens.ai");
> 27 |     await page.getByLabel(/password/i).fill("Admin@TrustLens2026!");
     |                                        ^ Error: locator.fill: Error: strict mode violation: getByLabel(/password/i) resolved to 2 elements:
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
  51 |     await page.reload();
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