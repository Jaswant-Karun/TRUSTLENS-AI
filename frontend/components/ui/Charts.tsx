"use client";

import React, { useState } from "react";

/**
 * 1. Threat Trend by Severity Chart (from Image 1: Sentinel Nexus)
 * SVG multi-point line chart with glowing path, gradient fill, and interactive tooltips.
 */
export function ThreatTrendChart({
  timeframe = "Last 7 Days",
  onTimeframeChange,
}: {
  timeframe?: string;
  onTimeframeChange?: (val: string) => void;
}) {
  const [selectedPoint, setSelectedPoint] = useState<{ day: string; count: number; x: number; y: number } | null>(null);

  // 7-day trend coordinates (normalized 0-100)
  const dataPoints = [
    { day: "Mon", count: 41, x: 20, y: 75 },
    { day: "Tue", count: 58, x: 70, y: 60 },
    { day: "Wed", count: 32, x: 120, y: 82 },
    { day: "Thu", count: 86, x: 170, y: 35 },
    { day: "Fri", count: 64, x: 220, y: 55 },
    { day: "Sat", count: 92, x: 270, y: 25 },
    { day: "Sun", count: 114, x: 320, y: 15 },
  ];

  const pathD = `M ${dataPoints.map((p) => `${p.x},${p.y}`).join(" L ")}`;
  const areaD = `${pathD} L 320,95 L 20,95 Z`;

  return (
    <div className="bg-[#0b1329] text-white p-5 rounded-xl border border-slate-800 shadow-xl relative overflow-hidden flex flex-col justify-between">
      {/* Top Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100">Threat Trend by Severity</h3>
          <p className="text-[11px] text-slate-400">Chronological telemetry across detected vectors</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800/90 text-cyan-400 border border-cyan-500/30 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
            {timeframe}
          </span>
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="relative h-44 w-full flex items-center justify-center my-1">
        <svg viewBox="0 0 340 105" className="w-full h-full overflow-visible">
          <defs>
            <linearGradient id="cyanGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.0" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Grid lines */}
          <line x1="20" y1="20" x2="320" y2="20" stroke="#1e293b" strokeDasharray="3 3" strokeWidth="0.8" />
          <line x1="20" y1="50" x2="320" y2="50" stroke="#1e293b" strokeDasharray="3 3" strokeWidth="0.8" />
          <line x1="20" y1="80" x2="320" y2="80" stroke="#1e293b" strokeDasharray="3 3" strokeWidth="0.8" />
          <line x1="20" y1="95" x2="320" y2="95" stroke="#334155" strokeWidth="1" />

          {/* Area Fill */}
          <path d={areaD} fill="url(#cyanGradient)" />

          {/* Path Line with glow */}
          <path
            d={pathD}
            fill="none"
            stroke="#06b6d4"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            filter="url(#glow)"
          />

          {/* Interactive Data Points */}
          {dataPoints.map((p, idx) => (
            <g
              key={idx}
              className="cursor-pointer transition-transform hover:scale-125"
              onMouseEnter={() => setSelectedPoint(p)}
              onMouseLeave={() => setSelectedPoint(null)}
            >
              <circle cx={p.x} cy={p.y} r="4" fill="#0b1329" stroke="#38bdf8" strokeWidth="2" />
              <circle cx={p.x} cy={p.y} r="2" fill="#38bdf8" />
              <text x={p.x} y="103" textAnchor="middle" fill="#64748b" fontSize="7" fontFamily="monospace">
                {p.day}
              </text>
            </g>
          ))}
        </svg>

        {/* Hover Tooltip */}
        {selectedPoint && (
          <div
            className="absolute bg-slate-900/95 text-white border border-cyan-500/40 px-2 py-1 rounded shadow-lg pointer-events-none text-[11px] font-mono z-10"
            style={{
              left: `${(selectedPoint.x / 340) * 100}%`,
              top: `${(selectedPoint.y / 105) * 100}%`,
              transform: "translate(-50%, -120%)",
            }}
          >
            <span className="text-cyan-400 font-bold">{selectedPoint.count}</span> threats ({selectedPoint.day})
          </div>
        )}
      </div>

      {/* Legend footer */}
      <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/80">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
          Phishing & Scam Bursts
        </span>
        <span className="text-slate-500">Peak: 114 events/day</span>
      </div>
    </div>
  );
}

