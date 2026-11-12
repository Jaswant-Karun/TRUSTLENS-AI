"use client";

import React, { useEffect, useState } from "react";
import {
  Network,
  ShieldAlert,
  ShieldCheck,
  AlertCircle,
  ExternalLink,
  ChevronRight,
  Info,
  Layers,
  ArrowRight,
} from "lucide-react";
import { getCampaigns, CampaignSummary } from "@/lib/api";
import { SkeletonCard } from "./ui/LoadingStates";

interface KillChainGraphProps {
  id?: string;
}

export default function KillChainGraph({ id }: KillChainGraphProps) {
  const [campaigns, setCampaigns] = useState<CampaignSummary[]>([]);
  const [selectedCampaign, setSelectedCampaign] = useState<CampaignSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    getCampaigns(12)
      .then((data) => {
        if (isMounted) {
          setCampaigns(data);
          if (data && data.length > 0) {
            setSelectedCampaign(data[0]);
          }
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return <SkeletonCard />;
  }

  return (
    <div id={id} className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 mb-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 mb-5 border-b border-slate-100 gap-3">
        <div>
          <div className="flex items-center space-x-2">
            <Network className="w-4 h-4 text-sky-600" />
            <h2 className="text-base font-bold text-slate-900">Campaign Intelligence & Attack Kill-Chain Graph</h2>
            <span className="text-xs px-2 py-0.5 rounded-full bg-sky-50 text-sky-700 font-mono font-medium border border-sky-200">
              HDBSCAN Model 4
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Discovered threat clusters linking deceptive lures, targeted institutions, and coordinated phishing infrastructure.
          </p>
        </div>

        <div className="text-xs font-mono text-slate-500 bg-slate-50 px-2.5 py-1 rounded border border-slate-200">
          Showing {campaigns.length} Active Coordinated Clusters
        </div>
      </div>

      {/* Grid: Left Cluster Selector, Right Kill-Chain Lifecycle */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Discovered Campaign Clusters List */}
        <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
          <div className="text-[11px] font-mono uppercase text-slate-400 font-semibold mb-2">
            Identified Threat Campaigns
          </div>
          {campaigns.length === 0 ? (
            <div className="p-4 bg-slate-50 rounded-lg text-xs text-slate-500 text-center">
              No active campaign clusters available.
            </div>
          ) : (
            campaigns.map((camp) => {
              const isSelected = selectedCampaign?.campaign_id === camp.campaign_id;
              return (
                <button
                  key={camp.campaign_id}
                  onClick={() => setSelectedCampaign(camp)}
                  className={`w-full text-left p-3 rounded-lg border transition-all flex flex-col justify-between ${
                    isSelected
                      ? "border-blue-500 bg-blue-50/60 shadow-sm"
                      : "border-slate-200 hover:border-slate-300 bg-white"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900">
                      Cluster #{camp.campaign_id}: {camp.target_brand}
                    </span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                      Cohesion: {Math.round(camp.cohesion_score * 100)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2 font-mono">
                    <span className="truncate max-w-[150px]">{camp.primary_tactic}</span>
                    <span className="font-semibold text-slate-700">{camp.cluster_size} messages</span>
                  </div>
                </button>
              );
            })
          )}
        </div>

        {/* Right: Interactive Kill-Chain Lifecycle Flow */}
        <div className="lg:col-span-2 bg-slate-50/70 border border-slate-200 rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-200">
              <div>
                <span className="text-[11px] font-mono uppercase text-slate-400 font-medium">Selected Dossier</span>
                <h3 className="text-sm font-bold text-slate-900">
                  {selectedCampaign ? `Cluster #${selectedCampaign.campaign_id} — ${selectedCampaign.target_brand}` : "Campaign Dossier"}
                </h3>
              </div>
              {selectedCampaign && (
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200 font-mono font-medium">
                  Status: {selectedCampaign.status.toUpperCase()}
                </span>
              )}
            </div>

            {/* 4-Stage Attack Lifecycle Pipeline */}
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 mb-6">
              {/* Stage 1: Vector Origin */}
              <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-subtle flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold">1. Delivery</span>
                  <div className="text-xs font-bold text-slate-800 mt-1">Bulk Gateway</div>
                  <p className="text-[11px] text-slate-500 mt-1">Automated sender routing deceptive SMS packets.</p>
                </div>
                <div className="text-[10px] text-blue-600 font-mono font-medium mt-3">Sender Header</div>
              </div>

              {/* Stage 2: Deceptive Pretext */}
              <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-subtle flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold">2. Pretext Lure</span>
                  <div className="text-xs font-bold text-slate-800 mt-1 truncate">
                    {selectedCampaign?.primary_tactic || "Account Coercion"}
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1">Impersonation of {selectedCampaign?.target_brand || "institution"}.</p>
                </div>
                <div className="text-[10px] text-amber-600 font-mono font-medium mt-3">Psychological Coercion</div>
              </div>

              {/* Stage 3: Phishing Landing */}
              <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-subtle flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold">3. Credential Trap</span>
                  <div className="text-xs font-bold text-slate-800 mt-1">Cloned Web Portal</div>
                  <p className="text-[11px] text-slate-500 mt-1">Typo-squatted domains hosting fake netbanking forms.</p>
                </div>
                <div className="text-[10px] text-rose-600 font-mono font-medium mt-3">Zero-Hop Detected</div>
              </div>

              {/* Stage 4: Exfiltration */}
              <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-subtle flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold">4. Interception</span>
                  <div className="text-xs font-bold text-slate-800 mt-1">Credential Harvesting</div>
                  <p className="text-[11px] text-slate-500 mt-1">OTP relays and unauthorized fund withdrawal.</p>
                </div>
                <div className="text-[10px] text-purple-600 font-mono font-medium mt-3">Active Mitigation</div>
              </div>
            </div>
          </div>

          {/* Mandatory Legal Caveat */}
          <div className="p-3 rounded-lg bg-amber-50/70 border border-amber-200 text-xs text-amber-900 flex items-start space-x-2">
            <Info className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
            <div className="text-[11px] leading-relaxed">
              <span className="font-semibold">Model 4 Anti-Fabrication Caveat:</span> Campaign clustering represents mathematical sentence embedding proximity and shared lexical/domain indicators. It does NOT automatically establish legal attribution or criminal culpability without independent forensic verification.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
