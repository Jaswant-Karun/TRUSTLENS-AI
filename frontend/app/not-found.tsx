import React from "react";
import Link from "next/link";
import { ShieldAlert, ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-card text-center max-w-md mx-auto my-16 space-y-4">
      <div className="w-12 h-12 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center mx-auto text-slate-500">
        <ShieldAlert className="w-6 h-6" />
      </div>
      <h2 className="text-base font-bold text-slate-900">404 — Route Not Found</h2>
      <p className="text-xs text-slate-500">
        The requested security module or investigation dossier does not exist.
      </p>
      <div className="pt-2">
        <Link
          href="/dashboard"
          className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Return to Dashboard</span>
        </Link>
      </div>
    </div>
  );
}
