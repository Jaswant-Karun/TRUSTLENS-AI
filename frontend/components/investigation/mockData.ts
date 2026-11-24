/**
 * TRUSTLENS AI - Illustrative Preview Fixture for Threat Investigation Workspace UI
 * NOTE: This is a clearly labelled demonstration fixture based on actual observed
 * Campaign Cluster #11 (Banking KYC Smishing) and Model 1-4 telemetry.
 * It is exclusively used for visual preview and UI validation.
 */

import { InvestigationData } from "./types";

export const illustrativeInvestigationFixture: InvestigationData = {
  id: "INV-2026-KYC-11",
  title: "Analysis of Banking KYC Smishing Syndicate #11",
  description:
    "This investigation models an active multilingual smishing campaign targeting Indian public sector bank customers (specifically State Bank of India). Attackers distribute urgent SMS and WhatsApp alerts claiming imminent account freeze due to expired PAN/KYC credentials, directing victims to spoofed credential-harvesting portals.",
  severity: "critical",
  visibility: "Organization",
  status: "Active",
  created: {
    date: "Yesterday, 9:29am",
    author: "Senior Analyst (RS)",
    relative: "1 day ago",
  },
  lastModified: {
    date: "Today, 2:32pm",
    author: "SOC Lead (TK)",
    relative: "10 minutes ago",
  },
  objectsCount: 139,
  tasksCount: 3,
  commentsCount: 0,
  sources: ["CERT-In Telemetry", "ScamShield Corpus", "Community Report #07a380c7"],
  tags: ["sbi_kyc", "smishing", "m1_bilstm", "m2_xgboost", "m4_cluster_11", "phishing_url"],
  attributes: {
    "Target Brand": "State Bank of India (SBI)",
    "Primary Vector": "Multilingual Smishing (SMS / WhatsApp)",
    "Language Distribution": "English (64%), Hindi / Hinglish (36%)",
    "ML Confidence": "98.4% (Calibrated Ensemble)",
    "Cluster Cohesion": "88.4% (HDBSCAN MiniLM-L6-v2)",
  },
  nodes: [
    // Central Node (Equivalent to GRIZZLY STEPPE in ThreatQ)
    {
      id: "node-cluster-11",
      label: "SBI KYC SYNDICATE #11",
      type: "campaign_cluster",
      subType: "HDBSCAN Cluster #11",
      severity: "critical",
      isCentral: true,
      x: 0,
      y: 0,
      radius: 40,
      metadata: {
        description: "47-cluster discovery corpus. 254 messages sharing high semantic cosine similarity.",
        confidence: 0.984,
        riskScore: 0.96,
        modelVersion: "trustlens-model4-campaign-v1.0",
        evidence: [
          "Cohesion score: 88.4%",
          "Shared lexical pattern: 'Dear customer your SBI account will be blocked today'",
          "Corroborated by 3 distinct user submissions",
        ],
        tags: ["cluster_11", "state_bank_of_india", "smishing"],
      },
    },

    // Category Node
    {
      id: "node-category-1",
      label: "Banking / KYC Fraud",
      type: "scam_category",
      subType: "Financial Deception",
      severity: "critical",
      x: 180,
      y: -90,
      metadata: {
        description: "Deceptive financial lure spoofing banking KYC and account maintenance procedures.",
      },
    },

    // Tactics Nodes
    {
      id: "node-tactic-urgency",
      label: "Urgency / Panic Pretext",
      type: "tactic",
      subType: "T01 - 10-Tactic Taxonomy",
      severity: "high",
      x: 190,
      y: 80,
      metadata: {
        description: "Demands immediate compliance within 24 hours under penalty of account suspension.",
        modelVersion: "trustlens-model3-tactics-v1.0",
        confidence: 0.942,
      },
    },
    {
      id: "node-tactic-authority",
      label: "Authority Spoofing",
      type: "tactic",
      subType: "T02 - Brand Impersonation",
      severity: "high",
      x: 120,
      y: 190,
      metadata: {
        description: "Impersonates SBI Bank Manager and Cyber Crime Cell authority seals.",
        modelVersion: "trustlens-model3-tactics-v1.0",
        confidence: 0.967,
      },
    },

    // Message Nodes
    {
      id: "node-msg-urgent",
      label: "SMS: 'SBI account blocked today'",
      type: "message",
      subType: "Observed SMS Exemplar",
      severity: "critical",
      x: -180,
      y: -80,
      metadata: {
        description: "Raw SMS text: 'Dear customer your SBI account will be blocked today please update your pan card immediately click here: http://sbi-kyc-update.com'",
        modelVersion: "trustlens-model1-bilstm-v1.0",
        riskScore: 0.95,
        evidence: ["Detected Language: English", "Bi-LSTM Probability: 0.954"],
      },
    },
    {
      id: "node-msg-hinglish",
      label: "SMS: 'Khata turant band hoga'",
      type: "message",
      subType: "Multilingual Lure",
      severity: "critical",
      x: -240,
      y: 40,
      metadata: {
        description: "Raw text: 'Aapka SBI khata turant band ho jayega, KYC update karein link par'",
        modelVersion: "trustlens-model1-bilstm-v1.0",
        riskScore: 0.93,
      },
    },

    // URL & Domain Nodes
    {
      id: "node-url-phish",
      label: "http://sbi-kyc-update.com",
      type: "url",
      subType: "Credential Harvester",
      severity: "critical",
      x: -120,
      y: -210,
      metadata: {
        description: "Zero-hop offline XGBoost inspection identified deceptive login credential form.",
        modelVersion: "trustlens-model2-xgboost-v1.0",
        riskScore: 1.0,
        evidence: [
          "High Shannon entropy (4.30)",
          "Hyphen in domain (typosquatting)",
          "Insecure HTTP scheme",
        ],
      },
    },
    {
      id: "node-domain-fqdn",
      label: "sbi-kyc-update.com",
      type: "domain",
      subType: "Spoofed FQDN",
      severity: "high",
      x: -10,
      y: -260,
      metadata: {
        description: "Registered 48 hours prior to attack spike via offshore registrar.",
      },
    },
    {
      id: "node-ip-c2",
      label: "194.168.20.14",
      type: "ip",
      subType: "Offshore Host IP",
      severity: "high",
      x: 140,
      y: -240,
      metadata: {
        description: "Hosting infrastructure associated with multiple recurring smishing domains.",
      },
    },

    // Indicators (Fingerprints with count badges matching ThreatQ)
    {
      id: "node-iocs-phone",
      label: "+91-98765-43210 (Sender)",
      type: "threat_indicator",
      subType: "Technical IOCs",
      count: 45,
      severity: "high",
      x: -20,
      y: 190,
      metadata: {
        description: "VoIP numbers originating SMS dispatch across Delhi & Mumbai telecom circles.",
      },
    },
    {
      id: "node-iocs-upi",
      label: "paytm-sbi-verify@upi",
      type: "threat_indicator",
      subType: "Extraction UPI ID",
      count: 18,
      severity: "critical",
      x: -120,
      y: 160,
      metadata: {
        description: "Fraudulent UPI handle used to extract micro-verification deposits.",
      },
    },

    // User Report Node
    {
      id: "node-report-citizen",
      label: "Citizen Report #07a380c7",
      type: "user_report",
      subType: "Verified Victim Report",
      severity: "medium",
      x: -280,
      y: -180,
      metadata: {
        description: "Victim received SMS after 8 PM; verified as malicious by SOC triage.",
        status: "verified",
      },
    },

    // Source Reference Node
    {
      id: "node-source-cert",
      label: "CERT-In Smishing Advisory",
      type: "source_reference",
      subType: "External Intelligence",
      severity: "low",
      x: 270,
      y: 0,
      metadata: {
        description: "Government CERT advisory documenting widespread banking impersonation wave.",
      },
    },
  ],

  edges: [
    // Cluster connections (Central hub radiating out like ThreatQ)
    { id: "e1", source: "node-cluster-11", target: "node-category-1", label: "categorized_as", relationship: "targets_entity", severity: "critical" },
    { id: "e2", source: "node-cluster-11", target: "node-tactic-urgency", label: "exhibits_tactic", relationship: "exhibits_tactic", severity: "high" },
    { id: "e3", source: "node-cluster-11", target: "node-tactic-authority", label: "impersonates_brand", relationship: "exhibits_tactic", severity: "high" },
    { id: "e4", source: "node-cluster-11", target: "node-msg-urgent", label: "exemplar_lure", relationship: "belongs_to_cluster", severity: "critical" },
    { id: "e5", source: "node-cluster-11", target: "node-msg-hinglish", label: "multilingual_variant", relationship: "belongs_to_cluster", severity: "critical" },
    { id: "e6", source: "node-cluster-11", target: "node-iocs-phone", label: "dispatched_from", relationship: "references_indicator", severity: "high" },
    { id: "e7", source: "node-cluster-11", target: "node-iocs-upi", label: "extracts_funds_via", relationship: "references_indicator", severity: "critical" },
    { id: "e8", source: "node-cluster-11", target: "node-source-cert", label: "referenced_in", relationship: "associated_with", severity: "neutral" },

    // Message -> URL -> Domain -> IP chain
    { id: "e9", source: "node-msg-urgent", target: "node-url-phish", label: "contains_url", relationship: "contains_url", severity: "critical" },
    { id: "e10", source: "node-url-phish", target: "node-domain-fqdn", label: "resolves_to", relationship: "resolves_to", severity: "high" },
    { id: "e11", source: "node-domain-fqdn", target: "node-ip-c2", label: "hosted_on", relationship: "resolves_to", severity: "high" },

    // Report reference
    { id: "e12", source: "node-report-citizen", target: "node-msg-urgent", label: "submitted_evidence", relationship: "reported_by", severity: "medium" },
  ],

  timeline: [
    // Tasks Track
    {
      id: "t1",
      title: "Read CERT-In advisory",
      dateLabel: "JAN 9",
      timestamp: "2026-01-09T09:00:00Z",
      track: "tasks",
      severity: "info",
      relatedNodeIds: ["node-source-cert"],
    },
    {
      id: "t2",
      title: "Hunt for indicators locally",
      dateLabel: "FEB 6",
      timestamp: "2026-02-06T14:30:00Z",
      track: "tasks",
      severity: "high",
      relatedNodeIds: ["node-iocs-phone", "node-iocs-upi"],
    },
    {
      id: "t3",
      title: "Plan incident mitigation",
      dateLabel: "FEB 27",
      timestamp: "2026-02-27T16:00:00Z",
      track: "tasks",
      severity: "critical",
      relatedNodeIds: ["node-cluster-11"],
    },

    // Situation Track
    {
      id: "s1",
      title: "Window of exposure",
      dateLabel: "JAN 16",
      timestamp: "2026-01-16T00:00:00Z",
      track: "situation",
      severity: "high",
      relatedNodeIds: ["node-msg-urgent"],
    },
    {
      id: "s2",
      title: "Operation FakeKYC activated",
      dateLabel: "JAN 23",
      timestamp: "2026-01-23T11:20:00Z",
      track: "situation",
      severity: "critical",
      relatedNodeIds: ["node-cluster-11"],
    },
    {
      id: "s3",
      title: "Report of mass SMS activity",
      dateLabel: "FEB 13",
      timestamp: "2026-02-13T10:15:00Z",
      track: "situation",
      severity: "high",
      relatedNodeIds: ["node-report-citizen"],
    },

    // Indicators Track
    {
      id: "i1",
      title: "sbi-kyc-update.com first seen",
      dateLabel: "FEB 13",
      timestamp: "2026-02-13T18:40:00Z",
      track: "indicators",
      severity: "critical",
      relatedNodeIds: ["node-url-phish", "node-domain-fqdn"],
    },
    {
      id: "i2",
      title: "194.168.20.14 created",
      dateLabel: "FEB 20",
      timestamp: "2026-02-20T08:12:00Z",
      track: "indicators",
      severity: "high",
      relatedNodeIds: ["node-ip-c2"],
    },
    {
      id: "i3",
      title: "paytm-sbi-verify@upi flagged",
      dateLabel: "FEB 20",
      timestamp: "2026-02-20T19:05:00Z",
      track: "indicators",
      severity: "critical",
      relatedNodeIds: ["node-iocs-upi"],
    },
  ],
};
