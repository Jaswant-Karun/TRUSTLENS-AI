"use client";

import React, { useEffect, useState } from "react";
import {
  Menu,
  Search,
  Activity,
  Terminal,
  ExternalLink,
  Plus,
  ShieldAlert,
} from "lucide-react";
import { getHealth, SystemHealth } from "@/lib/api";

interface TopNavbarProps {
  onOpenMobileSidebar: () => void;
  onQuickScanClick?: () => void;
  title?: string;
}

export function TopNavbar({
  onOpenMobileSidebar,
  onQuickScanClick,
  title = "TRUSTLENS AI SOC Platform",
}: TopNavbarProps) {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    let isMounted = true;

    const checkHealth = async () => {
      try {
        const res = await getHealth();
        if (isMounted) {
          setHealth(res);
          setIsHealthy(res.status === "healthy" || res.status === "online");
        }
      } catch {
        if (isMounted) {
          setIsHealthy(false);
        }
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 15000); // 15s polling
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="h-16 px-4 md:px-6 bg-white border-b border-slate-200/80 sticky top-0 z-30 flex items-center justify-between shadow-subtle">
      {/* Left Section: Mobile Toggle & Page Context */}
      <div className="flex items-center space-x-3.5">
        <button
          onClick={onOpenMobileSidebar}
          className="lg:hidden p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
          aria-label="Open Navigation Menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:block">
          <h2 className="text-sm font-bold text-slate-800 tracking-tight">{title}</h2>
          <p className="text-[11px] text-slate-500 font-medium">Multilingual Digital Fraud Intelligence & Prevention</p>
        </div>
      </div>

      {/* Right Section: Telemetry, Swagger Docs, New Scan CTA */}
      <div className="flex items-center space-x-3">
        {/* Real Backend Telemetry Indicator */}
        <div className="flex items-center space-x-2 px-2.5 py-1 rounded-full border text-xs font-mono font-medium">
          {isHealthy === null ? (
            <span className="flex items-center space-x-1.5 text-slate-400">
              <span className="w-2 h-2 rounded-full bg-slate-300 animate-pulse"></span>
              <span className="text-[11px]">Connecting...</span>
            </span>
          ) : isHealthy ? (
            <span className="flex items-center space-x-1.5 text-emerald-700 bg-emerald-50/60 border-emerald-200 px-2 py-0.5 rounded-full">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-[11px]">API: ONLINE</span>
            </span>
          ) : (
            <span className="flex items-center space-x-1.5 text-rose-700 bg-rose-50 border-rose-200 px-2 py-0.5 rounded-full">
              <span className="w-2 h-2 rounded-full bg-rose-500"></span>
              <span className="text-[11px]">API: STANDALONE</span>
            </span>
          )}
        </div>

        {/* API Docs Button */}
        <a
          href="http://127.0.0.1:8000/docs"
          target="_blank"
          rel="noreferrer"
          className="hidden md:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-medium transition-colors"
        >
          <Terminal className="w-3.5 h-3.5 text-blue-600" />
          <span>Docs</span>
          <ExternalLink className="w-3 h-3 text-slate-400" />
        </a>

        {/* Quick Scan Action Button */}
        {onQuickScanClick && (
          <button
            onClick={onQuickScanClick}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-lg shadow-sm transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Scan</span>
          </button>
        )}
      </div>
    </header>
  );
}
