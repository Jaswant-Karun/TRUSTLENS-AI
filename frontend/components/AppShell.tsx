"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Lock } from "lucide-react";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { CyberBackground } from "@/components/product/CyberBackground";
import { ProductHeader } from "@/components/product/ProductHeader";
import { NeonFrame } from "@/components/product/NeonFrame";
import { GlowButton } from "@/components/product/GlowButton";
import { AndroidShellBridge } from "@/components/android/AndroidShellBridge";
import { getStoredToken } from "@/lib/api";

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

const AUTH_REQUIRED_ROUTES = new Set(["/history"]);

const QUICK_NAV_LINKS = [
  { href: "/analyze/text", label: "Messages" },
  { href: "/analyze/url", label: "URLs" },
  { href: "/analyze/image", label: "OCR" },
  { href: "/history", label: "History" },
  { href: "/investigations", label: "Investigations" },
  { href: "/reports", label: "Reports" },
];

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const [hasToken, setHasToken] = useState<boolean | null>(null);

  useEffect(() => {
    setHasToken(Boolean(getStoredToken()));
  }, [pathname]);

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

  const isAuthBlocked = AUTH_REQUIRED_ROUTES.has(pathname) && hasToken === false;

  if (isStandalone) {
    return (
      <CyberBackground showHudFrame={true}>
        <ProductHeader />
        <main className="flex-1 flex flex-col pb-20 md:pb-0">{children}</main>
        <footer className="mt-auto border-t border-[#481326]/60 bg-[#050306]/80 py-4 px-6 pb-20 md:pb-4 text-[11px] font-mono text-[#A1A1AA]">
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
        <AndroidShellBridge onAuthHydrated={() => setHasToken(Boolean(getStoredToken()))} />
      </CyberBackground>
    );
  }

  if (isFullWidthWorkspace) {
    return (
      <CyberBackground showHudFrame={false}>
        <ProductHeader />
        <div className="flex-1 w-full bg-[#050306]/90 pb-20 md:pb-0 text-white">{children}</div>
        <AndroidShellBridge onAuthHydrated={() => setHasToken(Boolean(getStoredToken()))} />
      </CyberBackground>
    );
  }

  const routeInfo = getRouteInfo(pathname);

  return (
    <CyberBackground showHudFrame={true}>
      <ProductHeader />
      <main className="flex-1 p-4 pb-24 md:p-6 lg:p-8 max-w-7xl w-full mx-auto">
        <div className="mb-5 flex flex-col gap-3 border-b border-[#481326]/60 pb-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <Breadcrumb items={routeInfo.breadcrumbs} />
            <h1 className="mt-1 font-mono text-lg sm:text-xl font-bold uppercase tracking-wider text-white">
              {routeInfo.title}
            </h1>
          </div>
          <nav aria-label="Quick workflow navigation" className="flex flex-wrap gap-2 text-xs font-mono">
            {QUICK_NAV_LINKS.map((item) => {
              const active = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  className={`rounded border px-2.5 py-1 transition-colors ${
                    active
                      ? "border-[#FF174F] bg-[#FF174F]/15 text-white font-semibold"
                      : "border-[#481326] bg-[#10070D] text-[#A1A1AA] hover:border-[#FF174F]/60 hover:text-white"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {isAuthBlocked ? (
          <div className="mx-auto max-w-md py-12">
            <NeonFrame className="p-6 text-center space-y-4">
              <Lock className="mx-auto h-9 w-9 text-[#FF3D70]" />
              <h2 className="font-mono text-base font-bold uppercase tracking-wider text-white">
                Authentication Required
              </h2>
              <p className="text-xs text-[#A1A1AA]">
                Sign in to access your personal scan history and protected records.
              </p>
              <div className="flex justify-center gap-3">
                <Link href={`/login?next=${encodeURIComponent(pathname)}`}>
                  <GlowButton variant="primary" size="sm">SIGN IN</GlowButton>
                </Link>
                <Link href="/register">
                  <GlowButton variant="secondary" size="sm">GET STARTED</GlowButton>
                </Link>
              </div>
            </NeonFrame>
          </div>
        ) : (
          children
        )}
      </main>
      <AndroidShellBridge onAuthHydrated={() => setHasToken(Boolean(getStoredToken()))} />
    </CyberBackground>
  );
}
