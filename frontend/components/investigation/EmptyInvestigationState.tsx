"use client";

import React from "react";
import { ShieldAlert, Plus, Search, Layers, Compass } from "lucide-react";

interface EmptyInvestigationStateProps {
  onCreateClick?: () => void;
  onExploreDemoClick?: () => void;
  message?: string;
}

export function EmptyInvestigationState({
  onCreateClick,
  onExploreDemoClick,
  message = "No active investigation is currently loaded in the ThreatQ workspace.",
}: EmptyInvestigationStateProps) {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-[#181E28] text-slate-300 p-8 select-none">
      {/* Radar Graphic */}
      <div className="relative w-32 h-32 flex items-center justify-center mb-6">
        <div className="absolute inset-0 rounded-full border border-cyan-500/20 animate-ping"></div>
        <div className="absolute inset-4 rounded-full border border-blue-500/30"></div>
        <div className="absolute inset-8 rounded-full border border-[#3A4553]"></div>
        <div className="w-12 h-12 rounded-full bg-blue-600/20 border border-blue-500/60 flex items-center justify-center text-cyan-400 shadow-[0_0_20px_rgba(56,189,248,0.3)]">
          <ShieldAlert className="w-6 h-6" />
        </div>
      </div>

      <h3 className="text-base font-bold text-white font-mono tracking-wide uppercase mb-2">
        Investigation Workspace Standby
      </h3>
      <p className="text-xs text-slate-400 max-w-md text-center leading-relaxed mb-6 font-sans">
        {message} Select an existing incident from the directory, load an HDBSCAN campaign cluster, or initiate a new forensic dossier.
      </p>

      <div className="flex items-center space-x-3">
        {onCreateClick && (
          <button
            onClick={onCreateClick}
            className="h-9 px-4 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold flex items-center space-x-2 shadow-lg shadow-blue-600/30 transition-all border border-blue-400/40"
          >
            <Plus className="w-4 h-4" />
            <span>Create Investigation</span>
          </button>
        )}
        {onExploreDemoClick && (
          <button
            onClick={onExploreDemoClick}
            className="h-9 px-4 bg-[#252D38] hover:bg-[#1E2631] text-slate-200 rounded text-xs font-semibold flex items-center space-x-2 border border-[#3A4553] transition-colors"
          >
            <Compass className="w-4 h-4 text-cyan-400" />
            <span>Load KYC Dossier #11</span>
          </button>
        )}
      </div>
    </div>
  );
}
