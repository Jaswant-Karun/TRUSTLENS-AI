import type { Metadata } from "next";
import { LandingExperience } from "@/components/product/LandingExperience";

export const metadata: Metadata = {
  title: "TRUSTLENS AI — Intelligence That Stops Digital Fraud",
  description:
    "Detect suspicious messages, malicious URLs and emerging digital fraud campaigns using multilingual ML analysis, zero-hop URL inspection, screenshot OCR, and evidence-backed investigations.",
  keywords: [
    "digital fraud detection",
    "phishing URL scanner",
    "multilingual scam detection",
    "social engineering intelligence",
    "TRUSTLENS AI",
  ],
  openGraph: {
    title: "TRUSTLENS AI — Multilingual Digital Fraud Intelligence",
    description:
      "Evidence-backed scam message analysis, zero-hop phishing URL inspection, screenshot OCR, and case investigation workflows.",
    type: "website",
  },
};

export default function LandingPage() {
  return <LandingExperience />;
}
