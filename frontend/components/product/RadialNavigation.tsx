"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import { usePathname, useRouter } from "next/navigation";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import {
  Home,
  MessageSquareWarning,
  Link2,
  ScanSearch,
  ShieldAlert,
  FolderSearch,
  FileText,
  User,
  Compass,
  X,
} from "lucide-react";

export interface RadialNavItem {
  id: string;
  label: string;
  shortLabel: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

export const RADIAL_NAV_ITEMS: RadialNavItem[] = [
  { id: "home", label: "Home", shortLabel: "HOME", href: "/", icon: Home },
  { id: "message", label: "Message Scanner", shortLabel: "MESSAGES", href: "/analyze/text", icon: MessageSquareWarning },
  { id: "url", label: "URL Shield", shortLabel: "URL SHIELD", href: "/analyze/url", icon: Link2 },
  { id: "screenshot", label: "Screenshot Analyzer", shortLabel: "OCR SCAN", href: "/analyze/image", icon: ScanSearch },
  { id: "intel", label: "Threat Intelligence", shortLabel: "THREATS", href: "/intelligence/campaigns", icon: ShieldAlert },
  { id: "investigations", label: "Investigations", shortLabel: "CASES", href: "/investigations", icon: FolderSearch },
  { id: "reports", label: "Reports", shortLabel: "REPORTS", href: "/reports", icon: FileText },
  { id: "profile", label: "Profile", shortLabel: "PROFILE", href: "/profile", icon: User },
];

interface RadialNavigationProps {
  variant?: "hero" | "launcher";
}

function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return {
    x: cx + r * Math.cos(rad),
    y: cy + r * Math.sin(rad),
  };
}

function describeAnnularSector(
  cx: number,
  cy: number,
  innerR: number,
  outerR: number,
  startAngle: number,
  endAngle: number
) {
  const p1 = polarToCartesian(cx, cy, outerR, startAngle);
  const p2 = polarToCartesian(cx, cy, outerR, endAngle);
  const p3 = polarToCartesian(cx, cy, innerR, endAngle);
  const p4 = polarToCartesian(cx, cy, innerR, startAngle);
  const largeArc = endAngle - startAngle <= 180 ? "0" : "1";

  return [
    `M ${p1.x.toFixed(2)} ${p1.y.toFixed(2)}`,
    `A ${outerR} ${outerR} 0 ${largeArc} 1 ${p2.x.toFixed(2)} ${p2.y.toFixed(2)}`,
    `L ${p3.x.toFixed(2)} ${p3.y.toFixed(2)}`,
    `A ${innerR} ${innerR} 0 ${largeArc} 0 ${p4.x.toFixed(2)} ${p4.y.toFixed(2)}`,
    "Z",
  ].join(" ");
}

