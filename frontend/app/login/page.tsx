"use client";

import React, { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Eye, EyeOff, Lock, Mail, ShieldCheck, AlertCircle } from "lucide-react";
import { loginUser } from "@/lib/api";
import { NeonFrame } from "@/components/product/NeonFrame";
import { GlowButton } from "@/components/product/GlowButton";

function LoginFormContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = searchParams.get("next") || "/analyze/text";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email.trim() || !password) {
      setError("Please enter both your email address and password.");
      return;
    }
    setLoading(true);
    try {
      await loginUser(email.trim(), password);
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
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full border border-[#FF174F]/70 bg-[#170A12] shadow-[0_0_20px_rgba(255,23,79,0.3)]">
            <ShieldCheck className="h-6 w-6 text-[#FF3D70]" />
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

        <form onSubmit={handleSubmit} className="space-y-4">
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
                className="w-full rounded-lg border border-[#481326] bg-[#050306] py-2.5 pl-10 pr-3 text-sm text-white placeholder-[#A1A1AA]/50 focus:border-[#FF174F] focus:outline-none"
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
                className="w-full rounded-lg border border-[#481326] bg-[#050306] py-2.5 pl-10 pr-10 text-sm text-white placeholder-[#A1A1AA]/50 focus:border-[#FF174F] focus:outline-none"
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
