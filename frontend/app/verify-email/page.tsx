"use client";

import React from "react";
import Link from "next/link";
import { MailCheck } from "lucide-react";
import { NeonFrame } from "@/components/product/NeonFrame";
import { GlowButton } from "@/components/product/GlowButton";

export default function VerifyEmailPage() {
  return (
    <div className="mx-auto flex w-full max-w-md flex-1 items-center justify-center px-4 py-12">
      <NeonFrame className="w-full p-6 sm:p-8 text-center">
        <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full border border-[#FF174F]/70 bg-[#170A12]">
          <MailCheck className="h-6 w-6 text-[#FF3D70]" />
        </div>
        <h1 className="font-mono text-lg font-bold uppercase tracking-widest text-white">
          Email Verification
        </h1>
        <p className="mt-2 text-xs leading-relaxed text-[#A1A1AA]">
          Email verification tokens will be activated alongside SMTP delivery in
          Phase 3.12. Registered accounts can currently sign in directly via{" "}
          <span className="text-white">/login</span>.
        </p>
        <div className="mt-6">
          <Link href="/login">
            <GlowButton variant="primary" className="w-full">
              GO TO SIGN IN
            </GlowButton>
          </Link>
        </div>
      </NeonFrame>
    </div>
  );
}
