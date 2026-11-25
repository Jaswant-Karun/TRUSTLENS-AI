"use client";

import React from "react";
import { TrustLensMark } from "./BrandLogo";

export function BrandLoader({
  label = "INITIALIZING THREAT INTELLIGENCE...",
}: {
  label?: string;
}) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex min-h-[55vh] w-full flex-col items-center justify-center gap-4 px-4"
    >
      <div className="relative flex items-center justify-center">
        <span
          aria-hidden="true"
          className="cyber-pulse-ring absolute h-20 w-20 rounded-full border border-[#FF174F]/50 shadow-[0_0_24px_rgba(255,23,79,0.28)]"
        />
        <TrustLensMark className="relative z-10 h-12 w-12" />
      </div>
      <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#A1A1AA]">
        {label}
      </p>
    </div>
  );
}
