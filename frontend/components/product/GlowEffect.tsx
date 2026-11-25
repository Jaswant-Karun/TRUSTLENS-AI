"use client";

import React from "react";

interface GlowEffectProps {
  children: React.ReactNode;
  className?: string;
  intensity?: "subtle" | "medium" | "strong";
  pulse?: boolean;
}

/**
 * Lightweight CSS-only crimson/neon-red glow wrapper.
 * Respects prefers-reduced-motion via globals.css (.cyber-pulse-ring).
 */
export function GlowEffect({
  children,
  className = "",
  intensity = "subtle",
  pulse = false,
}: GlowEffectProps) {
  const glowMap = {
    subtle: "shadow-[0_0_16px_rgba(255,23,79,0.18)]",
    medium: "shadow-[0_0_26px_rgba(255,23,79,0.32)]",
    strong: "shadow-[0_0_38px_rgba(255,23,79,0.48)]",
  }[intensity];

  return (
    <div className={`relative ${glowMap} ${className}`}>
      {pulse && (
        <span
          aria-hidden="true"
          className="cyber-pulse-ring pointer-events-none absolute -inset-px rounded-[inherit] border border-[#FF174F]/45"
        />
      )}
      {children}
    </div>
  );
}
