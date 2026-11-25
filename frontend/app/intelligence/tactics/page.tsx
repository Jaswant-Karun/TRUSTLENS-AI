"use client";

import React from "react";
import { PageHeader, MultiClassConfusionMatrixHeatmap } from "@/components/ui";
import { Fingerprint } from "lucide-react";

const TACTICS_TAXONOMY = [
  {
    code: "H00",
    name: "Urgency and Time Pressure",
    supported: true,
    desc: "Forcing immediate action with tight deadlines to bypass rational evaluation.",
    exemplar: "Urgent! Update KYC within 24 hours or account will be permanently closed.",
  },
  {
    code: "H01",
    name: "Threats and Intimidation",
    supported: true,
    desc: "Coercion via legal arrest, power disconnection, or severe financial penalties.",
    exemplar: "Power disconnection warning tonight at 9:30 PM due to overdue electric bill.",
  },
  {
    code: "H02",
    name: "OTP & Credential Requests",
    supported: true,
    desc: "Direct deceptive harvesting of one-time passwords, netbanking pins, or CVVs.",
    exemplar: "Share the 6-digit verification code sent to your phone to reverse failed charge.",
  },
  {
    code: "H03",
    name: "Financial Manipulation",
    supported: true,
    desc: "Fabricated unauthorized debit alerts or fraudulent transaction reversal claims.",
    exemplar: "Your account debited INR 49,999. If not done by you, click here to dispute.",
  },
  {
    code: "H04",
    name: "Bank or Govt Impersonation",
    supported: true,
    desc: "Spoofing trusted institutions (SBI, HDFC, Income Tax Dept, Police, TRAI).",
    exemplar: "Official SBI Security Alert: Update PAN mandatory as per RBI guidelines.",
  },
  {
    code: "H05",
    name: "Fake Employment Opportunities",
    supported: true,
    desc: "Part-time work-from-home tasks, YouTube rating scams, and upfront deposit demands.",
    exemplar: "Earn 5000 daily working from home! Complete simple video liking tasks.",
  },
  {
    code: "H06",
    name: "Fake Investment Schemes",
    supported: false,
    desc: "High-yield crypto returns, pre-IPO stock tips, and deceptive Ponzi schemes.",
    exemplar: "UNAVAILABLE: Missing verified ground-truth training annotations in benchmark corpus.",
  },
  {
    code: "H07",
    name: "Account Suspension Threats",
    supported: true,
    desc: "Simulated lockouts, frozen assets, or dormant account closure ultimatums.",
    exemplar: "Dear Customer, your netbanking profile has been frozen due to KYC expiry.",
  },
  {
    code: "H08",
    name: "Prize and Reward Scams",
    supported: true,
    desc: "Lottery winnings, cashback rewards, and luxury gift claim fees.",
    exemplar: "Congratulations! You won INR 25,00,000 in lucky draw.",
  },
  {
    code: "H09",
    name: "Refund & Payment Manipulation",
    supported: true,
    desc: "Deceptive double-charge reversals, fake QR codes requesting PIN to receive money.",
    exemplar: "Scan this UPI QR code to accept your INR 1,500 electricity refund immediately.",
  },
];

export default function TacticsIntelligencePage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Social Engineering Tactic Intelligence"
        description="TRUSTLENS AI Model 3 isolates psychological coercion tactics deployed in deceptive communications (9 active classes; H06 unavailable without ground truth)."
        badge={{ text: "Model 3: Micro F1 95.1%", variant: "amber" }}
      />

      <MultiClassConfusionMatrixHeatmap />

      <div className="cyber-panel p-6 space-y-4">
        <div className="flex items-center space-x-2 pb-3 border-b border-[#481326]">
          <Fingerprint className="w-4 h-4 text-[#FF3D70]" />
          <h3 className="text-sm font-mono font-bold uppercase text-white">
            10 Social Engineering Manipulation Targets
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {TACTICS_TAXONOMY.map((tac) => (
            <div
              key={tac.code}
              className="p-4 rounded-xl border border-[#481326] bg-[#050306]/80 hover:border-[#FF174F]/60 transition-all space-y-2"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-bold text-white flex items-center gap-1.5">
                  <span className="font-mono text-[#FF3D70] bg-[#170A12] border border-[#481326] px-1.5 py-0.5 rounded text-[10px]">
                    {tac.code}
                  </span>
                  <span>{tac.name}</span>
                </span>
                <span
                  className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                    tac.supported
                      ? "text-[#00D68F] bg-[#00D68F]/10"
                      : "text-[#FFB020] bg-[#FFB020]/10"
                  }`}
                >
                  {tac.supported ? "Active" : "Unavailable"}
                </span>
              </div>
              <p className="text-xs text-[#A1A1AA] leading-relaxed">{tac.desc}</p>
              <div className="p-2 rounded bg-[#10070D] border border-[#481326]/70 text-[11px] font-mono text-[#A1A1AA] italic">
                &ldquo;{tac.exemplar}&rdquo;
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
