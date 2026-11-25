# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 01-navigation-and-radial.spec.ts >> Navigation, Radial Wheel & All Routes >> radial navigation opens, navigates to target route, and closes on Escape
- Location: e2e\01-navigation-and-radial.spec.ts:29:3

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('menuitem', { name: /message scanner/i }).first()
    - locator resolved to <button type="button" role="menuitem" title="Message Scanner" aria-label="Message Scanner" class="absolute z-10 flex flex-col items-center justify-center w-16 h-16 sm:w-20 sm:h-20 rounded-full text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF3D70] transition-transform duration-150 hover:scale-105">…</button>
  - attempting click action
    - waiting for element to be visible, enabled and stable
    - element is not stable
  - retrying click action
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling
    - element is outside of the viewport
  - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - element is outside of the viewport
    - retrying click action
      - waiting 100ms
    65 × waiting for element to be visible, enabled and stable
       - element is visible, enabled and stable
       - scrolling into view if needed
       - done scrolling
       - element is outside of the viewport
     - retrying click action
       - waiting 500ms
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling

```

# Page snapshot

```yaml
- generic [ref=e1]:
  - generic [ref=e3]:
    - banner [ref=e4]:
      - generic [ref=e5]:
        - generic [ref=e6]:
          - generic [ref=e7]:
            - button "Open primary radial navigation" [expanded] [ref=e8] [cursor=pointer]
            - menu "TRUSTLENS AI Primary Navigation" [ref=e14]:
              - menuitem "Home" [active] [ref=e26] [cursor=pointer]:
                - generic [ref=e31]: HOME
              - menuitem "Message Scanner" [ref=e32] [cursor=pointer]:
                - generic [ref=e36]: MESSAGES
              - menuitem "URL Shield" [ref=e37] [cursor=pointer]:
                - generic [ref=e42]: URL SHIELD
              - menuitem "Screenshot Analyzer" [ref=e43] [cursor=pointer]:
                - generic [ref=e52]: OCR SCAN
              - menuitem "Threat Intelligence" [ref=e53] [cursor=pointer]:
                - generic [ref=e57]: THREATS
              - menuitem "Investigations" [ref=e58] [cursor=pointer]:
                - generic [ref=e64]: CASES
              - menuitem "Reports" [ref=e65] [cursor=pointer]:
                - generic [ref=e70]: REPORTS
              - menuitem "Profile" [ref=e71] [cursor=pointer]:
                - generic [ref=e76]: PROFILE
              - button "Close radial navigation" [ref=e77] [cursor=pointer]
          - generic [ref=e81]: NAV WHEEL
        - link "TRUSTLENS AI" [ref=e82] [cursor=pointer]:
          - /url: /
        - generic [ref=e92]:
          - link "SIGN IN" [ref=e93] [cursor=pointer]:
            - /url: /login
          - link "GET STARTED" [ref=e94] [cursor=pointer]:
            - /url: /register
    - main [ref=e95]:
      - generic [ref=e96]:
        - generic [ref=e97]:
          - generic [ref=e99]: "ML CORE: OPERATIONAL"
          - generic [ref=e100]: "|"
          - generic [ref=e101]: ZERO-HOP URL SAFETY
        - generic [ref=e102]:
          - generic [ref=e103]: TRUSTLENS AI
          - heading "INTELLIGENCE THAT STOPS DIGITAL FRAUD." [level=1] [ref=e113]
          - paragraph [ref=e114]: Detect suspicious messages, malicious URLs and emerging digital fraud campaigns using intelligent multilingual analysis and real-world threat intelligence.
          - generic [ref=e115]:
            - link [ref=e116] [cursor=pointer]:
              - /url: /register
              - button "GET STARTED" [ref=e117]
            - link [ref=e120] [cursor=pointer]:
              - /url: /login
              - button "SIGN IN" [ref=e121]
        - region "Interactive Radial Navigation" [ref=e122]:
          - button "Expand TRUSTLENS AI radial navigation" [ref=e127] [cursor=pointer]:
            - generic [ref=e131]: EXPLORE
            - generic [ref=e132]: CLICK HUB
          - paragraph [ref=e133]: CLICK CENTER HUB TO ACCESS WORKFLOWS • ESC OR CLICK OUTSIDE TO CLOSE
        - region "Core Capabilities" [ref=e134]:
          - generic [ref=e135]:
            - heading "Multilingual Message Analysis" [level=2] [ref=e139]
            - paragraph [ref=e140]: Evaluates SMS, WhatsApp, and email text across English, Hindi (Devanagari), and Hinglish with calibrated risk scores and social-engineering tactic attribution.
          - generic [ref=e141]:
            - heading "Zero-Hop URL Shield" [level=2] [ref=e146]
            - paragraph [ref=e147]: Inspects 16 lexical and structural URL features using XGBoost and SHAP without ever opening, fetching, or executing the submitted link.
          - generic [ref=e148]:
            - heading "Screenshot OCR & Case Trails" [level=2] [ref=e157]
            - paragraph [ref=e158]: Validates PNG, JPEG, and WebP screenshots, extracts embedded text, and lets authenticated users attach evidence to persistent investigations.
        - generic [ref=e160]:
          - paragraph [ref=e165]: "Security & Privacy Guarantees: Submitted URLs are never visited or executed. Private investigations are isolated per account via JWT/RBAC. Campaign clustering reflects linguistic and indicator similarity, not legal proof of common criminal origin."
          - generic [ref=e166]: FASTAPI + ML CORE
    - contentinfo [ref=e171]:
      - generic [ref=e172]:
        - generic [ref=e173]: TRUSTLENS AI — Multilingual Digital Fraud Intelligence
        - generic [ref=e174]:
          - link "Scanner" [ref=e175] [cursor=pointer]:
            - /url: /analyze/text
          - link "Investigations" [ref=e176] [cursor=pointer]:
            - /url: /investigations
          - link "Reports" [ref=e177] [cursor=pointer]:
            - /url: /reports
  - alert [ref=e178]
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
  39 |     // Verify radial sector menu items appear and click Message Scanner
  40 |     const messageNav = page.getByRole("menuitem", { name: /message scanner/i }).first();
  41 |     await expect(messageNav).toBeVisible();
