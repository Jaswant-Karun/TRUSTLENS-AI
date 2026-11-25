"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Lock, KeyRound, AlertCircle } from "lucide-react";
import { NeonFrame } from "@/components/product/NeonFrame";
import { GlowButton } from "@/components/product/GlowButton";

export default function ResetPasswordPage() {
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [notice, setNotice] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!token.trim() || password.length < 8) {
      setNotice("Enter a valid reset token and a new password of at least 8 characters.");
      return;
    }
    setNotice(
      "Server-side password reset token verification is pending Phase 3.13 backend deployment. No password was modified."
    );
  };

  return (
    <div className="mx-auto flex w-full max-w-md flex-1 items-center justify-center px-4 py-12">
      <NeonFrame className="w-full p-6 sm:p-8">
        <h1 className="font-mono text-lg font-bold uppercase tracking-widest text-white">
          Reset Password
        </h1>
        <p className="mt-1.5 text-xs text-[#A1A1AA]">
          Set a new password using a signed recovery token.
        </p>

        {notice && (
          <div className="mt-4 flex items-start gap-2.5 rounded-lg border border-[#FFB020]/50 bg-[#FFB020]/10 p-3 text-xs text-[#FFB020]">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{notice}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <div className="relative">
            <KeyRound className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#A1A1AA]" />
            <input
              type="text"
              required
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Recovery token"
              className="w-full rounded-lg border border-[#481326] bg-[#050306] py-2.5 pl-10 pr-3 text-sm text-white placeholder-[#A1A1AA]/50 focus:border-[#FF174F] focus:outline-none"
            />
          </div>
          <div className="relative">
            <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#A1A1AA]" />
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="New password (min 8 chars)"
              className="w-full rounded-lg border border-[#481326] bg-[#050306] py-2.5 pl-10 pr-3 text-sm text-white placeholder-[#A1A1AA]/50 focus:border-[#FF174F] focus:outline-none"
            />
          </div>
          <GlowButton type="submit" variant="primary" className="w-full">
            UPDATE PASSWORD
          </GlowButton>
        </form>

        <p className="mt-5 text-center text-xs text-[#A1A1AA]">
          <Link href="/login" className="text-[#FF3D70] hover:underline">
            Return to Sign In
          </Link>
        </p>
      </NeonFrame>
    </div>
  );
}
