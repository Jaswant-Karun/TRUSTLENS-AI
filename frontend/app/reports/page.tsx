"use client";

import React, { useState, useEffect } from "react";
import {
  PageHeader,
  DataTable,
  Column,
  useToast,
  ErrorState,
  MetricCard,
  SearchFilterBar,
} from "@/components/ui";
import { IntelligenceReportPanel } from "@/components/reports/IntelligenceReportPanel";
import {
  getCommunityReports,
  submitCommunityReport,
  reviewCommunityReport,
  getCurrentUser,
  loginUser,
  CommunityReport,
  UserProfile,
} from "@/lib/api";
import {
  Users,
  Send,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ShieldCheck,
  ShieldAlert,
  Search,
  Filter,
  Plus,
  X,
  FileText,
  Tag,
  Check,
  Copy,
  Link as LinkIcon,
  Lock,
  UserCheck,
  LogIn,
} from "lucide-react";

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
  {
    report_id: "rep-004",
    target_type: "sms",
    target_identifier: "VK-SBIBNK",
    content: "Aapka SBI khata turant band ho jayega. Urgent verify karein: http://192.168.1.50/sbi-kyc/update.php",
    description: "Fake SBI KYC message targeting senior citizen users.",
    evidence_urls: ["http://192.168.1.50/sbi-kyc/update.php"],
    status: "verified_scam",
    assigned_tactics: ["urgency_and_time_pressure", "bank_impersonation", "account_suspension_threats"],
    created_at: "24-Nov-2026 09:45",
  },
  {
    report_id: "rep-005",
    target_type: "whatsapp",
    target_identifier: "+44 7911 123456",
    content: "Hello mom, my phone broke and I am using this temporary number. Can you pay my bill urgent?",
    description: "Impersonation of family member requiring immediate wire transfer.",
    evidence_urls: [],
    status: "verified_scam",
    assigned_tactics: ["financial_manipulation", "urgency_and_time_pressure"],
    created_at: "23-Nov-2026 18:30",
  },
];

const AVAILABLE_TACTICS = [
  { id: "urgency_and_time_pressure", label: "Urgency / Pressure" },
  { id: "threats_and_intimidation", label: "Threats & Intimidation" },
  { id: "otp_and_credential_requests", label: "Credential Theft" },
  { id: "financial_manipulation", label: "Financial Manipulation" },
  { id: "bank_impersonation", label: "Brand / Bank Spoofing" },
  { id: "fake_employment_opportunities", label: "Fake Job / Task" },
  { id: "fake_investment_schemes", label: "Fake Investment / Crypto" },
  { id: "account_suspension_threats", label: "Account Suspension" },
  { id: "prize_and_reward_scams", label: "Lottery / Reward" },
  { id: "refund_and_payment_manipulation", label: "Refund / QR Fraud" },
];

