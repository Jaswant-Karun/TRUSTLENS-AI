"use client";

import React from "react";

interface BrandLogoProps {
  size?: "sm" | "md" | "lg";
  showWordmark?: boolean;
  subtitle?: string;
  className?: string;
}

export function TrustLensMark({
  className = "h-8 w-8",
}: {
  className?: string;
}) {
  return (
    <svg
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="tl-shield-grad" x1="4" y1="4" x2="36" y2="36" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#FF174F" />
          <stop offset="100%" stopColor="#C2185B" />
        </linearGradient>
      </defs>
      {/* Outer hexagonal cyber shield */}
      <path
        d="M20 3L34 9.5V20.5C34 28.4 27.9 34.4 20 37C12.1 34.4 6 28.4 6 20.5V9.5L20 3Z"
        fill="#10070D"
        stroke="url(#tl-shield-grad)"
        strokeWidth="2"
      />
      {/* Optical intelligence lens ring */}
      <circle
        cx="20"
        cy="19.5"
        r="7.25"
        stroke="#FF3D70"
        strokeWidth="1.6"
        strokeDasharray="18 4"
      />
      {/* Precision reticle crosshairs */}
      <path
        d="M20 9.5V13.5M20 25.5V29.5M10 19.5H14M26 19.5H30"
        stroke="#FF174F"
        strokeWidth="1.4"
        strokeLinecap="round"
      />
      {/* Central AI pupil core */}
      <circle cx="20" cy="19.5" r="2.6" fill="#FFFFFF" />
      <circle cx="20" cy="19.5" r="1.2" fill="#FF174F" />
    </svg>
  );
}

export function BrandLogo({
  size = "md",
  showWordmark = true,
  subtitle,
  className = "",
}: BrandLogoProps) {
  const markSizes = {
    sm: "h-8 w-8",
    md: "h-10 w-10",
    lg: "h-12 w-12",
  }[size];

  const textSizes = {
    sm: "text-sm sm:text-base tracking-[0.24em]",
    md: "text-base sm:text-lg tracking-[0.26em]",
    lg: "text-xl sm:text-2xl tracking-[0.28em]",
  }[size];

  return (
    <span className={`inline-flex items-center gap-2.5 select-none ${className}`}>
      <TrustLensMark
        className={`${markSizes} drop-shadow-[0_0_12px_rgba(255,23,79,0.4)]`}
      />
      {showWordmark && (
        <span className="flex flex-col">
          <span className={`font-mono font-bold uppercase text-white ${textSizes}`}>
            TRUST<span className="text-[#FF174F]">LENS</span> AI
          </span>
          {subtitle && (
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#A1A1AA]">
              {subtitle}
            </span>
          )}
        </span>
      )}
    </span>
  );
}
