"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Lock, Mail, User, ShieldCheck, AlertCircle, CheckCircle2 } from "lucide-react";
import { loginUser, registerUser } from "@/lib/api";
import { NeonFrame } from "@/components/product/NeonFrame";
import { GlowButton } from "@/components/product/GlowButton";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!fullName.trim() || !email.trim() || password.length < 8) {
      setError("Provide your name, a valid email, and a password of at least 8 characters.");
      return;
    }

    setLoading(true);
    try {
      await registerUser({
        full_name: fullName.trim(),
        email: email.trim(),
        password,
      });
      await loginUser(email.trim(), password);
      setSuccess("Account created. Redirecting to Message Scanner...");
      router.push("/analyze/text");
    } catch (err: any) {
      setError(err?.message || "Registration failed. Please check your details.");
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
            Create Account
          </h1>
          <p className="mt-1.5 text-xs text-[#A1A1AA]">
            Register for persistent scan history and private investigations
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

        <form onSubmit={handleSubmit} className="space-y-4">
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
                className="w-full rounded-lg border border-[#481326] bg-[#050306] py-2.5 pl-10 pr-3 text-sm text-white placeholder-[#A1A1AA]/50 focus:border-[#FF174F] focus:outline-none"
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
                className="w-full rounded-lg border border-[#481326] bg-[#050306] py-2.5 pl-10 pr-3 text-sm text-white placeholder-[#A1A1AA]/50 focus:border-[#FF174F] focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="reg-password"
              className="mb-1.5 block font-mono text-[11px] uppercase tracking-wider text-[#A1A1AA]"
            >
              Password (min 8 chars)
            </label>
            <div className="relative">
              <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#A1A1AA]" />
              <input
                id="reg-password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Create a strong password"
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
            {loading ? "CREATING ACCOUNT..." : "CREATE ACCOUNT"}
          </GlowButton>
        </form>

        <p className="mt-6 text-center text-xs text-[#A1A1AA]">
          Already registered?{" "}
          <Link href="/login" className="font-semibold text-[#FF3D70] hover:underline">
            Sign in
          </Link>
        </p>
      </NeonFrame>
    </div>
  );
}
