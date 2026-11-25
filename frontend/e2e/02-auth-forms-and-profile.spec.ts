import { test, expect } from "@playwright/test";

test.describe("Authentication, Form Validation, Profile & Notifications", () => {
  test("login form validates invalid email and empty password", async ({ page }) => {
    await page.goto("/login");

    // Empty submit
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page.getByText(/Please enter a valid email address/i)).toBeVisible();

    // Invalid email format
    await page.getByLabel(/email/i).fill("not-an-email");
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page.getByText(/Please enter a valid email address/i)).toBeVisible();

    // Valid email but empty password
    await page.getByLabel(/email/i).fill("admin@trustlens.ai");
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page.getByText(/Please enter your password/i)).toBeVisible();
  });

  test("login, profile update, notification preferences, and logout persist properly", async ({
    page,
  }) => {
    await page.goto("/login");
    await page.getByLabel(/email/i).fill("admin@trustlens.ai");
    await page.locator('input[type="password"]').fill("Admin@TrustLens2026!");
    await page.getByRole("button", { name: /sign in/i }).click();

    await expect(page).toHaveURL(/\/analyze\/text/);
    const token = await page.evaluate(() => localStorage.getItem("trustlens_token"));
    expect(token).toBeTruthy();

    // Verify /history is unlocked once authenticated
    await page.goto("/history");
    await expect(page.getByText(/Authentication Required/i)).toHaveCount(0);

    // Profile management + Notification preferences
    await page.goto("/profile");
    const nameInput = page.locator("#profile-name");
    await expect(nameInput).toBeVisible();
    const originalName = await nameInput.inputValue();

    await nameInput.fill("TrustLens QA Analyst");
    const threatOptIn = page.getByLabel(/Consented emerging scam campaign advisories/i);
    await threatOptIn.check();
    await page.getByRole("button", { name: /save profile/i }).click();
    await expect(page.getByText(/Profile and preferences saved/i)).toBeVisible();

    // Reload and verify persisted in backend
    await page.reload();
    await expect(page.locator("#profile-name")).toHaveValue("TrustLens QA Analyst");
    await expect(
      page.getByLabel(/Consented emerging scam campaign advisories/i)
    ).toBeChecked();

    // Restore original name
    if (originalName) {
      await page.locator("#profile-name").fill(originalName);
      await page.getByRole("button", { name: /save profile/i }).click();
    }

    // Logout clears token and re-locks /history
    await page.getByRole("button", { name: /sign out/i }).click();
    await expect.poll(async () =>
      page.evaluate(() => localStorage.getItem("trustlens_token"))
    ).toBeNull();

    await page.goto("/history");
    await expect(page.getByText(/Authentication Required/i)).toBeVisible();
  });
});
