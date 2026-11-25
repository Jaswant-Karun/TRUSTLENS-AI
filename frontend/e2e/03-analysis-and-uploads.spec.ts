import { test, expect } from "@playwright/test";

// Minimal genuine 1x1 PNG (67 bytes) for real magic-byte upload testing
const VALID_PNG_BUFFER = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
  "base64"
);

test.describe("Message Analysis, URL Analysis & Image Upload Validation", () => {
  test("message analysis validates empty input and scans scam text", async ({ page }) => {
    await page.goto("/analyze/text");

    const textarea = page.locator("textarea").first();
    await expect(textarea).toBeVisible();

    // Empty scan validation
    await page.getByRole("button", { name: /analyze message|scan message|run analysis/i }).first().click();
    await expect(page.getByText(/enter|provide|empty|required/i).first()).toBeVisible();

    // Real scam message analysis
    await textarea.fill(
      "Aapka SBI khata turant band ho jayega. Urgent verify karein: http://192.168.1.50/sbi-kyc/update.php"
    );
    await page.getByRole("button", { name: /analyze message|scan message|run analysis/i }).first().click();

    await expect(page.getByText(/risk score|threat|scam|phishing|high|critical/i).first()).toBeVisible({
      timeout: 20_000,
    });
  });

  test("url analysis validates malformed URLs and inspects phishing URL", async ({ page }) => {
    await page.goto("/analyze/url");

    const urlInput = page.locator('input[type="text"], input[type="url"]').first();
    await urlInput.fill("bad url with spaces");
    await page.getByRole("button", { name: /inspect url|analyze url|scan url/i }).first().click();
    await expect(page.getByText(/valid URL|without spaces/i)).toBeVisible();

    await urlInput.fill("http://secure-login-hdfcbank-account-update.xyz/login.php");
    await page.getByRole("button", { name: /inspect url|analyze url|scan url/i }).first().click();

    await expect(page.getByText(/risk score|phishing|suspicious|threat|high|critical/i).first()).toBeVisible({
      timeout: 20_000,
    });
  });

  test("image upload rejects spoofed magic bytes and accepts valid PNG", async ({ page }) => {
    await page.goto("/analyze/image");

    const fileInput = page.locator('input[type="file"]');

    // 1. Reject spoofed .png containing plain text
    await fileInput.setInputFiles({
      name: "spoofed.png",
      mimeType: "image/png",
      buffer: Buffer.from("NOT_A_REAL_PNG_FILE_CONTENT"),
    });
    await expect(page.getByText(/Invalid image file signature/i)).toBeVisible();

    // 2. Accept genuine PNG magic-byte file and run OCR scan
    await fileInput.setInputFiles({
      name: "valid_test.png",
      mimeType: "image/png",
      buffer: VALID_PNG_BUFFER,
    });
    await expect(page.getByText("valid_test.png")).toBeVisible();

    await page.getByRole("button", { name: /analyze screenshot|scan screenshot|extract/i }).first().click();
    // 1x1 blank PNG returns either insufficient-evidence or OCR response panel without crashing
    await expect(
      page.getByText(/insufficient|ocr|extracted|risk|analyzed|no readable text/i).first()
    ).toBeVisible({ timeout: 25_000 });
  });
});
