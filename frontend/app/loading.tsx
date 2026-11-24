import React from "react";
import { SkeletonMetrics, SkeletonCard } from "@/components/ui/LoadingStates";

export default function Loading() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-12 w-64 bg-slate-200 rounded-lg"></div>
      <SkeletonMetrics />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    </div>
  );
}