export default function ReportsPage() {
  const [reports, setReports] = useState<CommunityReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  // Submit Modal state
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [targetType, setTargetType] = useState("sms");
  const [targetIdentifier, setTargetIdentifier] = useState("");
  const [content, setContent] = useState("");
  const [description, setDescription] = useState("");
  const [evidenceUrl, setEvidenceUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Review Modal state
  const [selectedReport, setSelectedReport] = useState<CommunityReport | null>(null);
  const [reviewVerdict, setReviewVerdict] = useState<"verified_scam" | "under_review" | "benign">("verified_scam");
  const [reviewNotes, setReviewNotes] = useState("");
  const [selectedTactics, setSelectedTactics] = useState<string[]>([]);
  const [reviewing, setReviewing] = useState(false);

  // Auth & Permissions state
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [authenticating, setAuthenticating] = useState(false);

  const { success, error, info } = useToast();

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
    getCurrentUser()
      .then((u) => setCurrentUser(u))
      .catch(() => setCurrentUser(null));
  }, []);

  const canReview = currentUser?.role === "analyst" || currentUser?.role === "admin";

  const handleQuickLogin = async () => {
    setAuthenticating(true);
    try {
      const res = await loginUser("analyst@trustlens.ai", "AnalystPassword123!");
      setCurrentUser(res.user);
      success("Authenticated", "SOC Analyst verification permissions activated.");
    } catch {
      error("Authentication Failed", "Could not authenticate as analyst.");
    } finally {
      setAuthenticating(false);
    }
  };

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
        evidence_urls: evidenceUrl.trim() ? [evidenceUrl.trim()] : undefined,
      });
      success("Report Submitted", "Thank you for contributing to crowd-sourced threat intelligence.");
      setContent("");
      setTargetIdentifier("");
      setDescription("");
      setEvidenceUrl("");
      setShowSubmitModal(false);
      loadReports();
    } catch (err: any) {
      error("Failed to Submit", err.message || "An error occurred submitting the report.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleOpenReview = (report: CommunityReport) => {
    setSelectedReport(report);
    setReviewVerdict(report.status === "benign" ? "benign" : "verified_scam");
    setReviewNotes("");
    setSelectedTactics(report.assigned_tactics || []);
  };

  const handleToggleTactic = (tacticId: string) => {
    setSelectedTactics((prev) =>
      prev.includes(tacticId) ? prev.filter((t) => t !== tacticId) : [...prev, tacticId]
    );
  };

  const handleCommitReview = async () => {
    if (!selectedReport) return;
    setReviewing(true);
    try {
      await reviewCommunityReport(selectedReport.report_id, {
        verdict: reviewVerdict,
        notes: reviewNotes.trim() || undefined,
        assigned_tactics: selectedTactics,
      });

      // Update local state immediately
      setReports((prev) =>
        prev.map((r) =>
          r.report_id === selectedReport.report_id
            ? { ...r, status: reviewVerdict, assigned_tactics: selectedTactics }
            : r
        )
      );

      success("Report Verified", `Submission ${selectedReport.report_id} marked as ${reviewVerdict}.`);
      setSelectedReport(null);
    } catch (err: any) {
      // In case of demo mock fallback
      setReports((prev) =>
        prev.map((r) =>
          r.report_id === selectedReport.report_id
            ? { ...r, status: reviewVerdict, assigned_tactics: selectedTactics }
            : r
        )
      );
      info("Review Recorded", `Status updated locally to ${reviewVerdict}.`);
      setSelectedReport(null);
    } finally {
      setReviewing(false);
    }
  };

  const filteredReports = reports.filter((r) => {
    const matchSearch =
      !search ||
      r.content.toLowerCase().includes(search.toLowerCase()) ||
      r.report_id.toLowerCase().includes(search.toLowerCase()) ||
      (r.target_identifier && r.target_identifier.toLowerCase().includes(search.toLowerCase()));
    const matchStatus = !statusFilter || r.status === statusFilter;
    return matchSearch && matchStatus;
  });

  // Calculate metrics
  const totalCount = reports.length;
  const verifiedScamCount = reports.filter((r) => r.status === "verified_scam").length;
  const underReviewCount = reports.filter((r) => r.status === "under_review").length;
  const benignCount = reports.filter((r) => r.status === "benign").length;

  const columns: Column<CommunityReport>[] = [
    {
      header: "Report ID",
      accessorKey: "report_id",
      cell: (row) => (
        <span className="font-mono text-xs font-bold text-slate-800">
          {row.report_id}
        </span>
      ),
    },
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
      header: "Identifier / Origin",
      accessorKey: "target_identifier",
      className: "font-mono text-xs font-bold text-slate-900",
      cell: (row) => row.target_identifier || "Anonymous Target",
    },
    {
      header: "Reported Content Excerpt",
      accessorKey: "content",
      cell: (row) => (
        <div className="space-y-1">
          <span className="font-mono text-xs text-slate-700 truncate max-w-md block">
            {row.content}
          </span>
          {row.description && (
            <span className="text-[11px] text-slate-400 italic block">
              Note: {row.description}
            </span>
          )}
        </div>
      ),
    },
    {
      header: "Tactics",
      accessorKey: "assigned_tactics",
      cell: (row) => (
        <div className="flex flex-wrap gap-1 max-w-xs">
          {row.assigned_tactics && row.assigned_tactics.length > 0 ? (
            row.assigned_tactics.slice(0, 2).map((t, i) => (
              <span
                key={i}
                className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200"
              >
                {t.replace(/_/g, " ")}
              </span>
            ))
          ) : (
            <span className="text-[11px] text-slate-400 font-mono">Unassigned</span>
          )}
          {row.assigned_tactics && row.assigned_tactics.length > 2 && (
            <span className="text-[10px] font-mono text-slate-400">
              +{row.assigned_tactics.length - 2} more
            </span>
          )}
        </div>
      ),
    },
    {
      header: "Status & Verification",
      accessorKey: "status",
      cell: (row) => {
        if (row.status === "verified_scam") {
          return (
            <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase bg-red-100 text-red-800 border border-red-300">
              <ShieldAlert className="w-3 h-3 text-red-600" />
              <span>Verified Scam</span>
            </span>
          );
        }
        if (row.status === "benign") {
          return (
            <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase bg-emerald-100 text-emerald-800 border border-emerald-300">
              <ShieldCheck className="w-3 h-3 text-emerald-600" />
              <span>Verified Benign</span>
            </span>
          );
        }
        if (row.status === "under_review") {
          return (
            <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase bg-amber-50 text-amber-800 border border-amber-300">
              <Clock className="w-3 h-3 text-amber-600" />
              <span>In Analyst Triage</span>
            </span>
          );
        }
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase border border-dashed bg-slate-100 text-slate-700 border-slate-300">
            <AlertTriangle className="w-3 h-3 text-slate-500" />
            <span>Unverified Submission</span>
          </span>
        );
      },
    },
    {
      header: "Action",
      cell: (row) => {
        if (canReview) {
          return (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleOpenReview(row);
              }}
              className="text-xs px-3 py-1 rounded bg-blue-600 hover:bg-blue-700 text-white font-semibold transition-colors shadow-sm"
            >
              Verify / Review
            </button>
          );
        }
        return (
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleQuickLogin();
            }}
            className="text-[11px] px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200 text-slate-600 font-mono transition-colors border border-slate-200"
            title="Analyst authentication required to review"
          >
            Analyst Login
          </button>
        );
      },
      align: "right",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <PageHeader
          title="Community Threat Reporting & Review Hub"
          description="Contribute suspicious lures, fraudulent UPI IDs, and phishing domains to collective defensive intelligence."
          badge={{ text: "Crowd Intelligence Feed", variant: "blue" }}
        />

        <button
          onClick={() => setShowSubmitModal(true)}
          className="self-start sm:self-auto flex items-center space-x-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Submit Scam Report</span>
        </button>
      </div>

      {/* Permissions & Analyst Role Banner */}
      <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono">
        <div className="flex items-center space-x-2 text-slate-700">
          {canReview ? (
            <>
              <UserCheck className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>
                Analyst Verification Mode: <strong className="text-slate-900">{currentUser?.email}</strong> ({currentUser?.role.toUpperCase()}) — Triage actions enabled.
              </span>
            </>
          ) : (
            <>
              <Lock className="w-4 h-4 text-amber-600 shrink-0" />
              <span>
                Public Contributor Mode — Anyone can submit reports. Sign in as SOC Analyst to access verification controls.
              </span>
            </>
          )}
        </div>

        {!canReview && (
          <button
            onClick={handleQuickLogin}
            disabled={authenticating}
            className="flex items-center space-x-1 px-3 py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-lg text-xs font-semibold transition-colors self-start sm:self-auto disabled:opacity-50"
          >
            <LogIn className="w-3.5 h-3.5" />
            <span>{authenticating ? "Authenticating..." : "Sign in as Analyst"}</span>
          </button>
        )}
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Submissions"
          value={totalCount}
          subtitle="Crowd-sourced signals logged"
          icon={Users}
          accentColor="blue"
        />
        <MetricCard
          title="Verified Scams"
          value={verifiedScamCount}
          subtitle="Confirmed malicious campaigns"
          accentColor="rose"
          icon={ShieldAlert}
        />
        <MetricCard
          title="Under Review"
          value={underReviewCount}
          subtitle="Awaiting analyst triage"
          accentColor="amber"
          icon={Clock}
        />
        <MetricCard
          title="Benign Submissions"
          value={benignCount}
          subtitle="Legitimate communications"
          accentColor="emerald"
          icon={ShieldCheck}
        />
      </div>

      {/* Main Incident Feed Table Card (Full Width) */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-100 gap-2">
          <div className="flex items-center space-x-2">
            <Users className="w-4 h-4 text-slate-700" />
            <h3 className="text-sm font-bold text-slate-900">
              Community Incident Intelligence Feed
            </h3>
          </div>
          <span className="text-xs font-mono text-slate-500">
            {filteredReports.length} Active Records • {verifiedScamCount} Verified Malicious
          </span>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search reports by content, sender, or ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full text-xs font-mono pl-9 pr-4 py-2.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs font-mono px-3 py-2.5 rounded-lg border border-slate-300 bg-white"
          >
            <option value="">All Statuses</option>
            <option value="verified_scam">Verified Scam</option>
            <option value="under_review">Under Review</option>
            <option value="pending">Pending</option>
            <option value="benign">Benign</option>
          </select>
        </div>

        {/* Data Table */}
        <DataTable
          columns={columns}
          data={filteredReports}
          onRowClick={(row) => handleOpenReview(row)}
          emptyTitle="No community reports match criteria"
          emptyDescription="Submit a new threat report using the button above."
        />

        {/* Phase 4.1: Investigation Report Generator & JSON / STIX 2.1 Exports */}
        <IntelligenceReportPanel />
      </div>

      {/* Submit Report Modal */}
      {showSubmitModal && (
        <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <Send className="w-4 h-4 text-blue-600" />
                <h4 className="text-sm font-bold text-slate-900">Submit Suspicious Scam Report</h4>
              </div>
              <button
                onClick={() => setShowSubmitModal(false)}
                className="text-slate-400 hover:text-slate-700 p-1 rounded"
              >
                <X className="w-4 h-4" />
              </button>
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

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Optional Evidence URL or Hosted Screenshot Link
                </label>
                <div className="relative">
                  <LinkIcon className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                  <input
                    type="url"
                    value={evidenceUrl}
                    onChange={(e) => setEvidenceUrl(e.target.value)}
                    placeholder="e.g. https://imgur.com/evidence.png or target link"
                    className="w-full text-xs font-mono pl-8 pr-3 py-2 rounded-lg border border-slate-300 bg-white"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowSubmitModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors flex items-center space-x-1.5 disabled:opacity-50"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{submitting ? "Submitting..." : "Submit to Threat Feed"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* SOC Analyst Verification Studio Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xl max-w-xl w-full p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <ShieldAlert className="w-4 h-4 text-blue-600" />
                <h4 className="text-sm font-bold text-slate-900">
                  SOC Analyst Verification Studio — #{selectedReport.report_id}
                </h4>
              </div>
              <button
                onClick={() => setSelectedReport(null)}
                className="text-slate-400 hover:text-slate-700 p-1 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Target Information */}
            <div className="space-y-3 font-mono text-xs bg-slate-50 p-3.5 rounded-lg border border-slate-200">
              <div className="flex justify-between">
                <span className="text-slate-500">Vector / Protocol:</span>
                <span className="font-bold uppercase text-slate-800">{selectedReport.target_type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Sender / Identifier:</span>
                <span className="font-bold text-slate-900">
                  {selectedReport.target_identifier || "Anonymous"}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block mb-1">Deceptive Lure Text:</span>
                <p className="p-2 bg-white rounded border border-slate-200 text-slate-800 font-sans text-xs">
                  {selectedReport.content}
                </p>
              </div>
            </div>

            {/* Verification Verdict Selector */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-700 block">
                Analyst Classification Verdict:
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setReviewVerdict("verified_scam")}
                  className={`p-2.5 rounded-lg border text-xs font-semibold transition-all ${
                    reviewVerdict === "verified_scam"
                      ? "bg-red-50 border-red-500 text-red-700 ring-2 ring-red-200"
                      : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                  }`}
                >
                  ⚠ Verified Scam
                </button>
                <button
                  type="button"
                  onClick={() => setReviewVerdict("under_review")}
                  className={`p-2.5 rounded-lg border text-xs font-semibold transition-all ${
                    reviewVerdict === "under_review"
                      ? "bg-amber-50 border-amber-500 text-amber-700 ring-2 ring-amber-200"
                      : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                  }`}
                >
                  ⏳ Under Review
                </button>
                <button
                  type="button"
                  onClick={() => setReviewVerdict("benign")}
                  className={`p-2.5 rounded-lg border text-xs font-semibold transition-all ${
                    reviewVerdict === "benign"
                      ? "bg-emerald-50 border-emerald-500 text-emerald-700 ring-2 ring-emerald-200"
                      : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                  }`}
                >
                  ✓ Benign
                </button>
              </div>
            </div>

            {/* Assign Tactics Selector */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-700 block">
                Assign Social Engineering Tactics:
              </label>
              <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto p-1">
                {AVAILABLE_TACTICS.map((tac) => {
                  const selected = selectedTactics.includes(tac.id);
                  return (
                    <button
                      key={tac.id}
                      type="button"
                      onClick={() => handleToggleTactic(tac.id)}
                      className={`text-[11px] font-mono px-2 py-1 rounded-md border transition-colors flex items-center space-x-1 ${
                        selected
                          ? "bg-blue-600 text-white border-blue-600"
                          : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100"
                      }`}
                    >
                      {selected && <Check className="w-3 h-3" />}
                      <span>{tac.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Analyst Notes */}
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Verification Notes & Attribution Evidence:
              </label>
              <textarea
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                rows={2}
                placeholder="Document observed indicators, spoofed brand name, or victim impact..."
                className="w-full text-xs font-mono p-2 rounded-lg border border-slate-300 bg-white"
              />
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setSelectedReport(null)}
                className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleCommitReview}
                disabled={reviewing}
                className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-all flex items-center space-x-1.5 disabled:opacity-50"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{reviewing ? "Committing..." : "Commit Verification"}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
