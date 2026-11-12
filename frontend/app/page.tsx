"use client";

import React, { useState } from "react";
import {
  Sidebar,
  TopNavbar,
  Breadcrumb,
  PageHeader,
  ConfirmDialog,
  useToast,
} from "@/components/ui";
import TelemetryCards from "@/components/TelemetryCards";
import ScanWorkbench from "@/components/ScanWorkbench";
import KillChainGraph from "@/components/KillChainGraph";
import IncidentFeed from "@/components/IncidentFeed";
import ModelGovernancePanel from "@/components/ModelGovernancePanel";
import { ShieldCheck, Plus, RefreshCw } from "lucide-react";

export default function DashboardPage() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const { info } = useToast();

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const getBreadcrumbs = () => {
    switch (activeTab) {
      case "scan":
        return [{ label: "Operations" }, { label: "Multi-Modal Threat Workbench" }];
      case "campaigns":
        return [{ label: "Intelligence" }, { label: "Campaign Discovery Graph" }];
      case "history":
        return [{ label: "Audit" }, { label: "Incident Detection Logs" }];
      case "models":
        return [{ label: "Governance" }, { label: "ML Evaluation & Confusion Matrix" }];
      default:
        return [{ label: "Dashboard" }, { label: "SOC Intelligence Overview" }];
    }
  };

  const getPageHeader = () => {
    switch (activeTab) {
      case "scan":
        return {
          title: "Multi-Modal Threat Workbench",
          description: "Zero-hop lexical URL inspection, multilingual SMS/WhatsApp analysis, and screenshot OCR forensic decomposition.",
          badge: { text: "Models 1, 2, 3 Active", variant: "blue" as const },
        };
      case "campaigns":
        return {
          title: "Scam Campaign Intelligence & Attribution",
          description: "Unsupervised HDBSCAN density clustering linking isolated deceptive communications into coordinated attack clusters.",
          badge: { text: "Model 4: 47 Clusters", variant: "amber" as const },
        };
      case "history":
        return {
          title: "Incident Telemetry & Audit Logs",
          description: "Complete chronological log of processed digital communications, assigned threat levels, and remedial actions.",
          badge: { text: "Real-time Telemetry", variant: "neutral" as const },
        };
      case "models":
        return {
          title: "Model Governance & Held-Out ML Evaluation",
          description: "Rigorous verification metrics: held-out confusion matrices, F1 scores, ROC-AUC, and SHAP feature importances.",
          badge: { text: "100% Production Verified", variant: "green" as const },
        };
      default:
        return {
          title: "SOC Threat Intelligence Cockpit",
          description: "Real-time deception detection, multi-vector threat scoring, and forensic explainability across digital channels.",
          badge: { text: "Enterprise Edition", variant: "blue" as const },
        };
    }
  };

  const header = getPageHeader();

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 flex">
      {/* 1. Dark Navy Collapsible Sidebar */}
      <Sidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
        isMobileOpen={isMobileOpen}
        onMobileClose={() => setIsMobileOpen(false)}
        activeTab={activeTab}
        onSelectTab={handleTabChange}
      />

      {/* Main Content Layout Container */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${
          isCollapsed ? "lg:pl-20" : "lg:pl-64"
        }`}
      >
        {/* 2. Crisp White Top Navigation Bar */}
        <TopNavbar
          onOpenMobileSidebar={() => setIsMobileOpen(true)}
          onQuickScanClick={() => {
            setActiveTab("scan");
            info("Switched to Threat Workbench", "Submit a message, URL, or screenshot to scan.");
          }}
          title={header.title}
        />

        {/* 3. Main Body Canvas */}
        <main className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {/* Breadcrumbs */}
          <Breadcrumb items={getBreadcrumbs()} />

          {/* Page Header */}
          <PageHeader
            title={header.title}
            description={header.description}
            badge={header.badge}
            actions={
              activeTab !== "scan" ? (
                <button
                  onClick={() => setActiveTab("scan")}
                  className="flex items-center space-x-1.5 px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Launch New Scan</span>
                </button>
              ) : undefined
            }
          />

          {/* Tab 1: Overview Cockpit */}
          {activeTab === "overview" && (
            <div className="space-y-6">
              <TelemetryCards />
              <ScanWorkbench id="scanner" />
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <KillChainGraph id="campaigns" />
                <ModelGovernancePanel id="models" />
              </div>
              <IncidentFeed id="history" />
            </div>
          )}

          {/* Tab 2: Dedicated Threat Workbench */}
          {activeTab === "scan" && (
            <div className="space-y-6">
              <ScanWorkbench id="scanner" />
            </div>
          )}

          {/* Tab 3: Dedicated Campaign Intelligence */}
          {activeTab === "campaigns" && (
            <div className="space-y-6">
              <KillChainGraph id="campaigns" />
            </div>
          )}

          {/* Tab 4: Dedicated Incident Logs */}
          {activeTab === "history" && (
            <div className="space-y-6">
              <IncidentFeed id="history" />
            </div>
          )}

          {/* Tab 5: Dedicated Model Governance & ML Evaluation */}
          {activeTab === "models" && (
            <div className="space-y-6">
              <ModelGovernancePanel id="models" />
            </div>
          )}
        </main>

        {/* Professional Footer */}
        <footer className="mt-auto py-5 px-6 border-t border-slate-200/80 bg-white text-xs font-mono text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>TRUSTLENS AI Platform | Machine Learning Security Core v1.0.0</span>
          </div>
          <div className="text-slate-400">
            Multilingual Fraud Intelligence & Deception Attribution
          </div>
        </footer>
      </div>

      {/* Confirmation Dialog Demo */}
      <ConfirmDialog
        isOpen={isConfirmOpen}
        title="Confirm Operational Action"
        message="Are you sure you want to proceed with this threat response action?"
        onConfirm={() => {
          setIsConfirmOpen(false);
          info("Action Confirmed", "Threat response initiated.");
        }}
        onCancel={() => setIsConfirmOpen(false)}
      />
    </div>
  );
}
