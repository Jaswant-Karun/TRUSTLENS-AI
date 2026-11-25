import { test, expect } from "@playwright/test";

const ALL_ROUTES = [
  "/",
  "/login",
  "/register",
  "/forgot-password",
  "/analyze/text",
  "/analyze/url",
  "/analyze/image",
  "/investigation",
  "/investigations",
  "/investigations/INV-2026-0011",
  "/intelligence/campaigns",
  "/intelligence/tactics",
  "/intelligence/threats",
  "/threat-library",
  "/reports",
  "/analytics",
  "/models",
  "/methodology",
  "/privacy-policy",
  "/settings",
  "/profile",
  "/history",
];

test.describe("Navigation, Radial Wheel & All Routes", () => {
  test("radial navigation opens, navigates to target route, and closes on Escape", async ({
    page,
  }) => {
    await page.goto("/");

    // Open radial navigation launcher in ProductHeader
    const launcher = page.locator("header button").first();
    await expect(launcher).toBeVisible();
    await launcher.click();

    // Verify radial sector items appear and click Message Scanner
    const messageNav = page.getByRole("button", { name: /message scanner|messages/i }).first();
    await expect(messageNav).toBeVisible();
    await messageNav.click();
    await expect(page).toHaveURL(/\/analyze\/text/);

    // Re-open radial nav and verify Escape closes it
    await launcher.click();
    await expect(page.getByRole("button", { name: /url shield/i }).first()).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.getByRole("button", { name: /url shield/i }).first()).toBeHidden();
  });

  test("all navigation routes render without uncaught errors", async ({ page }) => {
    const pageErrors: string[] = [];
    page.on("pageerror", (err) => pageErrors.push(`${page.url()}: ${err.message}`));

    for (const route of ALL_ROUTES) {
      const resp = await page.goto(route, { waitUntil: "domcontentloaded" });
      expect(resp?.status() ?? 200, `Route ${route} returned >= 500`).toBeLessThan(500);
      await expect(page.locator("body")).not.toBeEmpty();
    }

    expect(pageErrors, `Uncaught page errors: ${pageErrors.join("; ")}`).toEqual([]);
  });

  test("mobile bottom navigation bar works on mobile viewport", async ({
    page,
    isMobile,
  }) => {
    test.skip(!isMobile, "Mobile bottom nav bar is mobile-only");
    await page.goto("/analyze/text");
    const mobileNav = page.getByRole("navigation", { name: "Mobile primary navigation" });
    await expect(mobileNav).toBeVisible();

    await mobileNav.getByRole("link", { name: "URL" }).click();
    await expect(page).toHaveURL(/\/analyze\/url/);

    await mobileNav.getByRole("link", { name: "Image" }).click();
    await expect(page).toHaveURL(/\/analyze\/image/);

    await mobileNav.getByRole("link", { name: "Reports" }).click();
    await expect(page).toHaveURL(/\/reports/);
  });
});
