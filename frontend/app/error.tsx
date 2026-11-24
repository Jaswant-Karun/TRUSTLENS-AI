"use client";

import React, { useEffect } from "react";
import { AlertOctagon, RotateCcw } from "lucide-react";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Route error boundary caught:", error);
  }, [error]);

  return (
    <div className="bg-white rounded-xl border border-red-200 p-8 shadow-card text-center max-w-lg mx-auto my-12 space-y-4">
      <div className="w-12 h-12 rounded-full bg-red-50 border border-red-200 flex items-center justify-center mx-auto text-red-600">
        <AlertOctagon className="w-6 h-6" />
      </div>
      <h2 className="text-base font-bold text-slate-900">Module Execution Error</h2>
      <p className="text-xs text-slate-600 font-mono">
        {error.message || "An unexpected error occurred while loading this security module."}
      </p>
      <div className="pt-2">
        <button
          onClick={() => reset()}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reload Module</span>
        </button>
      </div>
    </div>
  );
}