export function RadialNavigation({ variant = "hero" }: RadialNavigationProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);
  const [focusedIdx, setFocusedIdx] = useState<number>(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const centerBtnRef = useRef<HTMLButtonElement>(null);
  const itemBtnRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const shouldReduceMotion = useReducedMotion();
  const router = useRouter();
  const pathname = usePathname();

  const closeMenu = useCallback(() => {
    setIsOpen(false);
    setHoveredIdx(null);
  }, []);

  // Close on outside click
  useEffect(() => {
    if (!isOpen) return;
    const handleOutside = (e: MouseEvent | TouchEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        closeMenu();
      }
    };
    document.addEventListener("mousedown", handleOutside);
    document.addEventListener("touchstart", handleOutside);
    return () => {
      document.removeEventListener("mousedown", handleOutside);
      document.removeEventListener("touchstart", handleOutside);
    };
  }, [isOpen, closeMenu]);

  // Move focus to first radial item when opened for seamless keyboard navigation
  useEffect(() => {
    if (isOpen) {
      setFocusedIdx(0);
      const timer = setTimeout(() => {
        itemBtnRefs.current[0]?.focus();
      }, 40);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  // Keyboard navigation (Escape, ArrowLeft/Right/Up/Down, Home/End)
  useEffect(() => {
    if (!isOpen) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        closeMenu();
        centerBtnRef.current?.focus();
      } else if (e.key === "ArrowRight" || e.key === "ArrowDown") {
        e.preventDefault();
        const next = (focusedIdx + 1) % RADIAL_NAV_ITEMS.length;
        setFocusedIdx(next);
        itemBtnRefs.current[next]?.focus();
      } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
        e.preventDefault();
        const prev = (focusedIdx - 1 + RADIAL_NAV_ITEMS.length) % RADIAL_NAV_ITEMS.length;
        setFocusedIdx(prev);
        itemBtnRefs.current[prev]?.focus();
      } else if (e.key === "Home") {
        e.preventDefault();
        setFocusedIdx(0);
        itemBtnRefs.current[0]?.focus();
      } else if (e.key === "End") {
        e.preventDefault();
        const last = RADIAL_NAV_ITEMS.length - 1;
        setFocusedIdx(last);
        itemBtnRefs.current[last]?.focus();
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [isOpen, focusedIdx, closeMenu]);

  const handleNavigate = (href: string) => {
    closeMenu();
    router.push(href);
  };

  const count = RADIAL_NAV_ITEMS.length;
  const sliceDeg = 360 / count; // 45 deg per slice

  const renderWheel = () => (
    <motion.div
      initial={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, scale: 0.72 }}
      animate={shouldReduceMotion ? { opacity: 1 } : { opacity: 1, scale: 1 }}
      exit={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, scale: 0.78 }}
      transition={shouldReduceMotion ? { duration: 0.1 } : { type: "spring", stiffness: 280, damping: 24 }}
      className="relative flex items-center justify-center w-[304px] h-[304px] sm:w-[390px] sm:h-[390px] select-none"
      role="menu"
      aria-label="TRUSTLENS AI Primary Navigation"
    >
      {/* Segmented Radial SVG Ring */}
      <svg
        viewBox="-200 -200 400 400"
        className="absolute inset-0 h-full w-full drop-shadow-[0_0_32px_rgba(255,23,79,0.28)]"
        aria-hidden="true"
      >
        <defs>
          <radialGradient id="activeSectorGrad" cx="50%" cy="50%" r="75%">
            <stop offset="0%" stopColor="#C2185B" stopOpacity="0.95" />
            <stop offset="100%" stopColor="#FF174F" stopOpacity="0.92" />
          </radialGradient>
        </defs>

        {/* Outer glowing ring */}
        <circle cx="0" cy="0" r="190" fill="none" stroke="#481326" strokeWidth="1.5" />

        {RADIAL_NAV_ITEMS.map((item, i) => {
          const startAngle = i * sliceDeg - sliceDeg / 2;
          const endAngle = startAngle + sliceDeg;
          const isActiveRoute =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          const isHighlighted = hoveredIdx === i || isActiveRoute;

          return (
            <path
              key={item.id}
              d={describeAnnularSector(0, 0, 58, 188, startAngle, endAngle)}
              fill={isHighlighted ? "url(#activeSectorGrad)" : "#130911"}
              fillOpacity={isHighlighted ? 0.96 : 0.94}
              stroke="#481326"
              strokeWidth="1.5"
              className="transition-colors duration-150"
            />
          );
        })}

        {/* Inner dark ring border */}
        <circle cx="0" cy="0" r="58" fill="#050306" stroke="#FF174F" strokeOpacity="0.5" strokeWidth="1.5" />
      </svg>

      {/* Interactive Sector Buttons */}
      {RADIAL_NAV_ITEMS.map((item, i) => {
        const Icon = item.icon;
        const angleDeg = i * sliceDeg;
        const radiusPct = 32; // % from center inside the ring
        const rad = ((angleDeg - 90) * Math.PI) / 180;
        const leftPct = 50 + radiusPct * Math.cos(rad);
        const topPct = 50 + radiusPct * Math.sin(rad);

        return (
          <button
            key={item.id}
            ref={(el) => {
              itemBtnRefs.current[i] = el;
            }}
            type="button"
            role="menuitem"
            aria-label={item.label}
            title={item.label}
            onMouseEnter={() => setHoveredIdx(i)}
            onMouseLeave={() => setHoveredIdx(null)}
            onFocus={() => {
              setHoveredIdx(i);
              setFocusedIdx(i);
            }}
            onClick={() => handleNavigate(item.href)}
            style={{
              left: `${leftPct}%`,
              top: `${topPct}%`,
              transform: "translate(-50%, -50%)",
            }}
            className="absolute z-10 flex flex-col items-center justify-center w-16 h-16 sm:w-20 sm:h-20 rounded-full text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF3D70] transition-transform duration-150 hover:scale-105"
          >
            <span className="flex items-center justify-center w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-[#050306]/45 border border-white/15 mb-1">
              <Icon className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" />
            </span>
            <span className="font-mono text-[8px] sm:text-[9.5px] font-semibold tracking-wider uppercase text-center leading-tight px-0.5 text-white/95">
              {item.shortLabel}
            </span>
          </button>
        );
      })}

      {/* Center Collapse Button */}
      <button
        type="button"
        aria-label="Close radial navigation"
        onClick={() => {
          closeMenu();
          centerBtnRef.current?.focus();
        }}
        className="relative z-20 flex items-center justify-center w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-[#10070D] border border-[#FF174F]/70 text-[#FF3D70] shadow-[0_0_24px_rgba(255,23,79,0.35)] hover:bg-[#170A12] hover:text-white transition-all duration-150"
      >
        <X className="w-6 h-6" />
      </button>
    </motion.div>
  );

  if (variant === "launcher") {
    return (
      <div ref={containerRef} className="relative">
        <button
          ref={centerBtnRef}
          type="button"
          aria-expanded={isOpen}
          aria-label="Open primary radial navigation"
          onClick={() => setIsOpen((prev) => !prev)}
          className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-[#FF174F] to-[#C2185B] text-white shadow-[0_0_18px_rgba(255,23,79,0.45)] border border-[#FF3D70]/60 hover:scale-105 transition-transform duration-150"
        >
          <Compass className="w-5 h-5" />
        </button>

        <AnimatePresence>
          {isOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#050306]/80 backdrop-blur-sm p-4">
              <div ref={containerRef}>{renderWheel()}</div>
            </div>
          )}
        </AnimatePresence>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="relative flex items-center justify-center min-h-[320px] sm:min-h-[400px]"
    >
      <AnimatePresence mode="wait">
        {!isOpen ? (
          <motion.div
            key="collapsed-hub"
            initial={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, scale: 0.9 }}
            animate={shouldReduceMotion ? { opacity: 1 } : { opacity: 1, scale: 1 }}
            exit={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, scale: 0.85 }}
            transition={{ duration: 0.18 }}
            className="relative flex items-center justify-center"
          >
            {/* Subtle pulsing neon ring */}
            <span
              aria-hidden="true"
              className="cyber-pulse-ring absolute w-36 h-36 sm:w-44 sm:h-44 rounded-full border border-[#FF174F]/45 shadow-[0_0_36px_rgba(255,23,79,0.22)]"
            />
            <span
              aria-hidden="true"
              className="absolute w-48 h-48 sm:w-56 sm:h-56 rounded-full border border-[#481326]/55 border-dashed"
            />

            <button
              ref={centerBtnRef}
              type="button"
              aria-expanded={false}
              aria-label="Expand TRUSTLENS AI radial navigation"
              onClick={() => setIsOpen(true)}
              className="relative z-10 flex flex-col items-center justify-center w-28 h-28 sm:w-32 sm:h-32 rounded-full bg-gradient-to-b from-[#170A12] to-[#050306] border-2 border-[#FF174F] text-white shadow-[0_0_30px_rgba(255,23,79,0.4)] hover:shadow-[0_0_42px_rgba(255,23,79,0.65)] hover:scale-105 transition-all duration-200 cursor-pointer"
            >
              <Compass className="w-7 h-7 sm:w-8 sm:h-8 text-[#FF3D70] mb-1.5" />
              <span className="font-mono text-[10px] font-bold tracking-[0.2em] uppercase text-white">
                EXPLORE
              </span>
              <span className="font-mono text-[8px] tracking-widest uppercase text-[#A1A1AA] mt-0.5">
                CLICK HUB
              </span>
            </button>
          </motion.div>
        ) : (
          <div key="expanded-wheel">{renderWheel()}</div>
        )}
      </AnimatePresence>
    </div>
  );
}
