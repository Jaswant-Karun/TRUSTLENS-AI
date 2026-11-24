"use client";

import React, { useState } from "react";
import { usePathname } from "next/navigation";
import { Sidebar } from "@/components/ui/Sidebar";
import { TopNavbar } from "@/components/ui/TopNavbar";
import { Breadcrumb } from "@/components/ui/Breadcrumb";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  // Derive dynamic page metadata and breadcrumbs from pathname
  const getRouteInfo = (path: string) => {
    switch (path) {
      case "/analyze/text":
        return {
          title: "Multilingual Text Scam Analysis",
          breadcrumbs: [{ label: "Analysis" }, { label: "Text Scam Detection" }],
        };
      case "/analyze/url":
        return {
          title: "Zero-Hop Phishing URL Inspection",
          breadcrumbs: [{ label: "Analysis" }, { label: "URL Inspection" }],
        };
      case "/analyze/image":
        return {
          title: "Screenshot Forensic OCR Analysis",
          breadcrumbs: [{ label: "Analysis" }, { label: "Screenshot OCR" }],
        };
      case "/investigation":
        return {
          title: "Multi-Modal Forensic Investigation Studio",
          breadcrumbs: [{ label: "Analysis" }, { label: "Comprehensive Studio" }],
        };
      case "/intelligence/tactics":
        return {
          title: "Social Engineering Tactic Intelligence",
          breadcrumbs: [{ label: "Intelligence" }, { label: "10-Tactic Taxonomy" }],
        };
      case "/intelligence/campaigns":
        return {
          title: "Scam Campaign Discovery & Attribution",
          breadcrumbs: [{ label: "Intelligence" }, { label: "HDBSCAN Clusters" }],
        };
      case "/intelligence/threats":
        return {
          title: "Threat Indicators & IOC Intelligence",
          breadcrumbs: [{ label: "Intelligence" }, { label: "Threat Indicators" }],
        };
      case "/models":
        return {
          title: "ML Center & Model Governance",
          breadcrumbs: [{ label: "ML Center" }, { label: "Model Performance & Benchmarks" }],
        };
      case "/history":
        return {
          title: "Analysis History & Incident Audit Trail",
          breadcrumbs: [{ label: "Records" }, { label: "Analysis History" }],
        };
      case "/reports":
        return {
          title: "Community Threat Reports & Review",
          breadcrumbs: [{ label: "Records" }, { label: "Community Reports" }],
        };
      case "/settings":
        return {
          title: "Platform Settings & Engine Configuration",
          breadcrumbs: [{ label: "Settings" }, { label: "System Config" }],
        };
      case "/dashboard":
      case "/":
      default:
        return {
          title: "SOC Threat Intelligence Cockpit",
          breadcrumbs: [{ label: "Overview" }, { label: "Executive Dashboard" }],
        };
    }
  };

  const routeInfo = getRouteInfo(pathname);

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 flex">
      {/* 1. Persistent Dark Navy Sidebar */}
      <Sidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
        isMobileOpen={isMobileOpen}
        onMobileClose={() => setIsMobileOpen(false)}
      />

      {/* Main Content Layout Container */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${
          isCollapsed ? "lg:pl-20" : "lg:pl-64"
        }`}
      >
        {/* 2. Top Navigation Bar */}
        <TopNavbar
          onOpenMobileSidebar={() => setIsMobileOpen(true)}
          title={routeInfo.title}
        />

        {/* 3. Main Page Content Canvas */}
        <main className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {/* Dynamic Breadcrumb Navigation */}
          <div className="mb-4">
            <Breadcrumb items={routeInfo.breadcrumbs} />
          </div>

          {/* Page Body Render */}
          {children}
        </main>

        {/* Persistent Enterprise Footer */}
        <footer className="mt-auto py-4 px-6 border-t border-slate-200/80 bg-white text-xs font-mono text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>TRUSTLENS AI Platform | Production Core v1.0.0</span>
          </div>
          <div className="text-slate-400">
            Multilingual Fraud Intelligence & Deception Attribution
          </div>
        </footer>
      </div>
    </div>
  );
}
