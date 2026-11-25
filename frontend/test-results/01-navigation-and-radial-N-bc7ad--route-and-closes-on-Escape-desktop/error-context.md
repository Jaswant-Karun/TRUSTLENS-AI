# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 01-navigation-and-radial.spec.ts >> Navigation, Radial Wheel & All Routes >> radial navigation opens, navigates to target route, and closes on Escape
- Location: e2e\01-navigation-and-radial.spec.ts:29:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('button', { name: /message scanner|messages/i }).first()
Expected: visible
Timeout: 12000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByRole('button', { name: /message scanner|messages/i }).first() with timeout 12000ms
  - waiting for getByRole('button', { name: /message scanner|messages/i }).first()

```

```yaml
- banner:
  - button "Open primary radial navigation" [expanded]:
    - img
  - menu "TRUSTLENS AI Primary Navigation":
    - menuitem "Home":
      - img
      - text: HOME
    - menuitem "Message Scanner":
      - img
      - text: MESSAGES
    - menuitem "URL Shield":
      - img
      - text: URL SHIELD
    - menuitem "Screenshot Analyzer":
      - img
      - text: OCR SCAN
    - menuitem "Threat Intelligence":
      - img
      - text: THREATS
    - menuitem "Investigations":
      - img
      - text: CASES
    - menuitem "Reports":
      - img
      - text: REPORTS
    - menuitem "Profile":
      - img
      - text: PROFILE
    - button "Close radial navigation":
      - img
  - text: NAV WHEEL
  - link "TRUSTLENS AI":
    - /url: /
  - link "SIGN IN":
    - /url: /login
  - link "GET STARTED":
    - /url: /register
- main:
  - text: "ML CORE: OPERATIONAL | ZERO-HOP URL SAFETY TRUSTLENS AI"
  - heading "INTELLIGENCE THAT STOPS DIGITAL FRAUD." [level=1]
  - paragraph: Detect suspicious messages, malicious URLs and emerging digital fraud campaigns using intelligent multilingual analysis and real-world threat intelligence.
  - link "GET STARTED":
    - /url: /register
    - button "GET STARTED":
      - text: GET STARTED
      - img
  - link "SIGN IN":
    - /url: /login
    - button "SIGN IN"
  - region "Interactive Radial Navigation":
    - button "Expand TRUSTLENS AI radial navigation":
      - img
      - text: EXPLORE CLICK HUB
    - paragraph: CLICK CENTER HUB TO ACCESS WORKFLOWS • ESC OR CLICK OUTSIDE TO CLOSE
  - region "Core Capabilities":
    - img
    - heading "Multilingual Message Analysis" [level=2]
    - paragraph: Evaluates SMS, WhatsApp, and email text across English, Hindi (Devanagari), and Hinglish with calibrated risk scores and social-engineering tactic attribution.
    - img
    - heading "Zero-Hop URL Shield" [level=2]
    - paragraph: Inspects 16 lexical and structural URL features using XGBoost and SHAP without ever opening, fetching, or executing the submitted link.
    - img
    - heading "Screenshot OCR & Case Trails" [level=2]
    - paragraph: Validates PNG, JPEG, and WebP screenshots, extracts embedded text, and lets authenticated users attach evidence to persistent investigations.
  - img
  - paragraph: "Security & Privacy Guarantees: Submitted URLs are never visited or executed. Private investigations are isolated per account via JWT/RBAC. Campaign clustering reflects linguistic and indicator similarity, not legal proof of common criminal origin."
  - img
  - text: FASTAPI + ML CORE
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
  3  | const ALL_ROUTES = [
  4  |   "/",
  5  |   "/login",
  6  |   "/register",
  7  |   "/forgot-password",
  8  |   "/analyze/text",
  9  |   "/analyze/url",
  10 |   "/analyze/image",
  11 |   "/investigation",
  12 |   "/investigations",
  13 |   "/investigations/INV-2026-0011",
  14 |   "/intelligence/campaigns",
  15 |   "/intelligence/tactics",
  16 |   "/intelligence/threats",
  17 |   "/threat-library",
  18 |   "/reports",
  19 |   "/analytics",
  20 |   "/models",
  21 |   "/methodology",
  22 |   "/privacy-policy",
  23 |   "/settings",
  24 |   "/profile",
  25 |   "/history",
  26 | ];
  27 | 
  28 | test.describe("Navigation, Radial Wheel & All Routes", () => {
  29 |   test("radial navigation opens, navigates to target route, and closes on Escape", async ({
  30 |     page,
  31 |   }) => {
  32 |     await page.goto("/");
  33 | 
  34 |     // Open radial navigation launcher in ProductHeader
  35 |     const launcher = page.locator("header button").first();
  36 |     await expect(launcher).toBeVisible();
  37 |     await launcher.click();
  38 | 
  39 |     // Verify radial sector items appear and click Message Scanner
  40 |     const messageNav = page.getByRole("button", { name: /message scanner|messages/i }).first();
> 41 |     await expect(messageNav).toBeVisible();
     |                              ^ Error: expect(locator).toBeVisible() failed
  42 |     await messageNav.click();
  43 |     await expect(page).toHaveURL(/\/analyze\/text/);
  44 | 
  45 |     // Re-open radial nav and verify Escape closes it
  46 |     await launcher.click();
  47 |     await expect(page.getByRole("button", { name: /url shield/i }).first()).toBeVisible();
  48 |     await page.keyboard.press("Escape");
  49 |     await expect(page.getByRole("button", { name: /url shield/i }).first()).toBeHidden();
  50 |   });
  51 | 
  52 |   test("all navigation routes render without uncaught errors", async ({ page }) => {
  53 |     const pageErrors: string[] = [];
  54 |     page.on("pageerror", (err) => pageErrors.push(`${page.url()}: ${err.message}`));
  55 | 
  56 |     for (const route of ALL_ROUTES) {
  57 |       const resp = await page.goto(route, { waitUntil: "domcontentloaded" });
  58 |       expect(resp?.status() ?? 200, `Route ${route} returned >= 500`).toBeLessThan(500);
  59 |       await expect(page.locator("body")).not.toBeEmpty();
  60 |     }
  61 | 
  62 |     expect(pageErrors, `Uncaught page errors: ${pageErrors.join("; ")}`).toEqual([]);
  63 |   });
  64 | 
  65 |   test("mobile bottom navigation bar works on mobile viewport", async ({
  66 |     page,
  67 |     isMobile,
  68 |   }) => {
  69 |     test.skip(!isMobile, "Mobile bottom nav bar is mobile-only");
  70 |     await page.goto("/analyze/text");
  71 |     const mobileNav = page.getByRole("navigation", { name: "Mobile primary navigation" });
  72 |     await expect(mobileNav).toBeVisible();
  73 | 
  74 |     await mobileNav.getByRole("link", { name: "URL" }).click();
  75 |     await expect(page).toHaveURL(/\/analyze\/url/);
  76 | 
  77 |     await mobileNav.getByRole("link", { name: "Image" }).click();
  78 |     await expect(page).toHaveURL(/\/analyze\/image/);
  79 | 
  80 |     await mobileNav.getByRole("link", { name: "Reports" }).click();
  81 |     await expect(page).toHaveURL(/\/reports/);
  82 |   });
  83 | });
  84 | 
```