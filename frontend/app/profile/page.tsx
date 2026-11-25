"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  AlertCircle,
  Bell,
  CheckCircle2,
  Clock,
  FolderSearch,
  Globe,
  History,
  LogOut,
  Save,
  Shield,
  User as UserIcon,
} from "lucide-react";
import {
  getCurrentUser,
  getStoredToken,
  getUserSessions,
  logoutUser,
  updateUserProfile,
  UserProfile,
} from "@/lib/api";
import { NeonFrame } from "@/components/product/NeonFrame";
import { GlowButton } from "@/components/product/GlowButton";

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [sessions, setSessions] = useState<
    Array<{ audit_id: string; action: string; client_ip?: string; timestamp: string }>
  >([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Editable form state
  const [fullName, setFullName] = useState("");
  const [preferredLanguage, setPreferredLanguage] = useState("en");
  const [primaryFocus, setPrimaryFocus] = useState("message_scanning");
  const [threatAlertsOptIn, setThreatAlertsOptIn] = useState(false);
  const [emailNotifications, setEmailNotifications] = useState(false);
  const [inAppNotifications, setInAppNotifications] = useState(true);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setLoading(false);
      return;
    }
    Promise.all([getCurrentUser(), getUserSessions().catch(() => ({ sessions: [] }))])
      .then(([profile, sessData]) => {
        setUser(profile);
        setFullName(profile.full_name || "");
        const prefs = profile.onboarding_preferences || {};
        setPreferredLanguage(prefs.preferred_language || "en");
        setPrimaryFocus(prefs.primary_focus || "message_scanning");
        setThreatAlertsOptIn(Boolean(prefs.threat_alerts_opt_in));
        setEmailNotifications(Boolean(prefs.email_notifications));
        setInAppNotifications(prefs.in_app_notifications !== false);
        setSessions(sessData.sessions || []);
      })
      .catch(() => {
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    if (fullName.trim().length < 2) {
      setError("Full name must be at least 2 characters.");
      return;
    }
    setSaving(true);
    try {
      const updated = await updateUserProfile({
        full_name: fullName.trim(),
        preferred_language: preferredLanguage,
        primary_focus: primaryFocus,
        threat_alerts_opt_in: threatAlertsOptIn,
        email_notifications: emailNotifications,
        in_app_notifications: inAppNotifications,
      });
      setUser(updated);
      setSuccess("Profile and preferences saved.");
    } catch (err: any) {
      setError(err?.message || "Failed to save profile changes.");
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    await logoutUser();
    router.push("/");
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 font-mono text-xs text-[#A1A1AA]">
        Loading authenticated profile...
      </div>
    );
  }

  if (!user) {
    return (
      <div className="mx-auto flex max-w-md flex-1 items-center justify-center px-4 py-12">
        <NeonFrame className="w-full p-6 sm:p-8 text-center">
          <UserIcon className="mx-auto mb-3 h-10 w-10 text-[#FF3D70]" />
          <h1 className="font-mono text-lg font-bold uppercase tracking-wider text-white">
            Authentication Required
          </h1>
          <p className="mt-2 text-xs text-[#A1A1AA]">
            Sign in to view and manage your TRUSTLENS AI profile, preferences,
            and active sessions.
          </p>
          <div className="mt-6 flex gap-3 justify-center">
            <Link href="/login?next=/profile">
              <GlowButton variant="primary">SIGN IN</GlowButton>
            </Link>
            <Link href="/register">
              <GlowButton variant="secondary">SIGN UP</GlowButton>
            </Link>
          </div>
        </NeonFrame>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-5xl px-4 py-8 sm:px-6 space-y-6">
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {/* Identity Card */}
        <NeonFrame className="p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-3.5">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-[#FF174F] to-[#C2185B] font-mono text-lg font-bold text-white shadow-[0_0_16px_rgba(255,23,79,0.4)]">
                {(user.full_name || user.email || "U")[0].toUpperCase()}
              </div>
              <div className="min-w-0">
                <h1 className="truncate font-mono text-sm font-bold uppercase tracking-wider text-white">
                  {user.full_name || "TRUSTLENS USER"}
                </h1>
                <p className="truncate text-xs text-[#A1A1AA]">{user.email}</p>
              </div>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              <span className="inline-flex items-center gap-1.5 rounded-full border border-[#00D68F]/40 bg-[#00D68F]/10 px-2.5 py-1 text-[10px] font-mono text-[#00D68F]">
                <CheckCircle2 className="h-3 w-3" />
                ACTIVE SESSION
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-[#FF174F]/15 border border-[#481326] px-2.5 py-1 font-mono text-[10px] uppercase text-[#FF3D70]">
                <Shield className="h-3 w-3" />
                {user.role}
              </span>
            </div>

            <div className="mt-5 space-y-2 text-xs text-[#A1A1AA]">
              <div className="flex justify-between">
                <span>Email Verified</span>
                <span className={user.email_verified ? "text-[#00D68F]" : "text-[#FFB020]"}>
                  {user.email_verified ? "Verified" : "Pending"}
                </span>
              </div>
              <div className="flex justify-between">
                <span>User ID</span>
                <span className="font-mono text-[11px] text-white truncate max-w-[140px]">
                  {user.user_id}
                </span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-[#481326] space-y-2.5">
            <div className="flex gap-2">
              <Link href="/history" className="flex-1">
                <GlowButton variant="secondary" size="sm" className="w-full">
                  <History className="h-3.5 w-3.5" />
                  HISTORY
                </GlowButton>
              </Link>
              <Link href="/investigations" className="flex-1">
                <GlowButton variant="secondary" size="sm" className="w-full">
                  <FolderSearch className="h-3.5 w-3.5" />
                  CASES
                </GlowButton>
              </Link>
            </div>
            <GlowButton variant="ghost" size="sm" className="w-full border border-[#481326]" onClick={handleLogout}>
              <LogOut className="h-3.5 w-3.5" />
              SIGN OUT
            </GlowButton>
          </div>
        </NeonFrame>

        {/* Editable Profile & Preferences */}
        <NeonFrame className="p-6 md:col-span-2">
          <h2 className="font-mono text-xs font-bold uppercase tracking-widest text-white border-b border-[#481326] pb-3">
            Profile, Language &amp; Notification Settings
          </h2>

          {error && (
            <div className="mt-4 flex items-center gap-2 rounded-lg border border-[#FF174F]/60 bg-[#FF174F]/10 p-3 text-xs text-[#FF3D70]">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
          {success && (
            <div className="mt-4 flex items-center gap-2 rounded-lg border border-[#00D68F]/50 bg-[#00D68F]/10 p-3 text-xs text-[#00D68F]">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              <span>{success}</span>
            </div>
          )}

          <form onSubmit={handleSave} className="mt-4 space-y-4">
            <div>
              <label htmlFor="profile-name" className="mb-1.5 block font-mono text-[11px] uppercase text-[#A1A1AA]">
                Full Name
              </label>
              <input
                id="profile-name"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="cyber-input"
                required
              />
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="profile-lang" className="mb-1.5 flex items-center gap-1.5 font-mono text-[11px] uppercase text-[#A1A1AA]">
                  <Globe className="h-3.5 w-3.5 text-[#FF3D70]" />
                  <span>Language Preference</span>
                </label>
                <select
                  id="profile-lang"
                  value={preferredLanguage}
                  onChange={(e) => setPreferredLanguage(e.target.value)}
                  className="cyber-select w-full"
                >
                  <option value="en">English</option>
                  <option value="hi">Hindi (Devanagari)</option>
                  <option value="hinglish">Hinglish</option>
                </select>
              </div>
              <div>
                <label htmlFor="profile-focus" className="mb-1.5 block font-mono text-[11px] uppercase text-[#A1A1AA]">
                  Default Workspace Focus
                </label>
                <select
                  id="profile-focus"
                  value={primaryFocus}
                  onChange={(e) => setPrimaryFocus(e.target.value)}
                  className="cyber-select w-full"
                >
                  <option value="message_scanning">Message Scanner</option>
                  <option value="url_shield">URL Shield</option>
                  <option value="investigations">Investigations</option>
                </select>
              </div>
            </div>

            <div className="rounded-lg border border-[#481326] bg-[#050306]/70 p-4 space-y-2.5">
              <div className="flex items-center gap-1.5 font-mono text-[10px] font-bold uppercase tracking-wider text-[#FF3D70]">
                <Bell className="h-3.5 w-3.5" />
                <span>Notification Preferences</span>
              </div>
              <label className="flex items-center gap-2 text-xs text-[#A1A1AA] cursor-pointer">
                <input
                  type="checkbox"
                  checked={inAppNotifications}
                  onChange={(e) => setInAppNotifications(e.target.checked)}
                  className="h-4 w-4 accent-[#FF174F]"
                />
                <span>In-app analysis &amp; investigation notifications</span>
              </label>
              <label className="flex items-center gap-2 text-xs text-[#A1A1AA] cursor-pointer">
                <input
                  type="checkbox"
                  checked={emailNotifications}
                  onChange={(e) => setEmailNotifications(e.target.checked)}
                  className="h-4 w-4 accent-[#FF174F]"
                />
                <span>Email security summaries (when mail delivery is enabled)</span>
              </label>
              <label className="flex items-center gap-2 text-xs text-[#A1A1AA] cursor-pointer">
                <input
                  type="checkbox"
                  checked={threatAlertsOptIn}
                  onChange={(e) => setThreatAlertsOptIn(e.target.checked)}
                  className="h-4 w-4 accent-[#FF174F]"
                />
                <span>Consented emerging scam campaign advisories</span>
              </label>
            </div>

            <div className="flex justify-end">
              <GlowButton type="submit" variant="primary" size="sm" disabled={saving}>
                <Save className="h-3.5 w-3.5" />
                {saving ? "SAVING..." : "SAVE PROFILE"}
              </GlowButton>
            </div>
          </form>
        </NeonFrame>
      </div>

      {/* Active Sessions & Recent Auth Activity */}
      <NeonFrame className="p-6">
        <div className="flex items-center gap-2 border-b border-[#481326] pb-3">
          <Clock className="h-4 w-4 text-[#FF3D70]" />
          <h2 className="font-mono text-xs font-bold uppercase tracking-widest text-white">
            Active Sessions &amp; Authentication History
          </h2>
        </div>
        {sessions.length === 0 ? (
          <p className="mt-4 text-xs text-[#A1A1AA]">No authentication events recorded yet.</p>
        ) : (
          <div className="mt-4 divide-y divide-[#481326]/50">
            {sessions.map((s) => (
              <div key={s.audit_id} className="flex flex-col sm:flex-row sm:items-center justify-between py-2.5 text-xs gap-1">
                <div className="flex items-center gap-2.5">
                  <span className="rounded bg-[#170A12] border border-[#481326] px-2 py-0.5 font-mono text-[10px] uppercase text-[#FF3D70]">
                    {s.action}
                  </span>
                  <span className="font-mono text-[#A1A1AA]">{s.client_ip || "session"}</span>
                </div>
                <span className="font-mono text-[11px] text-[#A1A1AA]">
                  {new Date(s.timestamp).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        )}
      </NeonFrame>
    </div>
  );
}