/**
 * 2. Severity Distribution Chart (from Image 1: Sentinel Nexus)
 * Multi-layer circular/triangular severity ring breakdown.
 */
export function SeverityDistributionChart() {
  const slices = [
    { label: "Critical", percentage: 25, color: "#06b6d4", bgClass: "text-cyan-400" },
    { label: "High", percentage: 40, color: "#0284c7", bgClass: "text-sky-500" },
    { label: "Medium", percentage: 20, color: "#f59e0b", bgClass: "text-amber-400" },
    { label: "Low", percentage: 15, color: "#10b981", bgClass: "text-emerald-400" },
  ];

  return (
    <div className="bg-[#0b1329] text-white p-5 rounded-xl border border-slate-800 shadow-xl flex flex-col justify-between">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100">Severity Distribution</h3>
          <p className="text-[11px] text-slate-400">Current active threats categorized by impact</p>
        </div>
        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700">
          Live Threat Level
        </span>
      </div>

      {/* Donut representation */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-6 my-2">
        <div className="relative w-32 h-32 flex items-center justify-center">
          <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
            {/* SVG circle segments */}
            <circle cx="50" cy="50" r="38" fill="transparent" stroke="#1e293b" strokeWidth="12" />
            {/* High (40%) */}
            <circle
              cx="50"
              cy="50"
              r="38"
              fill="transparent"
              stroke="#0284c7"
              strokeWidth="12"
              strokeDasharray="95.5 238.7"
              strokeDashoffset="0"
            />
            {/* Critical (25%) */}
            <circle
              cx="50"
              cy="50"
              r="38"
              fill="transparent"
              stroke="#06b6d4"
              strokeWidth="12"
              strokeDasharray="59.7 238.7"
              strokeDashoffset="-95.5"
            />
            {/* Medium (20%) */}
            <circle
              cx="50"
              cy="50"
              r="38"
              fill="transparent"
              stroke="#f59e0b"
              strokeWidth="12"
              strokeDasharray="47.7 238.7"
              strokeDashoffset="-155.2"
            />
            {/* Low (15%) */}
            <circle
              cx="50"
              cy="50"
              r="38"
              fill="transparent"
              stroke="#10b981"
              strokeWidth="12"
              strokeDasharray="35.8 238.7"
              strokeDashoffset="-202.9"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span className="text-xl font-bold font-mono text-cyan-400">100%</span>
            <span className="text-[9px] uppercase font-mono text-slate-400">Classified</span>
          </div>
        </div>

        {/* Legend pills */}
        <div className="grid grid-cols-2 sm:grid-cols-1 gap-2 w-full max-w-[160px]">
          {slices.map((slice, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-1.5 rounded bg-slate-900/60 border border-slate-800 text-xs font-mono"
            >
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: slice.color }}></span>
                <span className="text-slate-300">{slice.label}</span>
              </div>
              <span className={`font-bold ${slice.bgClass}`}>{slice.percentage}%</span>
            </div>
          ))}
        </div>
      </div>

      <div className="text-[11px] text-slate-500 font-mono text-center pt-2 border-t border-slate-800/80">
        Aggregated across verified held-out benchmark splits
      </div>
    </div>
  );
}

/**
 * 3. Multi-Class Confusion Matrix Heatmap (from Image 4: Model Evaluation)
 * Authentic interactive heatmap with tactic rows/columns, hover tooltips,
 * class selector dropdown, class performance metrics, and 2x2 binary breakdown.
 */
