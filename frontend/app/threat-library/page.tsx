"use client";

import React from "react";
import Link from "next/link";
import { TopNavigation } from "@/components/investigation/TopNavigation";
import { Zap, Activity, AlertTriangle, ArrowRight, Shield } from "lucide-react";

export default function ThreatLibraryHubPage() {
  return (
    <div className="min-h-screen bg-[#171C25] text-slate-100 flex flex-col font-sans select-none">
      <TopNavigation />

      <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto space-y-6">
        <div className="pb-4 border-b border-[#3A4553]">
          <h1 className="text-xl font-bold text-white tracking-wide">
            Threat Intelligence Library
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Curated intelligence repositories across social engineering tactics, unsupervised campaign clusters, and active threat indicators.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* 1. Tactic Intelligence */}
          <div className="bg-[#252D38] border border-[#3A4553] hover:border-purple-500/50 rounded-lg p-5 flex flex-col justify-between transition-all group shadow-xl">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-lg bg-purple-950/80 border border-purple-800/60 flex items-center justify-center text-purple-400">
                <Zap className="w-5 h-5" />
              </div>
              <h2 className="text-base font-bold text-white group-hover:text-purple-300 transition-colors">
                Social Engineering Tactics
              </h2>
              <p className="text-xs text-slate-300 leading-relaxed">
                Standardized 10-class social engineering taxonomy (Urgency, Authority Impersonation, Financial Coercion, Verification Traps).
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[#3A4553]">
              <Link
                href="/intelligence/tactics"
                className="inline-flex items-center space-x-1.5 text-xs font-semibold text-purple-400 hover:text-purple-300"
              >
                <span>Explore 10-Tactic Matrix</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* 2. Campaign Clusters */}
          <div className="bg-[#252D38] border border-[#3A4553] hover:border-orange-500/50 rounded-lg p-5 flex flex-col justify-between transition-all group shadow-xl">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-lg bg-orange-950/80 border border-orange-800/60 flex items-center justify-center text-orange-400">
                <Activity className="w-5 h-5" />
              </div>
              <h2 className="text-base font-bold text-white group-hover:text-orange-300 transition-colors">
                Campaign Discovery Clusters
              </h2>
              <p className="text-xs text-slate-300 leading-relaxed">
                47 unsupervised sentence-transformer density clusters grouping multi-lingual lures by mathematical embedding proximity.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[#3A4553]">
              <Link
                href="/intelligence/campaigns"
                className="inline-flex items-center space-x-1.5 text-xs font-semibold text-orange-400 hover:text-orange-300"
              >
                <span>View 47 Campaign Dossiers</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* 3. Threat Indicators */}
          <div className="bg-[#252D38] border border-[#3A4553] hover:border-rose-500/50 rounded-lg p-5 flex flex-col justify-between transition-all group shadow-xl">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-lg bg-rose-950/80 border border-rose-800/60 flex items-center justify-center text-rose-400">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h2 className="text-base font-bold text-white group-hover:text-rose-300 transition-colors">
                Threat Indicators & IOCs
              </h2>
              <p className="text-xs text-slate-300 leading-relaxed">
                Extracted technical indicators including VoIP dispatch numbers, fraudulent UPI handles, typosquatted FQDNs, and hosting IPs.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[#3A4553]">
              <Link
                href="/intelligence/threats"
                className="inline-flex items-center space-x-1.5 text-xs font-semibold text-rose-400 hover:text-rose-300"
              >
                <span>Inspect IOC Feed</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
