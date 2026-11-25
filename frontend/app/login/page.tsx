"use client";

import React, { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Eye, EyeOff, Lock, Mail, AlertCircle } from "lucide-react";
import {
  clearStoredToken,
  getCurrentUser,
  getStoredToken,
  loginUser,
} from "@/lib/api";
import { NeonFrame } from "@/components/product/NeonFrame";
import { GlowButton } from "@/components/product/GlowButton";
import { TrustLensMark } from "@/components/product/BrandLogo";

function sanitizeNextPath(rawNext: string | null): string {
  if (!rawNext || !rawNext.startsWith("/") || rawNext.startsWith("//")) {
    return "/analyze/text";
  }
  return rawNext;
}

function LoginFormContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = sanitizeNextPath(searchParams.get("next"));
  const reason = searchParams.get("reason");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(
    reason === "session_expired"
      ? "Your session has expired. Please sign in again."
      : null
  );

  // Verify existing token on mount; clear expired/invalid tokens instead of trusting blindly
  useEffect(() => {
    const token = getStoredToken();
    if (!token) return;
    getCurrentUser()
      .then(() => {
        router.replace(nextPath);
      })
      .catch(() => {
        clearStoredToken();
        setError("Your previous session expired or is invalid. Please sign in again.");
      });
  }, [router, nextPath]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const normalizedEmail = email.trim();
    if (!normalizedEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) {
      setError("Please enter a valid email address.");
      return;
    }
    if (!password) {
      setError("Please enter your password.");
      return;
    }

    setLoading(true);
    try {
      await loginUser(normalizedEmail, password);
      router.push(nextPath);
    } catch (err: any) {
      setError(err?.message || "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex w-full max-w-md flex-1 items-center justify-center px-4 py-12">
      <NeonFrame className="w-full p-6 sm:p-8">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center">
            <TrustLensMark className="h-11 w-11 drop-shadow-[0_0_14px_rgba(255,23,79,0.4)]" />
          </div>
          <h1 className="font-mono text-xl font-bold uppercase tracking-widest text-white">
            Sign In
          </h1>
          <p className="mt-1.5 text-xs text-[#A1A1AA]">
            Access your TRUSTLENS AI intelligence workspace
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

        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <div>
            <label
              htmlFor="login-email"
              className="mb-1.5 block font-mono text-[11px] uppercase tracking-wider text-[#A1A1AA]"
            >
              Email Address
            </label>
            <div className="relative">
              <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#A1A1AA]" />
              <input
                id="login-email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="analyst@organization.com"
                className="cyber-input pl-10"
              />
            </div>
          </div>

          <div>
            <div className="mb-1.5 flex items-center justify-between">
              <label
                htmlFor="login-password"
                className="block font-mono text-[11px] uppercase tracking-wider text-[#A1A1AA]"
              >
                Password
              </label>
              <Link
                href="/forgot-password"
                className="font-mono text-[11px] text-[#FF3D70] hover:underline"
              >
                Forgot password?
              </Link>
            </div>
            <div className="relative">
              <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#A1A1AA]" />
              <input
                id="login-password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
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

          <GlowButton type="submit" variant="primary" className="w-full" disabled={loading}>
            {loading ? "AUTHENTICATING..." : "SIGN IN TO TRUSTLENS"}
          </GlowButton>
        </form>

        <p className="mt-6 text-center text-xs text-[#A1A1AA]">
          New to TRUSTLENS AI?{" "}
          <Link href="/register" className="font-semibold text-[#FF3D70] hover:underline">
            Create an account
          </Link>
        </p>
      </NeonFrame>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center font-mono text-xs text-[#A1A1AA]">Loading authentication...</div>}>
      <LoginFormContent />
    </Suspense>
  );
}
