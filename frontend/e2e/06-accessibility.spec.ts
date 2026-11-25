import { test, expect } from "@playwright/test";
import path from "path";

const AXE_PATH = path.resolve(__dirname, "../node_modules/axe-core/axe.min.js");

const A11Y_ROUTES = [
  "/",
  "/login",
  "/analyze/text",
  "/analyze/url",
  "/analyze/image",
  "/methodology",
  "/privacy-policy",
  "/reports",
  "/profile",
];

test.describe("WCAG Accessibility Audit (axe-core)", () => {
  test("core routes have zero critical WCAG violations", async ({ page, browserName }, testInfo) => {
    // Run on desktop project to avoid redundant 3x execution while testing full layout
    test.skip(testInfo.project.name !== "desktop", "Run axe-core audit once on desktop");
    test.setTimeout(90_000);

    const criticalViolations: Array<{ route: string; id: string; impact: string; nodes: number }> = [];

    for (const route of A11Y_ROUTES) {
      await page.goto(route, { waitUntil: "domcontentloaded" });
      await page.addScriptTag({ path: AXE_PATH });
      const results = await page.evaluate(async () => {
        return await (window as any).axe.run(document, {
          runOnly: { type: "tag", values: ["wcag2a", "wcag2aa"] },
        });
      });
      for (const v of results.violations || []) {
        if (v.impact === "critical") {
          criticalViolations.push({
            route,
            id: v.id,
            impact: v.impact,
            nodes: v.nodes?.length || 0,
          });
        }
      }
    }

    expect(
      criticalViolations,
      `Critical WCAG violations: ${JSON.stringify(criticalViolations)}`
    ).toEqual([]);
  });
});
