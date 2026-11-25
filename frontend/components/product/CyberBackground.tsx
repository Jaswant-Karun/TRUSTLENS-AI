"use client";

import React from "react";
import { CircuitPattern } from "./CircuitPattern";

interface CyberBackgroundProps {
  children: React.ReactNode;
  showHudFrame?: boolean;
}

export function CyberBackground({ children, showHudFrame = true }: CyberBackgroundProps) {
  return (
    <div className="relative min-h-screen w-full overflow-x-hidden bg-[#050306] text-white selection:bg-[#FF174F]/30 selection:text-white">
      {/* Subtle dark-crimson ambient gradients */}
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 z-0"
        style={{
          background:
            "radial-gradient(circle at 50% 35%, rgba(194, 24, 91, 0.14) 0%, rgba(16, 7, 13, 0.45) 42%, rgba(5, 3, 6, 1) 78%)",
        }}
      />

      {/* Electronic circuit board pattern */}
      <div className="pointer-events-none fixed inset-0 z-0 opacity-90">
        <CircuitPattern />
      </div>

      {/* Subtle outer HUD geometric frame (inspired by reference) */}
      {showHudFrame && (
        <div
          aria-hidden="true"
          className="pointer-events-none fixed inset-3 sm:inset-5 z-0 hidden md:block border border-[#481326]/40"
        >
          <span className="absolute -top-1 left-8 h-1 w-8 bg-[#FFB020]/70 skew-x-[-35deg]" />
          <span className="absolute -top-1 right-8 h-1 w-8 bg-[#FFB020]/70 skew-x-[35deg]" />
          <span className="absolute -bottom-1 left-8 h-1 w-8 bg-[#FFB020]/70 skew-x-[35deg]" />
          <span className="absolute -bottom-1 right-8 h-1 w-8 bg-[#FFB020]/70 skew-x-[-35deg]" />
        </div>
      )}

      <div className="relative z-10 flex min-h-screen flex-col">{children}</div>
    </div>
  );
}
