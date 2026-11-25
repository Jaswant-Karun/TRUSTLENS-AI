"use client";

import React from "react";

interface NeonFrameProps {
  children: React.ReactNode;
  className?: string;
  variant?: "primary" | "secondary";
}

export function NeonFrame({
  children,
  className = "",
  variant = "primary",
}: NeonFrameProps) {
  const bg = variant === "primary" ? "bg-[#10070D]/85" : "bg-[#170A12]/85";
  return (
    <div
      className={`relative rounded-xl border border-[#481326] ${bg} backdrop-blur-md shadow-[0_8px_32px_rgba(0,0,0,0.65)] transition-colors duration-200 hover:border-[#FF174F]/60 ${className}`}
    >
      {/* Subtle geometric corner ticks */}
      <span
        aria-hidden="true"
        className="pointer-events-none absolute -top-px -left-px h-2.5 w-2.5 border-t-2 border-l-2 border-[#FF174F]/80 rounded-tl-sm"
      />
      <span
        aria-hidden="true"
        className="pointer-events-none absolute -bottom-px -right-px h-2.5 w-2.5 border-b-2 border-r-2 border-[#FF174F]/80 rounded-br-sm"
      />
      {children}
    </div>
  );
}
