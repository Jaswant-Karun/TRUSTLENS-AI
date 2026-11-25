"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  AlertCircle,
  CheckCircle2,
  Eye,
  EyeOff,
  Lock,
  Mail,
  User,
} from "lucide-react";
import { loginUser, registerUser } from "@/lib/api";
import { NeonFrame } from "@/components/product/NeonFrame";
import { GlowButton } from "@/components/product/GlowButton";
import { TrustLensMark } from "@/components/product/BrandLogo";

function evaluatePasswordStrength(pw: string) {
  let score = 0;
  if (pw.length >= 8) score += 1;
  if (/[A-Za-z]/.test(pw) && /\d/.test(pw)) score += 1;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score += 1;
  if (/[^A-Za-z0-9]/.test(pw) || pw.length >= 12) score += 1;

  if (score <= 1) return { score, label: "Weak", color: "bg-[#FF174F]", textColor: "text-[#FF174F]" };
  if (score <= 2) return { score, label: "Fair", color: "bg-[#FFB020]", textColor: "text-[#FFB020]" };
  return { score, label: "Strong", color: "bg-[#00D68F]", textColor: "text-[#00D68F]" };
}

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [preferredLanguage, setPreferredLanguage] = useState("en");
  const [primaryFocus, setPrimaryFocus] = useState("message_scanning");
  const [threatAlertsOptIn, setThreatAlertsOptIn] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const strength = useMemo(() => evaluatePasswordStrength(password), [password]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (fullName.trim().length < 2) {
      setError("Full name must be at least 2 characters.");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      setError("Please enter a valid email address.");
      return;
    }
    if (password.length < 8 || !/[A-Za-z]/.test(password) || !/\d/.test(password)) {
      setError("Password must be at least 8 characters and include both letters and numbers.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    if (!privacyAccepted || !termsAccepted) {
      setError("You must accept both the Privacy Policy and Terms of Service to register.");
      return;
    }

    setLoading(true);
    try {
      const regRes = await registerUser({
        full_name: fullName.trim(),
        email: email.trim(),
        password,
        privacy_accepted: privacyAccepted,
        terms_accepted: termsAccepted,
        onboarding_preferences: {
          preferred_language: preferredLanguage,
          primary_focus: primaryFocus,
          threat_alerts_opt_in: threatAlertsOptIn,
        },
      });
      await loginUser(email.trim(), password);
      setSuccess("Account created successfully. Preparing verification...");
      if (regRes.verification_token) {
        router.push(`/verify-email?token=${encodeURIComponent(regRes.verification_token)}`);
      } else {
        router.push("/verify-email");
      }
    } catch (err: any) {
      setError(err?.message || "Registration failed. Please check your details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex w-full max-w-lg flex-1 items-center justify-center px-4 py-10">
      <NeonFrame className="w-full p-6 sm:p-8">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center">
            <TrustLensMark className="h-11 w-11 drop-shadow-[0_0_14px_rgba(255,23,79,0.4)]" />
          </div>
          <h1 className="font-mono text-xl font-bold uppercase tracking-widest text-white">
            Create Account
          </h1>
          <p className="mt-1.5 text-xs text-[#A1A1AA]">
            Register and configure your fraud-intelligence preferences
          </p>
        </div>

        {error && (
          <div
            role="alert"
            className="mb-4 flex items-start gap-2.5 rounded-lg border border-[#FF174F]/60 bg-[#FF174F]/10 p-3 text-xs text-[#FF3D70]"
          >
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div
            role="status"
            className="mb-4 flex items-start gap-2.5 rounded-lg border border-[#00D68F]/60 bg-[#00D68F]/10 p-3 text-xs text-[#00D68F]"
          >
            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label
                htmlFor="reg-name"
                className="mb-1.5 block font-mono text-[11px] uppercase tracking-wider text-[#A1A1AA]"
              >
                Full Name
              </label>
              <div className="relative">
                <User className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#A1A1AA]" />
                <input
                  id="reg-name"
                  type="text"
                  autoComplete="name"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your Name"
                  className="cyber-input pl-10"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="reg-email"
                className="mb-1.5 block font-mono text-[11px] uppercase tracking-wider text-[#A1A1AA]"
              >
                Email Address
              </label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#A1A1AA]" />
                <input
                  id="reg-email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="cyber-input pl-10"
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label
                htmlFor="reg-password"
                className="mb-1.5 block font-mono text-[11px] uppercase tracking-wider text-[#A1A1AA]"
              >
                Password
              </label>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#A1A1AA]" />
                <input
                  id="reg-password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="new-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min 8 chars + digit"
                  className="cyber-input pl-10 pr-10"
                />
                <button
                  type="button"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#A1A1AA] hover:text-white"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <div>
              <label
                htmlFor="reg-confirm-password"
                className="mb-1.5 block font-mono text-[11px] uppercase tracking-wider text-[#A1A1AA]"
              >
                Confirm Password
              </label>
              <input
                id="reg-confirm-password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter password"
                className="cyber-input"
              />
            </div>
          </div>

          {/* Password Strength Meter */}
          {password && (
            <div className="space-y-1">
              <div className="flex items-center justify-between font-mono text-[10px] uppercase">
                <span className="text-[#A1A1AA]">Password Strength</span>
                <span className={strength.textColor}>{strength.label}</span>
              </div>
              <div className="grid grid-cols-4 gap-1.5">
                {[1, 2, 3, 4].map((step) => (
                  <div
                    key={step}
                    className={`h-1.5 rounded-full transition-colors ${
                      strength.score >= step ? strength.color : "bg-[#481326]/60"
                    }`}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Onboarding Preferences */}
          <div className="rounded-lg border border-[#481326] bg-[#050306]/70 p-3.5 space-y-3">
            <div className="font-mono text-[10px] font-bold uppercase tracking-wider text-[#FF3D70]">
              Onboarding Preferences
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="reg-lang"
                  className="mb-1 block font-mono text-[10px] uppercase text-[#A1A1AA]"
                >
                  Primary Language
                </label>
                <select
                  id="reg-lang"
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
                <label
                  htmlFor="reg-focus"
                  className="mb-1 block font-mono text-[10px] uppercase text-[#A1A1AA]"
                >
                  Starting Workflow
                </label>
                <select
                  id="reg-focus"
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
            <label className="flex items-center gap-2 text-xs text-[#A1A1AA] cursor-pointer">
              <input
                type="checkbox"
                checked={threatAlertsOptIn}
                onChange={(e) => setThreatAlertsOptIn(e.target.checked)}
                className="h-4 w-4 accent-[#FF174F]"
              />
              <span>Opt in to consented security &amp; campaign advisories</span>
            </label>
          </div>

          {/* Privacy Consent & Terms */}
          <div className="space-y-2 text-xs text-[#A1A1AA]">
            <label className="flex items-start gap-2 cursor-pointer">
              <input
                id="reg-privacy"
                type="checkbox"
                checked={privacyAccepted}
                onChange={(e) => setPrivacyAccepted(e.target.checked)}
                className="mt-0.5 h-4 w-4 accent-[#FF174F]"
              />
              <span>
                I consent to the{" "}
                <span className="text-white font-medium">TRUSTLENS AI Privacy Policy</span>{" "}
                (zero-hop URL safety, private case isolation).
              </span>
            </label>
            <label className="flex items-start gap-2 cursor-pointer">
              <input
                id="reg-terms"
                type="checkbox"
                checked={termsAccepted}
                onChange={(e) => setTermsAccepted(e.target.checked)}
                className="mt-0.5 h-4 w-4 accent-[#FF174F]"
              />
              <span>
                I accept the{" "}
                <span className="text-white font-medium">Terms of Service</span>.
              </span>
            </label>
          </div>

          <GlowButton type="submit" variant="primary" className="w-full" disabled={loading}>
            {loading ? "CREATING ACCOUNT..." : "CREATE ACCOUNT & CONTINUE"}
          </GlowButton>
        </form>

        <p className="mt-5 text-center text-xs text-[#A1A1AA]">
          Already registered?{" "}
          <Link href="/login" className="font-semibold text-[#FF3D70] hover:underline">
            Sign in
          </Link>
        </p>
      </NeonFrame>
    </div>
  );
}
