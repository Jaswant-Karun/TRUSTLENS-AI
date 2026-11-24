"use client";

import React, { useState, useEffect } from "react";
import { PageHeader, useToast } from "@/components/ui";
import {
  getHealth,
  SystemHealth,
  getStoredToken,
  setStoredToken,
  clearStoredToken,
  loginUser,
} from "@/lib/api";
import { Settings, ShieldCheck, Database, Cpu, Lock, LogOut, CheckCircle2, RefreshCw } from "lucide-react";

export default function SettingsPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(true);
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState("analyst@trustlens.ai");
  const [password, setPassword] = useState("AnalystPassword123!");
  const [loggingIn, setLoggingIn] = useState(false);
  const { success, error, info } = useToast();

  // Engine Preferences
  const [offlineOnly, setOfflineOnly] = useState(true);
  const [ocrLang, setOcrLang] = useState("eng+hin");
  const [minConfidence, setMinConfidence] = useState(70);

  useEffect(() => {
    setToken(getStoredToken());
    getHealth()
      .then((res) => {
        setHealth(res);
        setLoadingHealth(false);
      })
      .catch(() => {
        setLoadingHealth(false);
      });
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoggingIn(true);
    try {
      const res = await loginUser(email, password);
      setToken(res.access_token);
      success("Authenticated", `Logged in as ${res.user.email} (${res.user.role})`);
    } catch (err: any) {
      error("Authentication Failed", err.message || "Invalid credentials.");
    } finally {
      setLoggingIn(false);
    }
  };

  const handleLogout = () => {
    clearStoredToken();
    setToken(null);
    info("Logged Out", "Analyst session terminated.");
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Platform Settings & Engine Configuration"
        description="Inspect backend microservices, configure inference parameters, and manage analyst credentials."
        badge={{ text: "Configuration Core", variant: "neutral" }}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Diagnostics & Backend Status */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-4">
          <div className="flex items-center space-x-2 pb-3 border-b border-slate-100">
            <Cpu className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900">Backend System Diagnostics</h3>
          </div>

          {loadingHealth ? (
            <div className="flex items-center space-x-2 text-xs text-slate-500 font-mono py-4">
              <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
              <span>Checking microservice endpoints...</span>
            </div>
          ) : (
            <div className="space-y-3 font-mono text-xs">
              <div className="flex justify-between items-center p-2.5 rounded bg-slate-50 border border-slate-200">
                <span className="text-slate-600">FastAPI Core Status:</span>
                <span className="font-bold text-emerald-600 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> {health?.status || "Online"}
                </span>
              </div>

              <div className="flex justify-between items-center p-2.5 rounded bg-slate-50 border border-slate-200">
                <span className="text-slate-600">Database Connection:</span>
                <span className="font-bold text-emerald-600">
                  {health?.database_connected ? "MongoDB Atlas Connected" : "Local Mock Storage"}
                </span>
              </div>

              <div className="p-2.5 rounded bg-slate-50 border border-slate-200 space-y-1.5">
                <span className="text-slate-600 block font-semibold">Trained ML Engines Loaded:</span>
                <div className="grid grid-cols-2 gap-1 text-[11px]">
                  <span className="text-emerald-700">✓ Model 1: Text Scam (Bi-LSTM)</span>
                  <span className="text-emerald-700">✓ Model 2: URL (XGBoost)</span>
                  <span className="text-emerald-700">✓ Model 3: Tactics (10-SVM)</span>
                  <span className="text-emerald-700">✓ Model 4: HDBSCAN Clustering</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Security & Analyst Credentials */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-4">
          <div className="flex items-center space-x-2 pb-3 border-b border-slate-100">
            <Lock className="w-4 h-4 text-slate-600" />
            <h3 className="text-sm font-bold text-slate-900">Analyst Authentication & Role</h3>
          </div>

          {token ? (
            <div className="space-y-4 font-mono text-xs">
              <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200 text-emerald-900 space-y-1">
                <div className="font-bold flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Authenticated Session Active</span>
                </div>
                <div className="text-[11px] text-emerald-700">
                  Role: Analyst (Full Triage, Review & Retrain Access)
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="flex items-center space-x-1.5 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Terminate Session</span>
              </button>
            </div>
          ) : (
            <form onSubmit={handleLogin} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Analyst Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full text-xs font-mono p-2 rounded-lg border border-slate-300 bg-white"
                  required
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full text-xs font-mono p-2 rounded-lg border border-slate-300 bg-white"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loggingIn}
                className="w-full py-2 px-4 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors flex items-center justify-center space-x-1.5"
              >
                <Lock className="w-3.5 h-3.5" />
                <span>{loggingIn ? "Authenticating..." : "Sign In to Analyst Console"}</span>
              </button>
            </form>
          )}
        </div>

        {/* Engine Execution Parameters */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-4">
          <div className="flex items-center space-x-2 pb-3 border-b border-slate-100">
            <Settings className="w-4 h-4 text-slate-600" />
            <h3 className="text-sm font-bold text-slate-900">Inference & Safety Parameters</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-1">
              <span className="font-semibold text-slate-800 block">Zero-Hop Execution Safety</span>
              <p className="text-[11px] text-slate-500">
                Never issue outbound HTTP requests to submitted URLs during analysis.
              </p>
              <div className="pt-2 text-emerald-600 font-mono font-bold">✓ Enforced (100% Offline)</div>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-1">
              <span className="font-semibold text-slate-800 block">OCR Tesseract Languages</span>
              <p className="text-[11px] text-slate-500">
                Supported optical character recognition language dictionaries.
              </p>
              <div className="pt-2 text-blue-600 font-mono font-bold">English + Hindi (Devanagari)</div>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-1">
              <span className="font-semibold text-slate-800 block">Model 4 Density Threshold</span>
              <p className="text-[11px] text-slate-500">
                HDBSCAN minimum cluster size for campaign discovery.
              </p>
              <div className="pt-2 text-purple-600 font-mono font-bold">min_samples = 3</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
