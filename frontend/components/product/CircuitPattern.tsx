"use client";

import React from "react";

export function CircuitPattern({ className = "" }: { className?: string }) {
  return (
    <svg
      aria-hidden="true"
      className={`pointer-events-none absolute inset-0 h-full w-full ${className}`}
      viewBox="0 0 1440 900"
      preserveAspectRatio="xMidYMid slice"
      fill="none"
    >
      <defs>
        <pattern id="cyber-dot-grid" width="36" height="36" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r="0.8" fill="#481326" fillOpacity="0.45" />
        </pattern>
      </defs>

      <rect width="1440" height="900" fill="url(#cyber-dot-grid)" />

      {/* Static subtle PCB circuit traces */}
      <g stroke="#481326" strokeWidth="1" strokeOpacity="0.65">
        <path d="M0 160 H310 L355 205 H540" />
        <path d="M1440 190 H1090 L1045 235 H860" />
        <path d="M0 440 H210 L260 390 H420" />
        <path d="M1440 500 H1180 L1130 450 H960" />
        <path d="M0 710 H360 L410 760 H660" />
        <path d="M1440 730 H1060 L1010 680 H790" />
        <path d="M290 0 V110 L330 150" />
        <path d="M1140 0 V135 L1095 180" />
      </g>

      {/* Animated neon crimson signal pulses */}
      <g stroke="#FF174F" strokeWidth="1.25" strokeOpacity="0.75">
        <path d="M0 160 H310 L355 205 H540" className="cyber-trace-flow" />
        <path d="M1440 190 H1090 L1045 235 H860" className="cyber-trace-flow" />
        <path d="M0 710 H360 L410 760 H660" className="cyber-trace-flow" />
        <path d="M1440 500 H1180 L1130 450 H960" className="cyber-trace-flow" />
      </g>

      {/* Circuit connection nodes */}
      <g fill="#FF174F" fillOpacity="0.75">
        <circle cx="540" cy="205" r="2.5" />
        <circle cx="860" cy="235" r="2.5" />
        <circle cx="420" cy="390" r="2.5" />
        <circle cx="960" cy="450" r="2.5" />
        <circle cx="660" cy="760" r="2.5" />
        <circle cx="790" cy="680" r="2.5" />
        <circle cx="330" cy="150" r="2" />
        <circle cx="1095" cy="180" r="2" />
      </g>
    </svg>
  );
}
