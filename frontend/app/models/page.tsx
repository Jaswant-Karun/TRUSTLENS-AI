"use client";

import React from "react";
import { PageHeader } from "@/components/ui";
import ModelGovernancePanel from "@/components/ModelGovernancePanel";
import { Cpu, ShieldCheck, Database, Layers } from "lucide-react";

export default function ModelsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="ML Center: Model Governance & Production Verification"
        description="Rigorous held-out test evaluation benchmarks, multi-class confusion matrices, and SHAP explainability across all 4 machine learning engines."
        badge={{ text: "100% Production Verified", variant: "green" }}
      />

      {/* Model Architecture Metadata Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-subtle space-y-1.5">
          <span className="text-[10px] font-mono uppercase text-blue-600 font-semibold block">Model 1</span>
          <div className="text-xs font-bold text-slate-900">Multilingual Scam Classifier</div>
          <p className="text-[11px] text-slate-500 font-mono">Bi-LSTM + FastText (EN/HI/Hinglish)</p>
          <div className="pt-2 text-xs font-mono font-bold text-slate-800">F1: 97.6% (8,202 samples)</div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-subtle space-y-1.5">
          <span className="text-[10px] font-mono uppercase text-cyan-600 font-semibold block">Model 2</span>
          <div className="text-xs font-bold text-slate-900">Zero-Hop URL Detector</div>
          <p className="text-[11px] text-slate-500 font-mono">XGBoost on 38 Lexical Features</p>
          <div className="pt-2 text-xs font-mono font-bold text-slate-800">ROC-AUC: 1.000 (16,066 test)</div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-subtle space-y-1.5">
          <span className="text-[10px] font-mono uppercase text-amber-600 font-semibold block">Model 3</span>
          <div className="text-xs font-bold text-slate-900">Social Engineering Tactics</div>
          <p className="text-[11px] text-slate-500 font-mono">One-vs-Rest Linear SVM (10 labels)</p>
          <div className="pt-2 text-xs font-mono font-bold text-slate-800">Macro F1: 96.8% (4,780 test)</div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-subtle space-y-1.5">
          <span className="text-[10px] font-mono uppercase text-teal-600 font-semibold block">Model 4</span>
          <div className="text-xs font-bold text-slate-900">Campaign Clustering</div>
          <p className="text-[11px] text-slate-500 font-mono">Sentence Transformers + HDBSCAN</p>
          <div className="pt-2 text-xs font-mono font-bold text-slate-800">47 Active Clusters (Cohesion 0.88)</div>
        </div>
      </div>

      {/* Central Model Governance Heatmap & Binary Validation */}
      <ModelGovernancePanel id="models-governance" />
    </div>
  );
}