> 42 |     await messageNav.click();
     |                      ^ Error: locator.click: Test timeout of 45000ms exceeded.
  43 |     await expect(page).toHaveURL(/\/analyze\/text/);
  44 | 
  45 |     // Re-open radial nav and verify Escape closes it
  46 |     await launcher.click();
  47 |     await expect(page.getByRole("menuitem", { name: /url shield/i }).first()).toBeVisible();
  48 |     await page.keyboard.press("Escape");
  49 |     await expect(page.getByRole("menuitem", { name: /url shield/i }).first()).toBeHidden();
  50 |   });
  51 | 
  52 |   test("all navigation routes render without uncaught errors", async ({ page }) => {
  53 |     test.setTimeout(90_000);
  54 |     const pageErrors: string[] = [];
  55 |     page.on("pageerror", (err) => pageErrors.push(`${page.url()}: ${err.message}`));
  56 | 
  57 |     for (const route of ALL_ROUTES) {
  58 |       const resp = await page.goto(route, { waitUntil: "domcontentloaded" });
  59 |       expect(resp?.status() ?? 200, `Route ${route} returned >= 500`).toBeLessThan(500);
  60 |       await expect(page.locator("body")).not.toBeEmpty();
  61 |     }
  62 | 
  63 |     expect(pageErrors, `Uncaught page errors: ${pageErrors.join("; ")}`).toEqual([]);
  64 |   });
  65 | 
  66 |   test("mobile bottom navigation bar works on mobile viewport", async ({
  67 |     page,
  68 |     isMobile,
  69 |   }) => {
  70 |     test.skip(!isMobile, "Mobile bottom nav bar is mobile-only");
  71 |     await page.goto("/analyze/text");
  72 |     const mobileNav = page.getByRole("navigation", { name: "Mobile primary navigation" });
  73 |     await expect(mobileNav).toBeVisible();
  74 | 
  75 |     await mobileNav.getByRole("link", { name: "URL" }).click();
  76 |     await expect(page).toHaveURL(/\/analyze\/url/);
  77 | 
  78 |     await mobileNav.getByRole("link", { name: "Image" }).click();
  79 |     await expect(page).toHaveURL(/\/analyze\/image/);
  80 | 
  81 |     await mobileNav.getByRole("link", { name: "Reports" }).click();
  82 |     await expect(page).toHaveURL(/\/reports/);
  83 |   });
  84 | });
  85 | 
```