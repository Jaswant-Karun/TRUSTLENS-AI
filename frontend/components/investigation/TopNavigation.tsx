"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Shield,
  Search,
  Plus,
  Bell,
  HelpCircle,
  Settings,
  ChevronDown,
  Layers,
  Zap,
  Activity,
  History,
  AlertTriangle,
  User,
  X,
  ExternalLink,
  CheckCircle2,
} from "lucide-react";

interface TopNavigationProps {
  onCreateClick?: () => void;
  onSearchClick?: () => void;
}

export function TopNavigation({ onCreateClick, onSearchClick }: TopNavigationProps) {
  const pathname = usePathname();
  const [threatLibraryOpen, setThreatLibraryOpen] = useState(false);
  const [analyticsOpen, setAnalyticsOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);

  const isHomeActive = pathname === "/" || pathname === "/dashboard";
  const isThreatLibraryActive =
    pathname.startsWith("/threat-library") || pathname.startsWith("/intelligence");
  const isInvestigationsActive =
    pathname.startsWith("/investigation") || pathname.startsWith("/investigations");
  const isAnalyticsActive =
    pathname.startsWith("/analytics") ||
    pathname.startsWith("/models") ||
    pathname.startsWith("/history") ||
    pathname.startsWith("/reports");

  return (
    <header className="h-[52px] bg-[#252D38] border-b border-[#3A4553] flex items-center justify-between px-4 select-none relative z-40 text-slate-200">
      {/* Left: Branding & Core Navigation Links */}
      <div className="flex items-center space-x-6">
        {/* TRUSTLENS AI Brand */}
        <Link
          href="/dashboard"
          className="flex items-center space-x-2.5 group focus:outline-none"
        >
          <div className="w-8 h-8 rounded-md bg-gradient-to-br from-blue-600 via-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:shadow-blue-500/40 transition-all border border-blue-400/30">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center space-x-1">
              <span className="font-extrabold tracking-wider text-sm text-white font-mono">
                TRUSTLENS
              </span>
              <span className="text-[11px] font-bold text-cyan-400 font-mono tracking-widest bg-cyan-950/80 px-1 py-0.2 rounded border border-cyan-800/40">
                AI
              </span>
            </div>
            <span className="text-[9px] font-mono tracking-widest text-slate-400 -mt-0.5 uppercase">
              Threat Intelligence
            </span>
          </div>
        </Link>

        {/* Vertical Divider */}
        <div className="h-6 w-px bg-[#3A4553]"></div>

        {/* Primary Tabs */}
        <nav className="flex items-center space-x-1">
          {/* 1. Home */}
          <Link
            href="/dashboard"
            className={`px-3 py-1.5 rounded text-xs font-medium transition-colors flex items-center space-x-1.5 ${
              isHomeActive
                ? "text-white bg-[#181E28] border border-[#3A4553]"
                : "text-slate-300 hover:text-white hover:bg-[#1E2631]"
            }`}
          >
            <span>Home</span>
          </Link>

          {/* 2. Threat Library Dropdown */}
          <div className="relative">
            <button
              onClick={() => {
                setThreatLibraryOpen(!threatLibraryOpen);
                setAnalyticsOpen(false);
              }}
              className={`px-3 py-1.5 rounded text-xs font-medium transition-colors flex items-center space-x-1 ${
                isThreatLibraryActive
                  ? "text-white bg-[#181E28] border border-[#3A4553]"
                  : "text-slate-300 hover:text-white hover:bg-[#1E2631]"
              }`}
            >
              <span>Threat Library</span>
              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${threatLibraryOpen ? "rotate-180" : ""}`} />
            </button>

            {threatLibraryOpen && (
              <div
                className="absolute left-0 mt-1.5 w-60 bg-[#252D38] border border-[#3A4553] rounded-md shadow-2xl py-1.5 z-50 text-xs"
                onMouseLeave={() => setThreatLibraryOpen(false)}
              >
                <div className="px-3 py-1 text-[10px] font-semibold text-slate-400 uppercase tracking-wider font-mono">
                  Threat Assets
                </div>
                <Link
                  href="/threat-library"
                  onClick={() => setThreatLibraryOpen(false)}
                  className="flex items-center space-x-2 px-3 py-2 text-slate-200 hover:bg-[#181E28] hover:text-cyan-400"
                >
                  <Layers className="w-4 h-4 text-cyan-400" />
                  <div>
                    <div className="font-medium">Threat Library Overview</div>
                    <div className="text-[10px] text-slate-400">All tactics, campaigns & indicators</div>
                  </div>
                </Link>
                <Link
                  href="/intelligence/tactics"
                  onClick={() => setThreatLibraryOpen(false)}
                  className="flex items-center space-x-2 px-3 py-2 text-slate-200 hover:bg-[#181E28] hover:text-cyan-400"
                >
                  <Zap className="w-4 h-4 text-purple-400" />
                  <div>
                    <div className="font-medium">Tactic Intelligence</div>
                    <div className="text-[10px] text-slate-400">10-class social engineering taxonomy</div>
                  </div>
                </Link>
                <Link
                  href="/intelligence/campaigns"
                  onClick={() => setThreatLibraryOpen(false)}
                  className="flex items-center space-x-2 px-3 py-2 text-slate-200 hover:bg-[#181E28] hover:text-cyan-400"
                >
                  <Activity className="w-4 h-4 text-orange-400" />
                  <div>
                    <div className="font-medium">Campaign Clusters</div>
                    <div className="text-[10px] text-slate-400">47 HDBSCAN similarity dossiers</div>
                  </div>
                </Link>
                <Link
                  href="/intelligence/threats"
                  onClick={() => setThreatLibraryOpen(false)}
                  className="flex items-center space-x-2 px-3 py-2 text-slate-200 hover:bg-[#181E28] hover:text-cyan-400"
                >
                  <AlertTriangle className="w-4 h-4 text-rose-400" />
                  <div>
                    <div className="font-medium">Threat Indicators & IOCs</div>
                    <div className="text-[10px] text-slate-400">Phones, UPI handles, domains</div>
                  </div>
                </Link>
              </div>
            )}
          </div>

          {/* 3. Investigations (Primary Workspace Link) */}
          <Link
            href="/investigations"
            className={`px-3 py-1.5 rounded text-xs font-semibold transition-all flex items-center space-x-1.5 relative ${
              isInvestigationsActive
                ? "text-white bg-[#181E28] border border-blue-500/50 shadow-inner"
                : "text-slate-300 hover:text-white hover:bg-[#1E2631]"
            }`}
          >
            <div className={`w-1.5 h-1.5 rounded-full ${isInvestigationsActive ? "bg-cyan-400 animate-pulse" : "bg-slate-500"}`}></div>
            <span>Investigations</span>
            {isInvestigationsActive && (
              <span className="absolute -bottom-[9px] left-3 right-3 h-[2px] bg-cyan-400 rounded-full shadow-[0_0_8px_rgba(56,189,248,0.8)]"></span>
            )}
          </Link>

          {/* 4. Analytics Dropdown */}
          <div className="relative">
            <button
              onClick={() => {
                setAnalyticsOpen(!analyticsOpen);
                setThreatLibraryOpen(false);
              }}
              className={`px-3 py-1.5 rounded text-xs font-medium transition-colors flex items-center space-x-1 ${
                isAnalyticsActive
                  ? "text-white bg-[#181E28] border border-[#3A4553]"
                  : "text-slate-300 hover:text-white hover:bg-[#1E2631]"
              }`}
            >
              <span>Analytics</span>
              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${analyticsOpen ? "rotate-180" : ""}`} />
            </button>

            {analyticsOpen && (
              <div
                className="absolute left-0 mt-1.5 w-60 bg-[#252D38] border border-[#3A4553] rounded-md shadow-2xl py-1.5 z-50 text-xs"
                onMouseLeave={() => setAnalyticsOpen(false)}
              >
                <Link
                  href="/analytics"
                  onClick={() => setAnalyticsOpen(false)}
                  className="flex items-center space-x-2 px-3 py-2 text-slate-200 hover:bg-[#181E28] hover:text-cyan-400"
                >
                  <Layers className="w-4 h-4 text-cyan-400" />
                  <div>
                    <div className="font-medium">Analytics Cockpit</div>
                    <div className="text-[10px] text-slate-400">Platform performance & logs</div>
                  </div>
                </Link>
                <Link
                  href="/models"
                  onClick={() => setAnalyticsOpen(false)}
                  className="flex items-center space-x-2 px-3 py-2 text-slate-200 hover:bg-[#181E28] hover:text-cyan-400"
                >
                  <Activity className="w-4 h-4 text-emerald-400" />
                  <div>
                    <div className="font-medium">Model Performance Center</div>
                    <div className="text-[10px] text-slate-400">M1-M4 benchmarks & evaluation</div>
                  </div>
                </Link>
                <Link
                  href="/history"
                  onClick={() => setAnalyticsOpen(false)}
                  className="flex items-center space-x-2 px-3 py-2 text-slate-200 hover:bg-[#181E28] hover:text-cyan-400"
                >
                  <History className="w-4 h-4 text-blue-400" />
                  <div>
                    <div className="font-medium">Analysis Audit Ledger</div>
                    <div className="text-[10px] text-slate-400">115+ verified scan records</div>
                  </div>
                </Link>
                <Link
                  href="/reports"
                  onClick={() => setAnalyticsOpen(false)}
                  className="flex items-center space-x-2 px-3 py-2 text-slate-200 hover:bg-[#181E28] hover:text-cyan-400"
                >
                  <Shield className="w-4 h-4 text-rose-400" />
                  <div>
                    <div className="font-medium">Community Reports</div>
                    <div className="text-[10px] text-slate-400">Crowd threat telemetry & SOC review</div>
                  </div>
                </Link>
              </div>
            )}
          </div>
        </nav>
      </div>

      {/* Right: Actions, Search, Notifications, Profile */}
      <div className="flex items-center space-x-3">
        {/* "+ Create" Primary Action Button */}
        <button
          onClick={onCreateClick}
          className="h-8 px-3.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold flex items-center space-x-1.5 shadow-md shadow-blue-600/30 transition-all border border-blue-400/30 hover:scale-[1.02]"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Create</span>
        </button>

        {/* Global Search Button */}
        <button
          onClick={onSearchClick}
          title="Search threat intelligence..."
          className="w-8 h-8 rounded bg-[#1E2631] hover:bg-[#181E28] border border-[#3A4553] flex items-center justify-center text-slate-300 hover:text-white transition-colors"
        >
          <Search className="w-4 h-4" />
        </button>

        {/* Notifications Button with Popover */}
        <div className="relative">
          <button
            onClick={() => setNotificationsOpen(!notificationsOpen)}
            title="System & Threat Notifications"
            className="w-8 h-8 rounded bg-[#1E2631] hover:bg-[#181E28] border border-[#3A4553] flex items-center justify-center text-slate-300 hover:text-white transition-colors relative"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-cyan-400 ring-2 ring-[#252D38]"></span>
          </button>

          {notificationsOpen && (
            <div
              className="absolute right-0 mt-2 w-80 bg-[#252D38] border border-[#3A4553] rounded-md shadow-2xl py-2 z-50 text-xs"
              onMouseLeave={() => setNotificationsOpen(false)}
            >
              <div className="flex items-center justify-between px-3 py-1.5 border-b border-[#3A4553]">
                <span className="font-semibold text-white">Live Security Alerts</span>
                <span className="text-[10px] text-cyan-400 font-mono">3 Unread</span>
              </div>
              <div className="divide-y divide-[#3A4553]/60 max-h-64 overflow-y-auto">
                <div className="p-3 hover:bg-[#181E28] transition-colors cursor-pointer">
                  <div className="flex items-center space-x-2 text-rose-400 font-medium">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Critical Campaign Cluster #11 Spike</span>
                  </div>
                  <p className="text-[11px] text-slate-300 mt-1">
                    254 messages observed spoofing banking KYC. Cohesion: 88.4%.
                  </p>
                  <span className="text-[10px] text-slate-500 font-mono">10m ago</span>
                </div>
                <div className="p-3 hover:bg-[#181E28] transition-colors cursor-pointer">
                  <div className="flex items-center space-x-2 text-amber-400 font-medium">
                    <Activity className="w-3.5 h-3.5" />
                    <span>Phishing Domain Flagged: sbi-kyc.top</span>
                  </div>
                  <p className="text-[11px] text-slate-300 mt-1">
                    Model 2 (XGBoost) isolated domain with 100% confidence.
                  </p>
                  <span className="text-[10px] text-slate-500 font-mono">25m ago</span>
                </div>
                <div className="p-3 hover:bg-[#181E28] transition-colors cursor-pointer">
                  <div className="flex items-center space-x-2 text-emerald-400 font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>All 4 ML Inference Engines Online</span>
                  </div>
                  <p className="text-[11px] text-slate-300 mt-1">
                    Latency: 0.024ms. Zero synthetic indicators detected.
                  </p>
                  <span className="text-[10px] text-slate-500 font-mono">1h ago</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Help Button */}
        <button
          onClick={() => setHelpOpen(true)}
          title="Cyber Threat Playbook & Help"
          className="w-8 h-8 rounded bg-[#1E2631] hover:bg-[#181E28] border border-[#3A4553] flex items-center justify-center text-slate-300 hover:text-white transition-colors"
        >
          <HelpCircle className="w-4 h-4" />
        </button>

        {/* Settings Button */}
        <Link
          href="/settings"
          title="Platform & Engine Settings"
          className="w-8 h-8 rounded bg-[#1E2631] hover:bg-[#181E28] border border-[#3A4553] flex items-center justify-center text-slate-300 hover:text-white transition-colors"
        >
          <Settings className="w-4 h-4" />
        </Link>

        {/* User Profile Avatar Pill */}
        <div className="flex items-center space-x-2 pl-2 border-l border-[#3A4553]">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center text-white text-xs font-bold font-mono ring-1 ring-cyan-400/40">
            RS
          </div>
          <div className="hidden xl:flex flex-col text-left">
            <span className="text-xs font-semibold text-slate-200 leading-none">Senior Analyst</span>
            <span className="text-[10px] text-cyan-400 font-mono">SOC Lead</span>
          </div>
        </div>
      </div>

      {/* Help Modal */}
      {helpOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#252D38] border border-[#3A4553] rounded-lg shadow-2xl max-w-lg w-full p-5 text-slate-200">
            <div className="flex items-center justify-between border-b border-[#3A4553] pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-cyan-400" />
                <h3 className="font-semibold text-white">TRUSTLENS AI SOC Investigation Guide</h3>
              </div>
              <button
                onClick={() => setHelpOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-3 text-xs text-slate-300">
              <p>
                <strong>Central Threat Graph:</strong> Click and drag nodes to adjust the spatial topology. Click a node to inspect its indicators, model outputs, and linked relationships in the Right Inspector.
              </p>
              <p>
                <strong>Timeline Correlation:</strong> Scrub the bottom timeline to view chronological event chains (tasks, situations, indicator detections).
              </p>
              <p>
                <strong>Attribution Policy:</strong> Unsupervised clusters mathematically identify syntactic & semantic embedding proximity. Formal legal attribution requires external law enforcement corroboration.
              </p>
            </div>
            <div className="mt-5 flex justify-end">
              <button
                onClick={() => setHelpOpen(false)}
                className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-medium"
              >
                Got it
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
