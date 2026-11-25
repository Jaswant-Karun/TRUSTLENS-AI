"use client";

import React, { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { AlertCircle, CheckCircle2, MailCheck } from "lucide-react";
import { verifyEmailToken } from "@/lib/api";
import { NeonFrame } from "@/components/product/NeonFrame";
import { GlowButton } from "@/components/product/GlowButton";

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const initialToken = searchParams.get("token") || "";

  const [token, setToken] = useState(initialToken);
  const [loading, setLoading] = useState(false);
  const [verified, setVerified] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runVerification = async (tok: string) => {
    if (!tok.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await verifyEmailToken(tok.trim());
      setVerified(true);
    } catch (err: any) {
      setError(err?.message || "Invalid or expired verification token.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialToken) {
      runVerification(initialToken);
    }
  }, [initialToken]);

  return (
    <div className="mx-auto flex w-full max-w-md flex-1 items-center justify-center px-4 py-12">
      <NeonFrame className="w-full p-6 sm:p-8 text-center">
        <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full border border-[#FF174F]/70 bg-[#170A12]">
          <MailCheck className="h-6 w-6 text-[#FF3D70]" />
        </div>
        <h1 className="font-mono text-lg font-bold uppercase tracking-widest text-white">
          Email Verification
        </h1>

        {verified ? (
          <div className="mt-4 space-y-4">
            <div className="flex items-center justify-center gap-2 rounded-lg border border-[#00D68F]/50 bg-[#00D68F]/10 p-3 text-xs text-[#00D68F]">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              <span>Email verified successfully. Your onboarding is complete.</span>
            </div>
            <Link href="/analyze/text" className="block">
              <GlowButton variant="primary" className="w-full">
                OPEN MESSAGE SCANNER
              </GlowButton>
            </Link>
          </div>
        ) : (
          <div className="mt-3 space-y-4 text-left">
            <p className="text-xs leading-relaxed text-[#A1A1AA] text-center">
              Enter your verification token to confirm email ownership.
            </p>
            {error && (
              <div className="flex items-start gap-2 rounded-lg border border-[#FF174F]/60 bg-[#FF174F]/10 p-3 text-xs text-[#FF3D70]">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}
            <input
              type="text"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Paste verification token"
              className="cyber-input"
            />
            <GlowButton
              variant="primary"
              className="w-full"
              disabled={loading || !token.trim()}
              onClick={() => runVerification(token)}
            >
              {loading ? "VERIFYING..." : "VERIFY EMAIL"}
            </GlowButton>
            <div className="text-center text-xs text-[#A1A1AA]">
              <Link href="/analyze/text" className="hover:text-white underline">
                Continue to workspace
              </Link>
            </div>
          </div>
        )}
      </NeonFrame>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center font-mono text-xs text-[#A1A1AA]">Loading verification...</div>}>
      <VerifyEmailContent />
    </Suspense>
  );
}
