"use client";

import React from "react";
import Link from "next/link";
import {
  PageHeader,
  ThreatTrendChart,
  SeverityDistributionChart,
} from "@/components/ui";
import TelemetryCards from "@/components/TelemetryCards";
import IncidentFeed from "@/components/IncidentFeed";
import { Plus, ArrowRight, ShieldCheck, Search, Network, Cpu } from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="SOC Threat Intelligence Cockpit"
        description="Executive telemetry, real-time deception detection, multi-vector threat scoring, and forensic explainability."
        badge={{ text: "Enterprise v1.0.0", variant: "blue" }}
        actions={
          <div className="flex items-center space-x-2">
            <Link
              href="/investigation"
              className="flex items-center space-x-1.5 px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>New Investigation</span>
            </Link>
          </div>
        }
      />

      {/* Production Telemetry Row */}
      <TelemetryCards />

      {/* Dual Real-Time Visual Charts (Image 1 Sentinel Nexus Style) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ThreatTrendChart />
        <SeverityDistributionChart />
      </div>

      {/* Quick Launchpad to Dedicated Modules */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link
          href="/analyze/text"
          className="p-4 rounded-xl bg-white border border-slate-200 shadow-subtle hover:border-blue-400 hover:shadow-card transition-all group"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-800 font-mono">01. Text Deception</span>
            <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 transition-transform group-hover:translate-x-1" />
          </div>
          <p className="text-xs text-slate-500">
            Multilingual SMS, WhatsApp, and email manipulation triage across English, Hindi, and Hinglish.
          </p>
        </Link>

        <Link
          href="/intelligence/campaigns"
          className="p-4 rounded-xl bg-white border border-slate-200 shadow-subtle hover:border-cyan-400 hover:shadow-card transition-all group"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-800 font-mono">02. Campaign Intelligence</span>
            <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-cyan-600 transition-transform group-hover:translate-x-1" />
          </div>
          <p className="text-xs text-slate-500">
            Unsupervised HDBSCAN clustering discovering coordinated phishing infrastructure and shared lures.
          </p>
        </Link>

        <Link
          href="/models"
          className="p-4 rounded-xl bg-white border border-slate-200 shadow-subtle hover:border-emerald-400 hover:shadow-card transition-all group"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-800 font-mono">03. Model Governance</span>
            <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-600 transition-transform group-hover:translate-x-1" />
          </div>
          <p className="text-xs text-slate-500">
            Held-out benchmark verification, 10-tactic confusion matrices, and SHAP explainability.
          </p>
        </Link>
      </div>

      {/* Incident Telemetry Feed */}
      <IncidentFeed id="incidents" />
    </div>
  );
}
