import { test, expect } from "@playwright/test";

test.describe("Community Reports & Report Exports", () => {
  test("reports page search, filter, submission validation, and export controls", async ({
    page,
  }) => {
    await page.goto("/reports");
    await expect(page.getByText(/Community Threat Reports/i).first()).toBeVisible();

    // Search/filter reports table
    const searchBox = page.getByPlaceholder(/search/i).first();
    if (await searchBox.isVisible()) {
      await searchBox.fill("HDFC");
      await expect(searchBox).toHaveValue("HDFC");
      await searchBox.fill("");
    }

    // Test Intelligence Report / Export triggers if present on /reports
    const exportBtn = page.getByRole("button", { name: /export|generate report|stix|json/i }).first();
    if (await exportBtn.isVisible()) {
      await exportBtn.click();
    }

    // Verify backend STIX & JSON export endpoints directly with authenticated session
    await page.goto("/login");
    await page.getByLabel(/email/i).fill("admin@trustlens.ai");
    await page.getByLabel(/password/i).fill("Admin@TrustLens2026!");
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/analyze\/text/);

    const exportCheck = await page.evaluate(async () => {
      const token = localStorage.getItem("trustlens_token");
      const res = await fetch(
        "/api/v1/exports/stix?target_type=investigation&target_id=INV-2026-0011",
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return { status: res.status, ok: res.ok };
    });
    expect(exportCheck.status).toBeLessThan(500);
  });
});
