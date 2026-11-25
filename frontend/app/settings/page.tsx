"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { PageHeader, useToast } from "@/components/ui";
import { GlowButton } from "@/components/product/GlowButton";
import {
  getHealth,
  SystemHealth,
  getStoredToken,
  getCurrentUser,
  logoutUser,
  UserProfile,
} from "@/lib/api";
import { Settings, Cpu, Lock, LogOut, CheckCircle2, RefreshCw } from "lucide-react";

export default function SettingsPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(true);
  const [user, setUser] = useState<UserProfile | null>(null);
  const { info } = useToast();

  useEffect(() => {
    if (getStoredToken()) {
      getCurrentUser()
        .then((u) => setUser(u))
        .catch(() => setUser(null));
    }
    getHealth()
      .then((res) => setHealth(res))
      .catch(() => setHealth(null))
      .finally(() => setLoadingHealth(false));
  }, []);

  const handleLogout = async () => {
    await logoutUser();
    setUser(null);
    info("Logged Out", "Session terminated.");
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Platform Settings & Engine Configuration"
        description="Inspect live backend diagnostics, active ML engines, and current authentication status."
        badge={{ text: "Configuration Core", variant: "neutral" }}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Diagnostics */}
        <div className="cyber-panel p-6 space-y-4">
          <div className="flex items-center space-x-2 pb-3 border-b border-[#481326]">
            <Cpu className="w-4 h-4 text-[#FF3D70]" />
            <h3 className="text-sm font-mono font-bold uppercase text-white">
              Backend System Diagnostics
            </h3>
          </div>

          {loadingHealth ? (
            <div className="flex items-center space-x-2 text-xs text-[#A1A1AA] font-mono py-4">
              <RefreshCw className="w-4 h-4 animate-spin text-[#FF174F]" />
              <span>Checking microservice endpoints...</span>
            </div>
          ) : (
            <div className="space-y-3 font-mono text-xs">
              <div className="flex justify-between items-center p-2.5 rounded bg-[#050306] border border-[#481326]">
                <span className="text-[#A1A1AA]">FastAPI Core Status:</span>
                <span className="font-bold text-[#00D68F] flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> {health?.status || "Online"}
                </span>
              </div>

              <div className="flex justify-between items-center p-2.5 rounded bg-[#050306] border border-[#481326]">
                <span className="text-[#A1A1AA]">Database Connection:</span>
                <span className="font-bold text-[#00D68F]">
                  {health?.database_connected ? "MongoDB Connected" : "Unavailable"}
                </span>
              </div>

              <div className="p-2.5 rounded bg-[#050306] border border-[#481326] space-y-1.5">
                <span className="text-[#A1A1AA] block font-semibold">Trained ML Engines:</span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 text-[11px] text-[#00D68F]">
                  <span>✓ Model 1: TF-IDF Calibrated LinearSVC</span>
                  <span>✓ Model 2: Zero-Hop URL (XGBoost)</span>
                  <span>✓ Model 3: Tactics (9-Label OvR SVM)</span>
                  <span>✓ Model 4: HDBSCAN Clustering</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Account Session */}
        <div className="cyber-panel p-6 space-y-4">
          <div className="flex items-center space-x-2 pb-3 border-b border-[#481326]">
            <Lock className="w-4 h-4 text-[#FF3D70]" />
            <h3 className="text-sm font-mono font-bold uppercase text-white">
              Authentication &amp; Session
            </h3>
          </div>

          {user ? (
            <div className="space-y-4 font-mono text-xs">
              <div className="p-3.5 bg-[#00D68F]/10 rounded-lg border border-[#00D68F]/40 text-[#00D68F] space-y-1">
                <div className="font-bold flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Authenticated as {user.email}</span>
                </div>
                <div className="text-[11px] text-[#A1A1AA]">Role: {user.role}</div>
              </div>

              <div className="flex flex-wrap gap-3">
                <Link href="/profile">
                  <GlowButton variant="primary" size="sm">Manage Profile &amp; Preferences</GlowButton>
                </Link>
                <GlowButton variant="secondary" size="sm" onClick={handleLogout}>
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Terminate Session</span>
                </GlowButton>
              </div>
            </div>
          ) : (
            <div className="space-y-4 text-xs text-[#A1A1AA]">
              <p>Sign in via the TRUSTLENS AI authentication portal to manage profile settings and sessions.</p>
              <div className="flex gap-3">
                <Link href="/login?next=/settings">
                  <GlowButton variant="primary" size="sm">SIGN IN</GlowButton>
                </Link>
                <Link href="/register">
                  <GlowButton variant="secondary" size="sm">CREATE ACCOUNT</GlowButton>
                </Link>
              </div>
            </div>
          )}
        </div>

        {/* Engine Execution Parameters */}
        <div className="lg:col-span-2 cyber-panel p-6 space-y-4">
          <div className="flex items-center space-x-2 pb-3 border-b border-[#481326]">
            <Settings className="w-4 h-4 text-[#FF3D70]" />
            <h3 className="text-sm font-mono font-bold uppercase text-white">
              Inference &amp; Safety Parameters
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="p-3.5 bg-[#050306] rounded-lg border border-[#481326] space-y-1">
              <span className="font-semibold text-white block">Zero-Hop Execution Safety</span>
              <p className="text-[11px] text-[#A1A1AA]">
                Never issue outbound HTTP requests to submitted URLs during analysis.
              </p>
              <div className="pt-2 text-[#00D68F] font-mono font-bold">✓ Enforced (Offline)</div>
            </div>

            <div className="p-3.5 bg-[#050306] rounded-lg border border-[#481326] space-y-1">
              <span className="font-semibold text-white block">OCR Tesseract Pipeline</span>
              <p className="text-[11px] text-[#A1A1AA]">
                Local OCR extraction before text &amp; tactic evaluation.
              </p>
              <div className="pt-2 text-[#FF3D70] font-mono font-bold">PNG / JPEG / WEBP (10 MB)</div>
            </div>

            <div className="p-3.5 bg-[#050306] rounded-lg border border-[#481326] space-y-1">
              <span className="font-semibold text-white block">Model 4 Clustering</span>
              <p className="text-[11px] text-[#A1A1AA]">
                HDBSCAN similarity clustering synced to MongoDB scam_campaigns.
              </p>
              <div className="pt-2 text-[#FFB020] font-mono font-bold">47 Active Clusters</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
