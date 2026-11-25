"use client";

import React from "react";
import { PageHeader, MultiClassConfusionMatrixHeatmap } from "@/components/ui";
import { Fingerprint, ShieldAlert, CheckCircle2, Info } from "lucide-react";

const TACTICS_TAXONOMY = [
  {
    code: "H00",
    name: "Urgency and Time Pressure",
    desc: "Forcing immediate action with tight deadlines to bypass rational evaluation.",
    exemplar: "Urgent! Update KYC within 24 hours or account will be permanently closed.",
  },
  {
    code: "H01",
    name: "Threats and Intimidation",
    desc: "Coercion via legal arrest, power disconnection, or severe financial penalties.",
    exemplar: "Power disconnection warning tonight at 9:30 PM due to overdue electric bill.",
  },
  {
    code: "H02",
    name: "OTP & Credential Requests",
    desc: "Direct deceptive harvesting of one-time passwords, netbanking pins, or CVVs.",
    exemplar: "Share the 6-digit verification code sent to your phone to reverse failed charge.",
  },
  {
    code: "H03",
    name: "Financial Manipulation",
    desc: "Fabricated unauthorized debit alerts or fraudulent transaction reversal claims.",
    exemplar: "Your account debited INR 49,999. If not done by you, click here to dispute.",
  },
  {
    code: "H04",
    name: "Bank or Govt Impersonation",
    desc: "Spoofing trusted institutions (SBI, HDFC, Income Tax Dept, Police, TRAI).",
    exemplar: "Official SBI Security Alert: Update PAN mandatory as per RBI guidelines.",
  },
  {
    code: "H05",
    name: "Fake Employment Opportunities",
    desc: "Part-time work-from-home tasks, YouTube rating scams, and upfront deposit demands.",
    exemplar: "Earn 5000 daily working from home! Complete simple video liking tasks.",
  },
  {
    code: "H06",
    name: "Fake Investment Schemes",
    desc: "High-yield crypto returns, pre-IPO stock tips, and deceptive Ponzi schemes.",
    exemplar: "Guaranteed 300% returns in 7 days on crypto arbitrage platform.",
  },
  {
    code: "H07",
    name: "Account Suspension Threats",
    desc: "Simulated lockouts, frozen assets, or dormant account closure ultimatums.",
    exemplar: "Dear Customer, your netbanking profile has been frozen due to KYC expiry.",
  },
  {
    code: "H08",
    name: "Prize and Reward Scams",
    desc: "Lottery winnings, cashback rewards, and luxury gift claim fees.",
    exemplar: "Congratulations! You won INR 25,00,000 in Kaun Banega Crorepati lucky draw.",
  },
  {
    code: "H09",
    name: "Refund & Payment Manipulation",
    desc: "Deceptive double-charge reversals, fake QR codes requesting PIN to receive money.",
    exemplar: "Scan this UPI QR code to accept your INR 1,500 electricity refund immediately.",
  },
];

export default function TacticsIntelligencePage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Social Engineering Tactic Intelligence & 10-Label Taxonomy"
        description="TRUSTLENS AI Model 3 detects and isolates the psychological coercion tactics deployed in deceptive communications."
        badge={{ text: "Model 3: Macro F1 96.8%", variant: "amber" }}
      />

      {/* Interactive Confusion Matrix Heatmap (Image 4 Style) */}
      <MultiClassConfusionMatrixHeatmap />

      {/* 10-Tactic Taxonomy Reference Grid */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-4">
        <div className="flex items-center space-x-2 pb-3 border-b border-slate-100">
          <Fingerprint className="w-4 h-4 text-amber-600" />
          <h3 className="text-sm font-bold text-slate-900">
            Official 10 Social Engineering Manipulation Targets
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {TACTICS_TAXONOMY.map((tac) => (
            <div
              key={tac.code}
              className="p-4 rounded-xl border border-slate-200/90 bg-slate-50/50 hover:bg-white hover:border-amber-300 transition-all space-y-2"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                  <span className="font-mono text-amber-700 bg-amber-100 px-1.5 py-0.5 rounded text-[10px]">
                    {tac.code}
                  </span>
                  <span>{tac.name}</span>
                </span>
                <span className="text-[10px] font-mono text-slate-400">Production Class</span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">{tac.desc}</p>
              <div className="p-2 rounded bg-white border border-slate-200/80 text-[11px] font-mono text-slate-500 italic">
                &ldquo;{tac.exemplar}&rdquo;
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