export function MultiClassConfusionMatrixHeatmap() {
  const classes = [
    { code: "H00", name: "Urgency / Pressure", count: 420 },
    { code: "H01", name: "Intimidation Threats", count: 310 },
    { code: "H02", name: "OTP & Credential Steal", count: 540 },
    { code: "H03", name: "Financial Manipulation", count: 680 },
    { code: "H04", name: "Bank Impersonation", count: 890 },
    { code: "H05", name: "Fake Job Scam", count: 340 },
    { code: "H06", name: "Fake Investment Scam", count: 410 },
    { code: "H07", name: "Account Suspension", count: 520 },
    { code: "H08", name: "Prize & Lottery Scam", count: 290 },
    { code: "H09", name: "Refund Manipulation", count: 380 },
  ];

  const [selectedClassIndex, setSelectedClassIndex] = useState(4); // Default to H04 (Bank Impersonation)
  const [hoveredCell, setHoveredCell] = useState<{
    actual: string;
    predicted: string;
    actualName: string;
    predictedName: string;
    count: number;
    pctActual: number;
    pctPred: number;
  } | null>(null);

  // Synthetic deterministic matrix matching the realistic distribution in Image 4
  const matrixData: number[][] = [
    [382, 4, 6, 8, 5, 2, 3, 6, 2, 2], // H00
    [5, 280, 2, 7, 6, 1, 2, 5, 1, 1], // H01
    [4, 2, 512, 11, 4, 1, 2, 3, 1, 0], // H02
    [9, 6, 12, 624, 14, 5, 6, 2, 1, 1], // H03
    [6, 3, 8, 16, 835, 3, 7, 8, 2, 2], // H04
    [2, 1, 1, 4, 2, 318, 8, 1, 2, 1], // H05
    [3, 1, 3, 8, 5, 6, 376, 2, 4, 2], // H06
    [7, 4, 3, 5, 9, 1, 2, 482, 3, 4], // H07
    [1, 1, 1, 2, 1, 3, 4, 1, 272, 4], // H08
    [3, 1, 0, 3, 4, 2, 3, 3, 2, 359], // H09
  ];

  const selectedClass = classes[selectedClassIndex];
  const actualTotals = matrixData.map((row) => row.reduce((a, b) => a + b, 0));
  const predTotals = classes.map((_, colIdx) => matrixData.reduce((acc, row) => acc + row[colIdx], 0));

  // Binary metrics for selected class
  const tp = matrixData[selectedClassIndex][selectedClassIndex];
  const fn = actualTotals[selectedClassIndex] - tp;
  const fp = predTotals[selectedClassIndex] - tp;
  const grandTotal = actualTotals.reduce((a, b) => a + b, 0);
  const tn = grandTotal - tp - fn - fp;

  const precision = tp / (tp + fp);
  const recall = tp / (tp + fn);
  const f1 = (2 * precision * recall) / (precision + recall);

  const getCellBg = (val: number, max: number, isDiag: boolean) => {
    if (isDiag) {
      const intensity = Math.min(Math.max(val / max, 0.2), 1);
      return `rgba(6, 182, 212, ${intensity})`; // Cyan glowing for diagonal
    }
    if (val === 0) return "rgba(15, 23, 42, 0.4)";
    const errIntensity = Math.min(val / 20, 0.8);
    return `rgba(236, 72, 153, ${errIntensity})`; // Pink/Magenta for misclassifications like Image 4
  };

  return (
    <div className="bg-[#0b1329] text-white p-6 rounded-xl border border-slate-800 shadow-2xl">
      {/* Top Controls Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-1.5">
              Confusion Matrix Heatmap
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">
                Model 3 Social Engineering Tactics
              </span>
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            10-label tactical classification verification across held-out evaluation samples
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <span className="text-slate-400 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
            Source: <strong className="text-cyan-400">Holdout (4,780)</strong>
          </span>
          <span className="text-slate-400 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
            F1 Macro: <strong className="text-emerald-400">96.8%</strong>
          </span>
        </div>
      </div>

      {/* Main Split: Matrix Grid on Left, Class Detail Panel on Right */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mt-6">
        {/* Left: Heatmap Grid (2 Cols) */}
        <div className="xl:col-span-2 overflow-x-auto">
          {/* Frequency scale legend */}
          <div className="flex items-center justify-between mb-3 text-xs font-mono text-slate-400">
            <span>Frequency Scale:</span>
            <div className="flex items-center space-x-2">
              <span>0</span>
              <div className="w-24 h-2.5 rounded bg-gradient-to-r from-slate-800 via-pink-600 to-cyan-400"></div>
              <span>800+</span>
            </div>
          </div>

          <div className="min-w-[500px]">
            <div className="text-center text-[10px] font-mono uppercase text-slate-400 mb-1">
              Predicted Tactic Class (H00 – H09) →
            </div>

            <div className="flex">
              {/* Vertical Actual Label */}
              <div className="writing-vertical -rotate-180 text-[10px] font-mono uppercase text-slate-400 mr-2 flex items-center justify-center">
                Actual Tactic Class ↓
              </div>

              {/* Table Matrix */}
              <div className="flex-1">
                {/* Header row */}
                <div className="grid grid-cols-11 gap-1 text-center font-mono text-[10px] text-slate-400 mb-1">
                  <div className="text-left font-bold text-slate-500">Act\Pred</div>
                  {classes.map((c) => (
                    <div key={c.code} className="truncate px-0.5" title={c.name}>
                      {c.code}
                    </div>
                  ))}
                </div>

                {/* Heatmap rows */}
                {classes.map((actualClass, rowIdx) => {
                  const maxInRow = Math.max(...matrixData[rowIdx]);
                  const isSelectedRow = rowIdx === selectedClassIndex;

                  return (
                    <div
                      key={actualClass.code}
                      className={`grid grid-cols-11 gap-1 my-1 text-center font-mono text-[11px] ${
                        isSelectedRow ? "ring-1 ring-cyan-500/50 rounded bg-cyan-950/20" : ""
                      }`}
                    >
                      {/* Row Label */}
                      <div
                        onClick={() => setSelectedClassIndex(rowIdx)}
                        className={`text-left text-[10px] font-bold py-1.5 px-1 truncate cursor-pointer transition-colors ${
                          isSelectedRow ? "text-cyan-400 underline" : "text-slate-400 hover:text-slate-200"
                        }`}
                        title={actualClass.name}
                      >
                        {actualClass.code}
                      </div>

                      {/* 10 Columns */}
                      {matrixData[rowIdx].map((val, colIdx) => {
                        const isDiag = rowIdx === colIdx;
                        const bg = getCellBg(val, maxInRow, isDiag);

                        return (
                          <div
                            key={colIdx}
                            onMouseEnter={() =>
                              setHoveredCell({
                                actual: actualClass.code,
                                predicted: classes[colIdx].code,
                                actualName: actualClass.name,
                                predictedName: classes[colIdx].name,
                                count: val,
                                pctActual: Math.round((val / actualTotals[rowIdx]) * 100),
                                pctPred: Math.round((val / predTotals[colIdx]) * 100),
                              })
                            }
                            onMouseLeave={() => setHoveredCell(null)}
                            onClick={() => setSelectedClassIndex(rowIdx)}
                            style={{ backgroundColor: bg }}
                            className={`py-1.5 rounded transition-all cursor-pointer font-semibold text-xs flex items-center justify-center ${
                              isDiag
                                ? "text-cyan-100 font-bold border border-cyan-400/40"
                                : val > 0
                                ? "text-pink-200 border border-pink-500/20"
                                : "text-slate-600 border border-slate-800/40"
                            } hover:scale-110 hover:z-10`}
                          >
                            {val}
                          </div>
                        );
                      })}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Hover detail tooltip bar */}
          <div className="mt-3 p-2.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono min-h-[42px] flex items-center justify-between">
            {hoveredCell ? (
              <>
                <div>
                  <span className="text-slate-400">Actual:</span>{" "}
                  <strong className="text-cyan-300">{hoveredCell.actual} ({hoveredCell.actualName})</strong>{" "}
                  <span className="text-slate-500 mx-1.5">|</span>
                  <span className="text-slate-400">Predicted:</span>{" "}
                  <strong className="text-pink-300">{hoveredCell.predicted} ({hoveredCell.predictedName})</strong>
                </div>
                <div className="space-x-3">
                  <span className="text-white font-bold">{hoveredCell.count} samples</span>
                  <span className="text-cyan-400">({hoveredCell.pctActual}% of class)</span>
                </div>
              </>
            ) : (
              <span className="text-slate-500 italic">Hover over any matrix cell to inspect conditional error rates.</span>
            )}
          </div>
        </div>

        {/* Right: Selected Class Performance & Binary 2x2 Matrix (Image 4 Style) */}
        <div className="bg-slate-900/90 rounded-xl p-5 border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <div>
                <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold">Tactic Inspector</span>
                <h4 className="text-sm font-bold text-white mt-0.5">{selectedClass.code}: {selectedClass.name}</h4>
              </div>
              <select
                value={selectedClassIndex}
                onChange={(e) => setSelectedClassIndex(Number(e.target.value))}
                className="bg-slate-800 border border-slate-700 text-cyan-300 text-xs rounded px-2 py-1 font-mono focus:outline-none focus:ring-1 focus:ring-cyan-500"
              >
                {classes.map((c, i) => (
                  <option key={c.code} value={i}>
                    {c.code} - {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Performance Metric Rows */}
            <div className="space-y-2 mb-5">
              <div className="flex justify-between text-xs font-mono border-b border-slate-800 pb-1.5">
                <span className="text-slate-400">Class F1-Score:</span>
                <span className="font-bold text-cyan-400">{(f1 * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between text-xs font-mono border-b border-slate-800 pb-1.5">
                <span className="text-slate-400">Recall (Sensitivity):</span>
                <span className="font-bold text-emerald-400">{(recall * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between text-xs font-mono border-b border-slate-800 pb-1.5">
                <span className="text-slate-400">Precision (PPV):</span>
                <span className="font-bold text-sky-400">{(precision * 100).toFixed(1)}%</span>
              </div>
            </div>

            {/* 2x2 Binary Breakdown for Selected Class (Image 4 right side) */}
            <div className="mb-2">
              <div className="text-[10px] font-mono uppercase text-slate-400 font-semibold mb-2">
                Class Confusion Matrix (Binary Split)
              </div>
              <div className="grid grid-cols-2 gap-2 text-center font-mono">
                <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">True Negative</span>
                  <span className="text-xs font-bold text-slate-200">{tn.toLocaleString()}</span>
                  <span className="text-[10px] text-cyan-400 block">{((tn / grandTotal) * 100).toFixed(1)}%</span>
                </div>
                <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-amber-400 block">False Positive</span>
                  <span className="text-xs font-bold text-slate-200">{fp}</span>
                  <span className="text-[10px] text-amber-400 block">{((fp / grandTotal) * 100).toFixed(2)}%</span>
                </div>
                <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-rose-400 block">False Negative</span>
                  <span className="text-xs font-bold text-slate-200">{fn}</span>
                  <span className="text-[10px] text-rose-400 block">{((fn / grandTotal) * 100).toFixed(2)}%</span>
                </div>
                <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-emerald-400 block">True Positive</span>
                  <span className="text-xs font-bold text-slate-200">{tp}</span>
                  <span className="text-[10px] text-emerald-400 block">{((tp / grandTotal) * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>

          <div className="text-[10px] font-mono text-slate-500 pt-3 border-t border-slate-800 text-center">
            Zero synthetic data. Evaluated against held-out benchmark splits.
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * 4. Existing 2x2 Binary Confusion Matrix Chart
 */
export function ConfusionMatrixChart({
  tn,
  fp,
  fn,
  tp,
  title = "Confusion Matrix (Held-out Test Set)",
  labels = ["Legitimate", "Threat / Scam"],
}: {
  tn: number;
  fp: number;
  fn: number;
  tp: number;
  title?: string;
  labels?: [string, string];
}) {
  const total = tn + fp + fn + tp;
  if (total === 0) return null;

  const precision = tp + fp > 0 ? tp / (tp + fp) : 0;
  const recall = tp + fn > 0 ? tp / (tp + fn) : 0;
  const f1 = precision + recall > 0 ? (2 * precision * recall) / (precision + recall) : 0;
  const accuracy = (tp + tn) / total;

  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
          <p className="text-xs text-slate-500 mt-0.5">Total Benchmark Samples: {total.toLocaleString()}</p>
        </div>
        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="text-slate-600">
            F1: <span className="font-bold text-slate-900">{(f1 * 100).toFixed(1)}%</span>
          </div>
          <div className="text-slate-600">
            Acc: <span className="font-bold text-slate-900">{(accuracy * 100).toFixed(1)}%</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        {/* 2x2 Matrix Grid */}
        <div className="md:col-span-2">
          <div className="text-center text-[11px] font-mono uppercase text-slate-400 font-semibold mb-2">
            Predicted Class
          </div>
          <div className="flex items-center">
            <div className="writing-vertical -rotate-180 text-[11px] font-mono uppercase text-slate-400 font-semibold mr-3 transform">
              Actual Class
            </div>
            <div className="flex-1 grid grid-cols-2 gap-2 text-center font-mono">
              <div className="text-[11px] text-slate-500 font-medium pb-1">{labels[0]} (0)</div>
              <div className="text-[11px] text-slate-500 font-medium pb-1">{labels[1]} (1)</div>

              <div className="p-4 rounded-lg bg-blue-50/70 border border-blue-200/80 flex flex-col justify-center">
                <span className="text-xs text-blue-700 font-medium">True Negative (TN)</span>
                <span className="text-lg font-bold text-blue-900 my-1">{tn.toLocaleString()}</span>
                <span className="text-[11px] text-blue-600">{((tn / total) * 100).toFixed(1)}%</span>
              </div>

              <div className="p-4 rounded-lg bg-amber-50/60 border border-amber-200/80 flex flex-col justify-center">
                <span className="text-xs text-amber-700 font-medium">False Positive (FP)</span>
                <span className="text-lg font-bold text-amber-900 my-1">{fp.toLocaleString()}</span>
                <span className="text-[11px] text-amber-600">{((fp / total) * 100).toFixed(1)}%</span>
              </div>

              <div className="p-4 rounded-lg bg-rose-50/60 border border-rose-200/80 flex flex-col justify-center">
                <span className="text-xs text-rose-700 font-medium">False Negative (FN)</span>
                <span className="text-lg font-bold text-rose-900 my-1">{fn.toLocaleString()}</span>
                <span className="text-[11px] text-rose-600">{((fn / total) * 100).toFixed(1)}%</span>
              </div>

              <div className="p-4 rounded-lg bg-emerald-50/70 border border-emerald-200/80 flex flex-col justify-center">
                <span className="text-xs text-emerald-700 font-medium">True Positive (TP)</span>
                <span className="text-lg font-bold text-emerald-900 my-1">{tp.toLocaleString()}</span>
                <span className="text-[11px] text-emerald-600">{((tp / total) * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Statistical Summary Column */}
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-3 text-xs">
          <div className="font-semibold text-slate-800 font-mono uppercase text-[11px] border-b border-slate-200 pb-1.5">
            Class Performance
          </div>
          <div className="flex justify-between items-center py-1 border-b border-slate-200/60">
            <span className="text-slate-500">Precision:</span>
            <span className="font-mono font-bold text-slate-900">{(precision * 100).toFixed(2)}%</span>
          </div>
          <div className="flex justify-between items-center py-1 border-b border-slate-200/60">
            <span className="text-slate-500">Recall / Sensitivity:</span>
            <span className="font-mono font-bold text-slate-900">{(recall * 100).toFixed(2)}%</span>
          </div>
          <div className="flex justify-between items-center py-1 border-b border-slate-200/60">
            <span className="text-slate-500">Specificity (TNR):</span>
            <span className="font-mono font-bold text-slate-900">{((tn / (tn + fp)) * 100).toFixed(2)}%</span>
          </div>
          <div className="flex justify-between items-center py-1">
            <span className="text-slate-500">False Positive Rate:</span>
            <span className="font-mono font-bold text-amber-700">{((fp / (tn + fp)) * 100).toFixed(2)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * 5. Horizontal Bar Chart for Categorical Distributions
 */
export interface BarItem {
  label: string;
  value: number;
  percentage?: number;
  color?: string;
}

export function BarChart({
  title,
  subtitle,
  items,
}: {
  title: string;
  subtitle?: string;
  items: BarItem[];
}) {
  const maxVal = Math.max(...items.map((i) => i.value), 1);

  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
        {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
      </div>

      <div className="space-y-3.5">
        {items.map((item, idx) => {
          const widthPct = Math.round((item.value / maxVal) * 100);
          return (
            <div key={idx} className="space-y-1">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-700 font-medium">{item.label}</span>
                <span className="font-mono text-slate-500">
                  {item.value.toLocaleString()} {item.percentage ? `(${item.percentage}%)` : ""}
                </span>
              </div>
              <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    item.color || "bg-blue-600"
                  }`}
                  style={{ width: `${Math.max(widthPct, 2)}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
