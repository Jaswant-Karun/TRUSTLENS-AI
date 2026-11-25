"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { CyberBackground } from "@/components/product/CyberBackground";
import { ProductHeader } from "@/components/product/ProductHeader";

interface AppShellProps {
  children: React.ReactNode;
}

const PUBLIC_OR_STANDALONE_ROUTES = new Set([
  "/",
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
  "/verify-email",
  "/profile",
]);

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();

  const getRouteInfo = (path: string) => {
    switch (path) {
      case "/analyze/text":
        return {
          title: "Multilingual Text Scam Analysis",
          breadcrumbs: [{ label: "Analysis" }, { label: "Message Scanner" }],
        };
      case "/analyze/url":
        return {
          title: "Zero-Hop Phishing URL Inspection",
          breadcrumbs: [{ label: "Analysis" }, { label: "URL Shield" }],
        };
      case "/analyze/image":
        return {
          title: "Screenshot Forensic OCR Analysis",
          breadcrumbs: [{ label: "Analysis" }, { label: "Screenshot Analyzer" }],
        };
      case "/investigation":
        return {
          title: "Multi-Modal Forensic Investigation Studio",
          breadcrumbs: [{ label: "Analysis" }, { label: "Comprehensive Studio" }],
        };
      case "/intelligence/tactics":
        return {
          title: "Social Engineering Tactic Intelligence",
          breadcrumbs: [{ label: "Intelligence" }, { label: "Tactic Taxonomy" }],
        };
      case "/intelligence/campaigns":
        return {
          title: "Scam Campaign Discovery & Attribution",
          breadcrumbs: [{ label: "Intelligence" }, { label: "Campaign Clusters" }],
        };
      case "/intelligence/threats":
        return {
          title: "Threat Indicators & IOC Intelligence",
          breadcrumbs: [{ label: "Intelligence" }, { label: "Threat Indicators" }],
        };
      case "/models":
        return {
          title: "ML Center & Model Governance",
          breadcrumbs: [{ label: "ML Center" }, { label: "Model Benchmarks" }],
        };
      case "/history":
        return {
          title: "Analysis History & Incident Audit Trail",
          breadcrumbs: [{ label: "Records" }, { label: "Analysis History" }],
        };
      case "/reports":
        return {
          title: "Community Threat Reports & Review",
          breadcrumbs: [{ label: "Records" }, { label: "Reports" }],
        };
      case "/settings":
        return {
          title: "Platform Settings & Configuration",
          breadcrumbs: [{ label: "Account" }, { label: "Settings" }],
        };
      case "/dashboard":
      default:
        return {
          title: "Threat Intelligence Overview",
          breadcrumbs: [{ label: "Overview" }, { label: "Intelligence Hub" }],
        };
    }
  };

  const isStandalone = PUBLIC_OR_STANDALONE_ROUTES.has(pathname);
  const isFullWidthWorkspace =
    pathname.startsWith("/investigations") ||
    pathname === "/threat-library" ||
    pathname === "/analytics";

  if (isStandalone) {
    return (
      <CyberBackground showHudFrame={true}>
        <ProductHeader />
        <main className="flex-1 flex flex-col">{children}</main>
        <footer className="mt-auto border-t border-[#481326]/60 bg-[#050306]/80 py-4 px-6 text-[11px] font-mono text-[#A1A1AA]">
          <div className="mx-auto flex max-w-7xl flex-col sm:flex-row items-center justify-between gap-2">
            <span>TRUSTLENS AI — Multilingual Digital Fraud Intelligence</span>
            <div className="flex items-center gap-4">
              <Link href="/analyze/text" className="hover:text-white">
                Scanner
              </Link>
              <Link href="/investigations" className="hover:text-white">
                Investigations
              </Link>
              <Link href="/reports" className="hover:text-white">
                Reports
              </Link>
            </div>
          </div>
        </footer>
      </CyberBackground>
    );
  }

  if (isFullWidthWorkspace) {
    return (
      <CyberBackground showHudFrame={false}>
        <ProductHeader />
        <div className="flex-1 w-full bg-[#050306]/90 text-white">{children}</div>
      </CyberBackground>
    );
  }

  const routeInfo = getRouteInfo(pathname);

  return (
    <CyberBackground showHudFrame={true}>
      <ProductHeader />
      <main className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto">
        <div className="mb-5 flex flex-col gap-1 border-b border-[#481326]/60 pb-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Breadcrumb items={routeInfo.breadcrumbs} />
            <h1 className="mt-1 font-mono text-lg sm:text-xl font-bold uppercase tracking-wider text-white">
              {routeInfo.title}
            </h1>
          </div>
          <div className="flex flex-wrap gap-2 text-xs font-mono">
            <Link
              href="/analyze/text"
              className="rounded border border-[#481326] bg-[#10070D] px-2.5 py-1 text-[#A1A1AA] hover:border-[#FF174F] hover:text-white"
            >
              Messages
            </Link>
            <Link
              href="/analyze/url"
              className="rounded border border-[#481326] bg-[#10070D] px-2.5 py-1 text-[#A1A1AA] hover:border-[#FF174F] hover:text-white"
            >
              URLs
            </Link>
            <Link
              href="/analyze/image"
              className="rounded border border-[#481326] bg-[#10070D] px-2.5 py-1 text-[#A1A1AA] hover:border-[#FF174F] hover:text-white"
            >
              OCR
            </Link>
            <Link
              href="/history"
              className="rounded border border-[#481326] bg-[#10070D] px-2.5 py-1 text-[#A1A1AA] hover:border-[#FF174F] hover:text-white"
            >
              History
            </Link>
          </div>
        </div>

        {children}
      </main>
    </CyberBackground>
  );
}
