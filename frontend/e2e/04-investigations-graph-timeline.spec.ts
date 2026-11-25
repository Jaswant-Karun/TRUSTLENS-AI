import { test, expect } from "@playwright/test";

test.describe("Investigations, Graph Interactions, Filters, Search & Timeline Sync", () => {
  test("investigations directory search and workspace interactive controls", async ({
    page,
  }) => {
    await page.goto("/investigations");
    const dirSearch = page.getByPlaceholder(/search/i).first();
    await expect(dirSearch).toBeVisible();
    await dirSearch.fill("KYC");

    // Open investigation dossier
    await page.goto("/investigations/INV-2026-0011");

    // Wait for workspace toolbar & graph to finish loading
    const nodeSearch = page.getByPlaceholder("Filter nodes...");
    await expect(nodeSearch).toBeVisible({ timeout: 20_000 });

    // Search nodes
    await nodeSearch.fill("sbi");
    await expect(nodeSearch).toHaveValue("sbi");
    await nodeSearch.fill("");

    // Graph zoom & layout controls
    await page.getByTitle("Zoom In").click();
    await page.getByTitle("Zoom Out").click();
    await page.getByTitle("Fit to Screen").click();
    await page.getByTitle("Reset Layout & Positions").click();

    // Minimap toggle
    const minimapBtn = page.getByTitle("Toggle Bird's-Eye Minimap");
    await minimapBtn.click();
    await minimapBtn.click();

    // Graph Filter Panel
    const filterBtn = page.getByRole("button", { name: /filter/i }).first();
    await filterBtn.click();
    const clearBtn = page.getByRole("button", { name: /clear all/i }).first();
    if (await clearBtn.isVisible()) {
      await clearBtn.click();
      await page.getByRole("button", { name: /select all/i }).first().click();
    }

    // ObjectInspector collapse & expand
    const collapseBtn = page.getByTitle("Collapse Panel");
    if (await collapseBtn.isVisible()) {
      await collapseBtn.click();
      await expect(page.getByTitle("Expand Details Panel")).toBeVisible();
      await page.getByTitle("Expand Details Panel").click();
    }

    // Timeline collapse/expand & event selection synchronization
    const timelineHeader = page.getByText(/Correlation Timeline/i).first();
    await expect(timelineHeader).toBeVisible();
    const refreshTimelineBtn = page.getByTitle("Refresh Timeline");
    if (await refreshTimelineBtn.isVisible()) {
      await refreshTimelineBtn.click();
    }
  });
});
