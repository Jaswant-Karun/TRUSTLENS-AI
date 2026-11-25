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
        - button "Open primary radial navigation" [ref=e8] [cursor=pointer]
        - link "TRUSTLENS AI" [ref=e12] [cursor=pointer]:
          - /url: /
        - link "SIGN IN" [ref=e23] [cursor=pointer]:
          - /url: /login
    - main [ref=e24]:
      - generic [ref=e26]:
        - generic [ref=e27]:
          - heading "Sign In" [level=1] [ref=e35]
          - paragraph [ref=e36]: Access your TRUSTLENS AI intelligence workspace
        - generic [ref=e37]:
          - generic [ref=e38]:
            - generic [ref=e39]: Email Address
            - textbox "Email Address" [active] [ref=e41]:
              - /placeholder: analyst@organization.com
              - text: admin@trustlens.ai
          - generic [ref=e42]:
            - generic [ref=e43]:
              - generic [ref=e44]: Password
              - link "Forgot password?" [ref=e45] [cursor=pointer]:
                - /url: /forgot-password
            - generic [ref=e46]:
              - textbox "Password" [ref=e47]:
                - /placeholder: ••••••••••••
              - button "Show password" [ref=e48] [cursor=pointer]
          - button "SIGN IN TO TRUSTLENS" [ref=e52] [cursor=pointer]
        - paragraph [ref=e53]:
          - text: New to TRUSTLENS AI?
          - link "Create an account" [ref=e54] [cursor=pointer]:
            - /url: /register
    - contentinfo [ref=e55]:
      - generic [ref=e56]:
        - generic [ref=e57]: TRUSTLENS AI — Multilingual Digital Fraud Intelligence
        - generic [ref=e58]:
          - link "Scanner" [ref=e59] [cursor=pointer]:
            - /url: /analyze/text
          - link "Investigations" [ref=e60] [cursor=pointer]:
            - /url: /investigations
          - link "Reports" [ref=e61] [cursor=pointer]:
            - /url: /reports
    - navigation "Mobile primary navigation" [ref=e62]:
      - link "Text" [ref=e63] [cursor=pointer]:
        - /url: /analyze/text
      - link "URL" [ref=e67] [cursor=pointer]:
        - /url: /analyze/url
      - link "Image" [ref=e72] [cursor=pointer]:
        - /url: /analyze/image
      - link "Cases" [ref=e78] [cursor=pointer]:
        - /url: /investigations
      - link "Reports" [ref=e84] [cursor=pointer]:
        - /url: /reports
      - link "Profile" [ref=e88] [cursor=pointer]:
        - /url: /profile
  - alert [ref=e93]
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