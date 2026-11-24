"use client";

import React from "react";
import Link from "next/link";
import { TopNavigation } from "@/components/investigation/TopNavigation";
import { Activity, History, Shield, ArrowRight, BarChart3 } from "lucide-react";

export default function AnalyticsHubPage() {
  return (
    <div className="min-h-screen bg-[#171C25] text-slate-100 flex flex-col font-sans select-none">
      <TopNavigation />

      <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto space-y-6">
        <div className="pb-4 border-b border-[#3A4553]">
          <h1 className="text-xl font-bold text-white tracking-wide">
            SOC Analytics & Performance Center
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Empirical machine learning benchmark evaluations, historical audit trails, and crowd-sourced threat triage metrics.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* 1. Model Performance Center */}
          <div className="bg-[#252D38] border border-[#3A4553] hover:border-emerald-500/50 rounded-lg p-5 flex flex-col justify-between transition-all group shadow-xl">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400">
                <Activity className="w-5 h-5" />
              </div>
              <h2 className="text-base font-bold text-white group-hover:text-emerald-300 transition-colors">
                ML Model Performance Center
              </h2>
              <p className="text-xs text-slate-300 leading-relaxed">
                Empirical test benchmark metrics for M1 (Bi-LSTM), M2 (XGBoost), M3 (Tactic Classifier), and M4 (HDBSCAN Clusterer).
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[#3A4553]">
              <Link
                href="/models"
                className="inline-flex items-center space-x-1.5 text-xs font-semibold text-emerald-400 hover:text-emerald-300"
              >
                <span>View Evaluation Benchmarks</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* 2. Analysis History */}
          <div className="bg-[#252D38] border border-[#3A4553] hover:border-blue-500/50 rounded-lg p-5 flex flex-col justify-between transition-all group shadow-xl">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-lg bg-blue-950/80 border border-blue-800/60 flex items-center justify-center text-blue-400">
                <History className="w-5 h-5" />
              </div>
              <h2 className="text-base font-bold text-white group-hover:text-blue-300 transition-colors">
                Analysis Audit Ledger
              </h2>
              <p className="text-xs text-slate-300 leading-relaxed">
                Immutable record of 115+ verified scans evaluated across multi-lingual SMS, phishing URLs, and vision OCR vectors.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[#3A4553]">
              <Link
                href="/history"
                className="inline-flex items-center space-x-1.5 text-xs font-semibold text-blue-400 hover:text-blue-300"
              >
                <span>Browse Scan History</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* 3. Community Reports */}
          <div className="bg-[#252D38] border border-[#3A4553] hover:border-rose-500/50 rounded-lg p-5 flex flex-col justify-between transition-all group shadow-xl">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-lg bg-rose-950/80 border border-rose-800/60 flex items-center justify-center text-rose-400">
                <Shield className="w-5 h-5" />
              </div>
              <h2 className="text-base font-bold text-white group-hover:text-rose-300 transition-colors">
                Community Reports & Triage
              </h2>
              <p className="text-xs text-slate-300 leading-relaxed">
                Citizen-reported threat telemetry feed with permission-gated SOC analyst verification and tactic assignment workflows.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[#3A4553]">
              <Link
                href="/reports"
                className="inline-flex items-center space-x-1.5 text-xs font-semibold text-rose-400 hover:text-rose-300"
              >
                <span>Access Triage Portal</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
