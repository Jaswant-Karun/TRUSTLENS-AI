"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Shield,
  LayoutDashboard,
  MessageSquare,
  Globe,
  Image as ImageIcon,
  Crosshair,
  Fingerprint,
  Network,
  AlertTriangle,
  Cpu,
  History,
  Users,
  Settings,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Activity,
  Layers,
} from "lucide-react";

interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  isMobileOpen: boolean;
  onMobileClose: () => void;
}

interface NavSection {
  title: string;
  items: {
    label: string;
    href: string;
    icon: React.ComponentType<{ className?: string }>;
    badge?: string;
    badgeColor?: string;
  }[];
}

export function Sidebar({
  isCollapsed,
  onToggleCollapse,
  isMobileOpen,
  onMobileClose,
}: SidebarProps) {
  const pathname = usePathname();

  const navigationSections: NavSection[] = [
    {
      title: "Overview",
      items: [
        {
          label: "Dashboard",
          href: "/dashboard",
          icon: LayoutDashboard,
          badge: "Live",
          badgeColor: "bg-emerald-950 text-emerald-400 border-emerald-800",
        },
        {
          label: "Investigation Workspace",
          href: "/investigations/INV-2026-KYC-11",
          icon: Network,
          badge: "ThreatQ UI",
          badgeColor: "bg-blue-950 text-cyan-300 border-blue-800",
        },
      ],
    },
    {
      title: "Analysis",
      items: [
        {
          label: "Text Analysis",
          href: "/analyze/text",
          icon: MessageSquare,
          badge: "M1+M3",
          badgeColor: "bg-blue-950 text-blue-400 border-blue-800",
        },
        {
          label: "URL Analysis",
          href: "/analyze/url",
          icon: Globe,
          badge: "Zero-Hop",
          badgeColor: "bg-cyan-950 text-cyan-400 border-cyan-800",
        },
        {
          label: "Screenshot Analysis",
          href: "/analyze/image",
          icon: ImageIcon,
          badge: "OCR",
          badgeColor: "bg-purple-950 text-purple-400 border-purple-800",
        },
        {
          label: "Comprehensive Investigation",
          href: "/investigation",
          icon: Crosshair,
          badge: "Multi-Vector",
          badgeColor: "bg-rose-950 text-rose-400 border-rose-800",
        },
      ],
    },
    {
      title: "Intelligence",
      items: [
        {
          label: "Tactic Intelligence",
          href: "/intelligence/tactics",
          icon: Fingerprint,
          badge: "10 Tactics",
          badgeColor: "bg-amber-950 text-amber-400 border-amber-800",
        },
        {
          label: "Campaign Intelligence",
          href: "/intelligence/campaigns",
          icon: Network,
          badge: "HDBSCAN",
          badgeColor: "bg-teal-950 text-teal-400 border-teal-800",
        },
        {
          label: "Threat Intelligence",
          href: "/intelligence/threats",
          icon: AlertTriangle,
        },
      ],
    },
    {
      title: "ML Center",
      items: [
        {
          label: "Model Performance",
          href: "/models",
          icon: Cpu,
          badge: "98% F1",
          badgeColor: "bg-emerald-950 text-emerald-400 border-emerald-800",
        },
      ],
    },
    {
      title: "Records",
      items: [
        {
          label: "Analysis History",
          href: "/history",
          icon: History,
        },
        {
          label: "Community Reports",
          href: "/reports",
          icon: Users,
        },
      ],
    },
    {
      title: "Settings",
      items: [
        {
          label: "Settings",
          href: "/settings",
          icon: Settings,
        },
      ],
    },
  ];

  const isItemActive = (href: string) => {
    if (href === "/dashboard") {
      return pathname === "/dashboard" || pathname === "/";
    }
    return pathname === href || pathname.startsWith(href + "/");
  };

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isMobileOpen && (
        <div
          onClick={onMobileClose}
          className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-40 lg:hidden"
        />
      )}

      {/* Main Persistent Sidebar Panel */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col bg-[#0b1329] border-r border-slate-800/80 transition-all duration-300 ${
          isCollapsed ? "w-20" : "w-64"
        } ${isMobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}
      >
        {/* Brand Header */}
        <div className="h-16 px-4 flex items-center justify-between border-b border-slate-800">
          <Link href="/dashboard" className="flex items-center space-x-3 overflow-hidden">
            <div className="w-9 h-9 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0 shadow-sm">
              <Shield className="w-5 h-5 text-sky-400" />
            </div>
            {!isCollapsed && (
              <div className="flex flex-col min-w-0">
                <span className="font-bold text-sm tracking-wider text-white font-mono flex items-center gap-1.5">
                  TRUSTLENS<span className="text-cyan-400">AI</span>
                </span>
                <span className="text-[10px] text-slate-400 uppercase tracking-widest font-mono">
                  SOC Intelligence
                </span>
              </div>
            )}
          </Link>

          {/* Collapse Toggle Button (Desktop) */}
          <button
            onClick={onToggleCollapse}
            className="hidden lg:flex p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors"
            aria-label={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Scrollable Navigation Items */}
        <div className="flex-1 py-4 px-3 overflow-y-auto space-y-6">
          {navigationSections.map((section, sIdx) => (
            <div key={sIdx} className="space-y-1">
              {!isCollapsed && (
                <div className="px-3 pb-1.5 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold">
                  {section.title}
                </div>
              )}
              {isCollapsed && sIdx > 0 && <div className="border-t border-slate-800/60 my-2"></div>}

              {section.items.map((item) => {
                const Icon = item.icon;
                const active = isItemActive(item.href);

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => {
                      if (isMobileOpen) onMobileClose();
                    }}
                    title={isCollapsed ? item.label : undefined}
                    className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all group ${
                      active
                        ? "bg-blue-600/20 text-cyan-300 font-semibold border border-blue-500/30 shadow-sm"
                        : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/50 border border-transparent"
                    }`}
                  >
                    <div className="flex items-center space-x-3 min-w-0">
                      <Icon
                        className={`w-4 h-4 shrink-0 transition-colors ${
                          active ? "text-cyan-400" : "text-slate-400 group-hover:text-slate-200"
                        }`}
                      />
                      {!isCollapsed && <span className="truncate">{item.label}</span>}
                    </div>

                    {!isCollapsed && item.badge && (
                      <span
                        className={`text-[9px] font-mono px-1.5 py-0.5 rounded border uppercase tracking-wider shrink-0 ${
                          item.badgeColor || "bg-slate-800 text-slate-300 border-slate-700"
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          ))}
        </div>

        {/* Bottom Engine Status & System Info */}
        <div className="p-3 border-t border-slate-800 bg-[#080d1c]">
          {!isCollapsed ? (
            <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-[11px] font-mono">
                <span className="flex items-center space-x-1.5 text-slate-300">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>Engine Online</span>
                </span>
                <span className="text-[10px] text-cyan-400 font-semibold">v1.0.0</span>
              </div>
              <div className="text-[10px] text-slate-400 font-mono">
                Models: M1 (Text) • M2 (URL) • M3 (Tactics) • M4 (Clustering)
              </div>
            </div>
          ) : (
            <div className="flex justify-center" title="Engine Online v1.0.0">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
