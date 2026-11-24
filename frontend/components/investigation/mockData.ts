/**
 * TRUSTLENS AI - Development-Only Preview Fixture
 *
 * PROVENANCE & CLASSIFICATION:
 * - DATA CLASSIFICATION: Synthetic Demonstration Example
 * - PURPOSE: Isolated development visual testing and component preview ONLY.
 * - WARNING: DO NOT import into production data paths or present as real threat intelligence.
 * - Live production workspaces fetch exclusively from MongoDB via /api/v1/investigations.
 */

import { InvestigationData } from "./types";

export const devOnlyDemonstrationFixture: InvestigationData = {
  id: "DEV-ONLY-DEMO-KYC-11",
  title: "[DEMO ONLY] Illustrative Banking KYC Smishing Preview",
  description:
    "ISOLATED TEST FIXTURE: Demonstrates UI presentation of multi-label scam classifications, graph layouts, and timeline tracks. Not verified real threat intelligence.",
  severity: "critical",
  visibility: "Organization",
  status: "Active",
  created: {
    date: "Test Datum",
    author: "Test Lead (RS)",
    relative: "Demonstration",
  },
  lastModified: {
    date: "Test Datum",
    author: "Test Lead (RS)",
    relative: "Demonstration",
  },
  objectsCount: 10,
  tasksCount: 2,
  commentsCount: 0,
  sources: ["Isolated Demo Mock"],
  tags: ["demo_fixture", "visual_preview_only"],
  attributes: {
    "Data Classification": "Isolated Synthetic Demo Fixture",
    "Production Source": "None - Do Not Treat as Live Intelligence",
  },
  nodes: [
    {
      id: "demo-node-hub",
      label: "Synthetic Campaign Hub #11",
      type: "campaign_cluster",
      severity: "critical",
      isCentral: true,
      x: 0,
      y: 0,
      radius: 40,
      metadata: {
        description: "Synthetic central cluster node for layout verification.",
        confidence: 0.99,
        riskScore: 0.95,
      },
    },
    {
      id: "demo-node-url",
      label: "http://demo-phish-portal.example",
      type: "url",
      severity: "critical",
      x: -160,
      y: -140,
      metadata: {
        description: "Synthetic example URL node.",
      },
    },
  ],
  edges: [
    {
      id: "demo-edge-1",
      source: "demo-node-url",
      target: "demo-node-hub",
      label: "contains url",
      relationship: "contains_url",
      weight: 1.0,
    },
  ],
  timeline: [
    {
      id: "demo-t-1",
      title: "Synthetic Event Preview",
      timestamp: "2026-11-24T00:00:00Z",
      dateLabel: "Demo Date",
      track: "situation",
      severity: "critical",
      relatedNodeIds: ["demo-node-hub"],
      description: "Visual timeline demonstration track.",
    },
  ],
};

// Backwards-compatible alias for isolated test suites
export const illustrativeInvestigationFixture = devOnlyDemonstrationFixture;
