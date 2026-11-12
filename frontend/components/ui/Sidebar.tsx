"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Shield,
  LayoutDashboard,
  Search,
  Network,
  History,
  Cpu,
  FileText,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Activity,
  CheckCircle2,
} from "lucide-react";

interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  isMobileOpen: boolean;
  onMobileClose: () => void;
  activeTab?: string;
  onSelectTab?: (tab: string) => void;
}

export function Sidebar({
  isCollapsed,
  onToggleCollapse,
  isMobileOpen,
  onMobileClose,
  activeTab,
  onSelectTab,
}: SidebarProps) {
  const pathname = usePathname();

  const navItems = [
    {
      id: "overview",
      label: "SOC Overview",
      href: "/",
      icon: LayoutDashboard,
      badge: "Live",
    },
    {
      id: "scan",
      label: "Threat Workbench",
      href: "/#scanner",
      icon: Search,
      badge: "Multi-Vector",
    },
    {
      id: "campaigns",
      label: "Campaign Intelligence",
      href: "/#campaigns",
      icon: Network,
      badge: "47 Clusters",
    },
    {
      id: "history",
      label: "Incident Logs",
      href: "/#history",
      icon: History,
    },
    {
      id: "models",
      label: "Model Governance",
      href: "/#models",
      icon: Cpu,
      badge: "98% F1",
    },
  ];

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isMobileOpen && (
        <div
          onClick={onMobileClose}
          className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-40 lg:hidden"
        />
      )}

      {/* Main Sidebar Panel */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col bg-[#0b1329] border-r border-slate-800/80 transition-all duration-300 ${
          isCollapsed ? "w-20" : "w-64"
        } ${isMobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}
      >
        {/* Brand Header */}
        <div className="h-16 px-4 flex items-center justify-between border-b border-slate-800">
          <Link href="/" className="flex items-center space-x-3 overflow-hidden">
            <div className="w-9 h-9 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0 shadow-sm">
              <Shield className="w-5 h-5 text-sky-400" />
            </div>
            {!isCollapsed && (
              <div className="flex flex-col min-w-0">
                <div className="flex items-center space-x-1.5">
                  <span className="font-bold text-sm tracking-wider text-white">TRUSTLENS</span>
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-sky-500/20 text-sky-300 font-mono font-semibold border border-sky-500/30">
                    AI
                  </span>
                </div>
                <span className="text-[11px] text-slate-400 truncate font-mono">Fraud Intelligence</span>
              </div>
            )}
          </Link>

          {/* Desktop Collapse Toggle */}
          <button
            onClick={onToggleCollapse}
            className="hidden lg:flex p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Items List */}
        <div className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <div className={`px-2 pb-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold ${isCollapsed ? "text-center" : ""}`}>
            {isCollapsed ? "•••" : "Platform Navigation"}
          </div>

          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab ? activeTab === item.id : pathname === item.href;

            return (
              <button
                key={item.id}
                onClick={() => {
                  if (onSelectTab) onSelectTab(item.id);
                  onMobileClose();
                }}
                className={`w-full flex items-center rounded-lg px-3 py-2.5 text-xs font-medium transition-all ${
                  isActive
                    ? "bg-blue-600 text-white shadow-sm font-semibold"
                    : "text-slate-300 hover:bg-slate-800/80 hover:text-white"
                } ${isCollapsed ? "justify-center" : "justify-between"}`}
                title={isCollapsed ? item.label : undefined}
              >
                <div className="flex items-center space-x-3 min-w-0">
                  <Icon className={`w-4 h-4 shrink-0 ${isActive ? "text-white" : "text-slate-400"}`} />
                  {!isCollapsed && <span className="truncate">{item.label}</span>}
                </div>
                {!isCollapsed && item.badge && (
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-medium ${
                      isActive
                        ? "bg-blue-700 text-blue-100"
                        : "bg-slate-800 text-slate-400 border border-slate-700"
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Model Readiness Status Box */}
        {!isCollapsed && (
          <div className="p-3 mx-3 mb-3 rounded-lg bg-slate-900/90 border border-slate-800 text-[11px] font-mono space-y-2">
            <div className="flex items-center justify-between text-slate-400">
              <span>ML Engine Status</span>
              <span className="flex items-center space-x-1 text-emerald-400 font-semibold">
                <CheckCircle2 className="w-3 h-3" />
                <span>4 / 4 Online</span>
              </span>
            </div>
            <div className="grid grid-cols-2 gap-1 text-[10px] text-slate-500">
              <span className="truncate">• M1: Text (97.8%)</span>
              <span className="truncate">• M2: URL (98.8%)</span>
              <span className="truncate">• M3: Tactics (10)</span>
              <span className="truncate">• M4: Clusters (47)</span>
            </div>
          </div>
        )}

        {/* User / Host Footer */}
        <div className="p-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center space-x-2.5 min-w-0">
            <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-white text-[11px] shrink-0">
              TL
            </div>
            {!isCollapsed && (
              <div className="truncate">
                <div className="text-white font-medium text-xs truncate">SOC Analyst</div>
                <div className="text-[10px] text-slate-500 font-mono truncate">trustlens-node-1</div>
              </div>
            )}
          </div>
          {!isCollapsed && (
            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="p-1.5 text-slate-400 hover:text-white rounded hover:bg-slate-800 transition-colors"
              title="FastAPI Swagger Documentation"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>
      </aside>
    </>
  );
}
