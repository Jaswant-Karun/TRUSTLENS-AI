"use client";

import React from "react";
import { ListFilter, ShieldX, AlertTriangle, ShieldCheck } from "lucide-react";

interface Incident {
  time: string;
  channel: string;
  sender: string;
  preview: string;
  classification: string;
  severity: "critical" | "high" | "medium" | "clean";
  action: string;
}

const RECENT_INCIDENTS: Incident[] = [
  {
    time: "22:14:02",
    channel: "SMS (Hinglish)",
    sender: "VK-SBIBNK",
    preview: "Aapka SBI khata turant band ho jayega. Urgent verify karein...",
    classification: "Smishing / Banking",
    severity: "critical",
    action: "Blocked",
  },
  {
    time: "22:11:45",
    channel: "URL",
    sender: "Web Request",
    preview: "http://203.0.113.15/secure-login-portal/auth.php",
    classification: "Credential Phishing",
    severity: "critical",
    action: "Domain Blocked",
  },
  {
    time: "22:08:19",
    channel: "WhatsApp",
    sender: "+91 98402 11928",
    preview: "Earn 5000 daily part-time job from home! Complete simple YouTube tasks...",
    classification: "Fake Employment Scam",
    severity: "high",
    action: "Flagged",
  },
  {
    time: "22:04:33",
    channel: "Email",
    sender: "billing@hdfc-updates-kyc.top",
    preview: "Notice: Your KYC renewal period has lapsed. Re-enter credentials...",
    classification: "Phishing Lure",
    severity: "high",
    action: "Quarantined",
  },
  {
    time: "21:58:12",
    channel: "SMS (English)",
    sender: "AD-SWIGGY",
    preview: "Your dinner order #99281 has been picked up by the delivery partner.",
    classification: "Legitimate Transaction",
    severity: "clean",
    action: "Allowed",
  },
];

export default function IncidentFeed() {
  return (
    <div className="bg-card border border-border rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center space-x-2">
            <ListFilter className="w-4 h-4 text-slate-400" />
            <span>Recent Threat Intelligence Feed & Detection Log</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time feed of multi-channel digital communications decomposed and analyzed by TRUSTLENS AI.
          </p>
        </div>
        <div className="text-xs font-mono text-slate-500">
          Showing 5 latest events
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-surface text-slate-400 border-b border-border uppercase">
            <tr>
              <th className="py-2.5 px-3">Time</th>
              <th className="py-2.5 px-3">Vector</th>
              <th className="py-2.5 px-3">Sender / Source</th>
              <th className="py-2.5 px-3">Payload Excerpt</th>
              <th className="py-2.5 px-3">Classification</th>
              <th className="py-2.5 px-3">Severity</th>
              <th className="py-2.5 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {RECENT_INCIDENTS.map((inc, i) => (
              <tr key={i} className="hover:bg-surface/50 transition-colors">
                <td className="py-2.5 px-3 text-slate-400">{inc.time}</td>
                <td className="py-2.5 px-3 text-slate-300 font-semibold">{inc.channel}</td>
                <td className="py-2.5 px-3 text-slate-400">{inc.sender}</td>
                <td className="py-2.5 px-3 text-slate-300 max-w-xs truncate">{inc.preview}</td>
                <td className="py-2.5 px-3 text-slate-200">{inc.classification}</td>
                <td className="py-2.5 px-3">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${
                      inc.severity === "critical"
                        ? "bg-cyberRed/20 text-cyberRed border border-cyberRed/30"
                        : inc.severity === "high"
                        ? "bg-cyberAmber/20 text-cyberAmber border border-cyberAmber/30"
                        : "bg-cyberGreen/20 text-cyberGreen border border-cyberGreen/30"
                    }`}
                  >
                    {inc.severity}
                  </span>
                </td>
                <td className="py-2.5 px-3 text-right">
                  <span className="text-slate-300">{inc.action}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
