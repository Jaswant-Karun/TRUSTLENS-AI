"use client";

import React from "react";

interface GlowButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
}

export function GlowButton({
  variant = "primary",
  size = "md",
  className = "",
  children,
  ...props
}: GlowButtonProps) {
  const sizes = {
    sm: "px-3.5 py-2 text-xs",
    md: "px-5 py-2.5 text-sm",
    lg: "px-6 py-3 text-sm",
  }[size];

  const variants = {
    primary:
      "bg-gradient-to-r from-[#FF174F] to-[#C2185B] text-white border border-[#FF3D70]/60 shadow-[0_0_20px_rgba(255,23,79,0.32)] hover:shadow-[0_0_28px_rgba(255,23,79,0.55)] hover:brightness-110",
    secondary:
      "bg-[#170A12]/90 text-white border border-[#481326] hover:border-[#FF174F] hover:bg-[#10070D] hover:shadow-[0_0_16px_rgba(255,23,79,0.2)]",
    ghost:
      "bg-transparent text-[#A1A1AA] border border-transparent hover:text-white hover:border-[#481326] hover:bg-[#10070D]/60",
  }[variant];

  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-lg font-mono font-semibold uppercase tracking-wider transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed min-h-[40px] ${sizes} ${variants} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
