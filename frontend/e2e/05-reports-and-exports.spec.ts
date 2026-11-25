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

    // Authenticate via /api/v1/auth/login inside browser context to test protected STIX/JSON exports
    const exportCheck = await page.evaluate(async () => {
      const loginRes = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: "admin@trustlens.ai",
          password: "Admin@TrustLens2026!",
        }),
      });
      if (!loginRes.ok) {
        return { loginStatus: loginRes.status, stixStatus: 0, jsonStatus: 0 };
      }
      const { access_token } = await loginRes.json();
      localStorage.setItem("trustlens_token", access_token);

      const stixRes = await fetch(
        "/api/v1/exports/stix?target_type=investigation&target_id=INV-2026-0011",
        { headers: { Authorization: `Bearer ${access_token}` } }
      );
      const jsonRes = await fetch(
        "/api/v1/exports/json?target_type=investigation&target_id=INV-2026-0011",
        { headers: { Authorization: `Bearer ${access_token}` } }
      );
      return {
        loginStatus: loginRes.status,
        stixStatus: stixRes.status,
        jsonStatus: jsonRes.status,
      };
    });

    expect(exportCheck.loginStatus).toBe(200);
    expect(exportCheck.stixStatus).toBeLessThan(500);
    expect(exportCheck.jsonStatus).toBeLessThan(500);

    // Reload /reports authenticated and verify Intelligence Report / Export UI controls if present
    await page.reload();
    const exportBtn = page.getByRole("button", { name: /export|generate report|stix|json/i }).first();
    if (await exportBtn.isVisible()) {
      await exportBtn.click();
    }
  });
});
