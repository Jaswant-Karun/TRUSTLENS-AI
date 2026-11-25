"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Mail, AlertCircle } from "lucide-react";
import { NeonFrame } from "@/components/product/NeonFrame";
import { GlowButton } from "@/components/product/GlowButton";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [notice, setNotice] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      setNotice("Please enter your registered email address.");
      return;
    }
    setNotice(
      "Password recovery email delivery requires backend SMTP/token configuration (scheduled in Phase 3.13). Please contact your platform administrator to reset credentials."
    );
  };

  return (
    <div className="mx-auto flex w-full max-w-md flex-1 items-center justify-center px-4 py-12">
      <NeonFrame className="w-full p-6 sm:p-8">
        <h1 className="font-mono text-lg font-bold uppercase tracking-widest text-white">
          Password Recovery
        </h1>
        <p className="mt-1.5 text-xs text-[#A1A1AA]">
          Enter your account email to check recovery availability.
        </p>

        {notice && (
          <div className="mt-4 flex items-start gap-2.5 rounded-lg border border-[#FFB020]/50 bg-[#FFB020]/10 p-3 text-xs text-[#FFB020]">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{notice}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <div className="relative">
            <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#A1A1AA]" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full rounded-lg border border-[#481326] bg-[#050306] py-2.5 pl-10 pr-3 text-sm text-white placeholder-[#A1A1AA]/50 focus:border-[#FF174F] focus:outline-none"
            />
          </div>
          <GlowButton type="submit" variant="primary" className="w-full">
            REQUEST RECOVERY
          </GlowButton>
        </form>

        <div className="mt-5 flex justify-between text-xs text-[#A1A1AA]">
          <Link href="/login" className="text-[#FF3D70] hover:underline">
            Back to Sign In
          </Link>
          <Link href="/reset-password" className="hover:text-white">
            Have a reset token?
          </Link>
        </div>
      </NeonFrame>
    </div>
  );
}
