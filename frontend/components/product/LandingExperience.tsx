"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import {
  ArrowRight,
  Lock,
  MessageSquareWarning,
  Link2,
  ScanSearch,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { getStoredToken, getHealth, SystemHealth } from "@/lib/api";
import { RadialNavigation } from "@/components/product/RadialNavigation";
import { NeonFrame } from "@/components/product/NeonFrame";
import { GlowButton } from "@/components/product/GlowButton";
import { GlowEffect } from "@/components/product/GlowEffect";

export function LandingExperience() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const shouldReduceMotion = useReducedMotion();

  useEffect(() => {
    setIsAuthenticated(Boolean(getStoredToken()));
    getHealth()
      .then((res: SystemHealth) => setHealth(res))
      .catch(() => setHealth(null));
  }, []);

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col items-center px-4 py-8 sm:px-6 sm:py-12">
      {/* Live Engine Status Pill (Real Backend Health) */}
      <motion.div
        initial={shouldReduceMotion ? false : { opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="mb-6 inline-flex items-center gap-2.5 rounded-full border border-[#481326] bg-[#10070D]/90 px-4 py-1.5 text-xs font-mono uppercase tracking-widest"
      >
        <span
          className={`h-2 w-2 rounded-full ${
            health?.status === "healthy" || health?.database_connected
              ? "bg-[#00D68F] shadow-[0_0_8px_#00D68F]"
              : "bg-[#FFB020]"
          }`}
        />
        <span className="text-[#A1A1AA]">
          ML CORE:{" "}
          <span className="text-white">
            {health?.database_connected ? "OPERATIONAL" : "STANDBY"}
          </span>
        </span>
        <span className="text-[#481326]">|</span>
        <span className="text-[#FF3D70]">ZERO-HOP URL SAFETY</span>
      </motion.div>

      {/* Animated Product Branding & Hero Headline */}
      <motion.header
        initial={shouldReduceMotion ? false : { opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45 }}
        className="max-w-3xl text-center"
      >
        <div className="mb-4 inline-flex items-center justify-center">
          <GlowEffect intensity="medium" pulse={!shouldReduceMotion} className="rounded-full">
            <div className="inline-flex items-center gap-2 rounded-full border border-[#FF174F]/60 bg-[#170A12]/90 px-4 py-1.5 font-mono text-[11px] font-bold uppercase tracking-[0.25em] text-white">
              <Sparkles className="h-3.5 w-3.5 text-[#FF3D70]" />
              <span>TRUSTLENS AI</span>
            </div>
          </GlowEffect>
        </div>

        <h1 className="font-mono text-3xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-[3.25rem] lg:leading-[1.12]">
          INTELLIGENCE THAT STOPS{" "}
          <span className="bg-gradient-to-r from-[#FF174F] to-[#FF3D70] bg-clip-text text-transparent">
            DIGITAL FRAUD.
          </span>
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-sm leading-relaxed text-[#A1A1AA] sm:text-base">
          Detect suspicious messages, malicious URLs and emerging digital fraud
          campaigns using intelligent multilingual analysis and real-world threat
          intelligence.
        </p>

        {/* Primary & Secondary CTAs */}
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          {isAuthenticated ? (
            <>
              <Link href="/analyze/text">
                <GlowButton variant="primary" size="lg">
                  OPEN MESSAGE SCANNER
                  <ArrowRight className="h-4 w-4" />
                </GlowButton>
              </Link>
              <Link href="/investigations">
                <GlowButton variant="secondary" size="lg">
                  INVESTIGATIONS
                </GlowButton>
              </Link>
            </>
          ) : (
            <>
              <Link href="/register">
                <GlowButton variant="primary" size="lg">
                  GET STARTED
                  <ArrowRight className="h-4 w-4" />
                </GlowButton>
              </Link>
              <Link href="/login">
                <GlowButton variant="secondary" size="lg">
                  SIGN IN
                </GlowButton>
              </Link>
            </>
          )}
        </div>
      </motion.header>

      {/* Central Interactive Radial Navigation */}
      <section
        aria-label="Interactive Radial Navigation"
        className="my-6 flex w-full flex-col items-center justify-center"
      >
        <RadialNavigation variant="hero" />
        <p className="mt-1 font-mono text-[11px] uppercase tracking-[0.2em] text-[#A1A1AA] text-center">
          CLICK CENTER HUB TO ACCESS WORKFLOWS • ESC OR CLICK OUTSIDE TO CLOSE
        </p>
      </section>

      {/* Genuine Capabilities & Security Messaging (No Dashboard Cards) */}
      <section
        aria-label="Core Capabilities"
        className="mt-6 grid w-full grid-cols-1 gap-4 md:grid-cols-3"
      >
        <NeonFrame className="p-5">
          <div className="flex items-center gap-2.5 text-[#FF3D70]">
            <MessageSquareWarning className="h-5 w-5" />
            <h2 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
              Multilingual Message Analysis
            </h2>
          </div>
          <p className="mt-2.5 text-xs leading-relaxed text-[#A1A1AA]">
            Evaluates SMS, WhatsApp, and email text across English, Hindi
            (Devanagari), and Hinglish with calibrated risk scores and
            social-engineering tactic attribution.
          </p>
        </NeonFrame>

        <NeonFrame className="p-5">
          <div className="flex items-center gap-2.5 text-[#FF3D70]">
            <Link2 className="h-5 w-5" />
            <h2 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
              Zero-Hop URL Shield
            </h2>
          </div>
          <p className="mt-2.5 text-xs leading-relaxed text-[#A1A1AA]">
            Inspects 16 lexical and structural URL features using XGBoost and
            SHAP without ever opening, fetching, or executing the submitted link.
          </p>
        </NeonFrame>

        <NeonFrame className="p-5">
          <div className="flex items-center gap-2.5 text-[#FF3D70]">
            <ScanSearch className="h-5 w-5" />
            <h2 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
              Screenshot OCR & Case Trails
            </h2>
          </div>
          <p className="mt-2.5 text-xs leading-relaxed text-[#A1A1AA]">
            Validates PNG, JPEG, and WebP screenshots, extracts embedded text,
            and lets authenticated users attach evidence to persistent
            investigations.
          </p>
        </NeonFrame>
      </section>

      {/* Security & Transparency Assurance */}
      <NeonFrame variant="secondary" className="mt-6 w-full p-4 sm:p-5">
        <div className="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center">
          <div className="flex items-start gap-3">
            <Lock className="mt-0.5 h-4 w-4 shrink-0 text-[#00D68F]" />
            <p className="text-xs leading-relaxed text-[#A1A1AA]">
              <span className="font-semibold text-white">
                Security &amp; Privacy Guarantees:
              </span>{" "}
              Submitted URLs are never visited or executed. Private
              investigations are isolated per account via JWT/RBAC. Campaign
              clustering reflects linguistic and indicator similarity, not legal
              proof of common criminal origin.
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-2 text-[11px] font-mono text-[#A1A1AA]">
            <ShieldCheck className="h-4 w-4 text-[#FF174F]" />
            <span>FASTAPI + ML CORE</span>
          </div>
        </div>
      </NeonFrame>
    </div>
  );
}
