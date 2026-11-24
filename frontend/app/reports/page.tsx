"use client";

import React, { useState, useEffect } from "react";
import {
  PageHeader,
  DataTable,
  Column,
  useToast,
  ErrorState,
} from "@/components/ui";
import {
  getCommunityReports,
  submitCommunityReport,
  CommunityReport,
} from "@/lib/api";
import { Users, Send, AlertTriangle, CheckCircle2, Clock, ShieldCheck } from "lucide-react";

const BACKUP_REPORTS: CommunityReport[] = [
  {
    report_id: "rep-001",
    target_type: "sms",
    target_identifier: "+91 98402 11928",
    content: "Earn 5000 daily part-time job from home! Complete simple YouTube tasks.",
    description: "Received via WhatsApp unsolicited from unknown international number.",
    evidence_urls: [],
    status: "verified_scam",
    assigned_tactics: ["fake_employment_opportunities", "financial_manipulation"],
    created_at: "24-Nov-2026 12:40",
  },
  {
    report_id: "rep-002",
    target_type: "url",
    target_identifier: "http://secure-login-hdfcbank-account-update.xyz",
    content: "Fake netbanking portal mimicking HDFC Bank KYC verification.",
    description: "Sent via SMS pretending to be HDFC bank notice.",
    evidence_urls: ["http://secure-login-hdfcbank-account-update.xyz"],
    status: "verified_scam",
    assigned_tactics: ["bank_impersonation", "otp_and_credential_requests"],
    created_at: "24-Nov-2026 11:15",
  },
  {
    report_id: "rep-003",
    target_type: "upi",
    target_identifier: "refund-merchant@ybl",
    content: "Deceptive QR code asking for UPI PIN to receive electricity bill refund.",
    description: "User was asked to approve request in PhonePe.",
    evidence_urls: [],
    status: "under_review",
    assigned_tactics: ["refund_and_payment_manipulation"],
    created_at: "24-Nov-2026 10:20",
  },
];

export default function ReportsPage() {
  const [reports, setReports] = useState<CommunityReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [targetType, setTargetType] = useState("sms");
  const [targetIdentifier, setTargetIdentifier] = useState("");
  const [content, setContent] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { success, error } = useToast();

  const loadReports = () => {
    getCommunityReports()
      .then((data) => {
        if (data && data.items && data.items.length > 0) {
          setReports(data.items);
        } else {
          setReports(BACKUP_REPORTS);
        }
        setLoading(false);
      })
      .catch(() => {
        setReports(BACKUP_REPORTS);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadReports();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) {
      error("Submission Error", "Please provide the scam communication content.");
      return;
    }

    setSubmitting(true);
    try {
      const newReport = await submitCommunityReport({
        target_type: targetType,
        target_identifier: targetIdentifier.trim() || undefined,
        content,
        description: description.trim() || undefined,
      });
      success("Report Submitted", "Thank you for contributing to crowd-sourced threat intelligence.");
      setContent("");
      setTargetIdentifier("");
      setDescription("");
      loadReports();
    } catch (err: any) {
      error("Failed to Submit", err.message || "An error occurred submitting the report.");
    } finally {
      setSubmitting(false);
    }
  };

  const columns: Column<CommunityReport>[] = [
    {
      header: "Vector",
      accessorKey: "target_type",
      cell: (row) => (
        <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[11px] uppercase border border-slate-200">
          {row.target_type}
        </span>
      ),
    },
    {
      header: "Identifier / Sender",
      accessorKey: "target_identifier",
      className: "font-mono text-xs font-bold text-slate-900",
      cell: (row) => row.target_identifier || "Anonymous Target",
    },
    {
      header: "Reported Content Excerpt",
      accessorKey: "content",
      cell: (row) => (
        <span className="font-mono text-xs text-slate-700 truncate max-w-sm block">
          {row.content}
        </span>
      ),
    },
    {
      header: "Verification Status",
      accessorKey: "status",
      cell: (row) => {
        const styles = {
          verified_scam: "bg-red-50 text-red-700 border-red-200",
          under_review: "bg-amber-50 text-amber-700 border-amber-200",
          pending: "bg-slate-100 text-slate-700 border-slate-200",
          benign: "bg-emerald-50 text-emerald-700 border-emerald-200",
        };
        return (
          <span
            className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase border ${
              styles[row.status] || styles.pending
            }`}
          >
            {row.status.replace(/_/g, " ")}
          </span>
        );
      },
    },
    {
      header: "Reported At",
      accessorKey: "created_at",
      className: "font-mono text-xs text-slate-500",
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Community Threat Reporting & Review Hub"
        description="Contribute suspicious lures, fraudulent UPI IDs, and phishing domains to collective defensive intelligence."
        badge={{ text: "Crowd Intelligence", variant: "blue" }}
      />

      {/* Grid: Submit Report on Left, Live Community Feed on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Submit New Report Card */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-4">
          <div className="flex items-center space-x-2 pb-3 border-b border-slate-100">
            <Send className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900">Submit Suspicious Scam</h3>
          </div>

          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Scam Vector Type
              </label>
              <select
                value={targetType}
                onChange={(e) => setTargetType(e.target.value)}
                className="w-full text-xs font-mono p-2 rounded-lg border border-slate-300 bg-white"
              >
                <option value="sms">SMS Text Message</option>
                <option value="whatsapp">WhatsApp / Messaging</option>
                <option value="url">Phishing Web URL</option>
                <option value="upi">Fraudulent UPI / Payment</option>
                <option value="email">Email Phishing</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Sender Number / URL / Identifier
              </label>
              <input
                type="text"
                value={targetIdentifier}
                onChange={(e) => setTargetIdentifier(e.target.value)}
                placeholder="e.g. +91 98402 11928 or domain.xyz"
                className="w-full text-xs font-mono p-2 rounded-lg border border-slate-300 bg-white"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Deceptive Content / Lure Text *
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={3}
                placeholder="Paste the suspicious communication body..."
                className="w-full text-xs font-mono p-2 rounded-lg border border-slate-300 bg-white"
                required
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Victim Context / Notes (Optional)
              </label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g. Asked for upfront registration fee"
                className="w-full text-xs font-mono p-2 rounded-lg border border-slate-300 bg-white"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors flex items-center justify-center space-x-1.5 disabled:opacity-50"
            >
              <Send className="w-3.5 h-3.5" />
              <span>{submitting ? "Submitting Report..." : "Submit to Threat Feed"}</span>
            </button>
          </form>
        </div>

        {/* Right: Community Submissions Table (2 Cols) */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <Users className="w-4 h-4 text-slate-600" />
              <h3 className="text-sm font-bold text-slate-900">Community Incident Intelligence</h3>
            </div>
            <span className="text-xs font-mono text-slate-500">{reports.length} Submissions</span>
          </div>

          <DataTable
            columns={columns}
            data={reports}
            emptyTitle="No community reports recorded yet"
            emptyDescription="Submit the first threat lure using the form."
          />
        </div>
      </div>
    </div>
  );
}
