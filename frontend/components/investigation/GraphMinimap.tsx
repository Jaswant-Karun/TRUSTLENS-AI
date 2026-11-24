"use client";

import React from "react";
import { GraphNode } from "./types";

interface GraphMinimapProps {
  nodes: GraphNode[];
  viewState: {
    x: number;
    y: number;
    zoom: number;
    bounds: { minX: number; maxX: number; minY: number; maxY: number };
  };
  onClose: () => void;
}

export function GraphMinimap({ nodes, viewState, onClose }: GraphMinimapProps) {
  const { bounds, x, y, zoom } = viewState;

  const width = 140;
  const height = 90;

  const spanX = Math.max(bounds.maxX - bounds.minX, 600);
  const spanY = Math.max(bounds.maxY - bounds.minY, 400);

  // Map world coordinate to minimap coordinate
  const toMinimapX = (worldX: number) => ((worldX - bounds.minX) / spanX) * width;
  const toMinimapY = (worldY: number) => ((worldY - bounds.minY) / spanY) * height;

  // Viewport box in world coordinates:
  // Visible region: canvasWidth / zoom by canvasHeight / zoom
  const vpWidthWorld = 1200 / zoom;
  const vpHeightWorld = 800 / zoom;
  const vpLeftWorld = -x / zoom;
  const vpTopWorld = -y / zoom;

  const vpX = Math.max(0, toMinimapX(vpLeftWorld));
  const vpY = Math.max(0, toMinimapY(vpTopWorld));
  const vpW = Math.min(width, (vpWidthWorld / spanX) * width);
  const vpH = Math.min(height, (vpHeightWorld / spanY) * height);

  return (
    <div className="absolute top-14 left-4 z-30 w-[142px] h-[92px] bg-[#1E2631]/95 backdrop-blur-md border border-[#3A4553] rounded-md shadow-2xl overflow-hidden select-none">
      <svg className="w-full h-full block">
        {/* Node dots */}
        {nodes.map((node) => {
          const mx = toMinimapX(node.x);
          const my = toMinimapY(node.y);
          const color = node.isCentral ? "#EF4444" : "#38BDF8";
          return (
            <circle
              key={node.id}
              cx={mx}
              cy={my}
              r={node.isCentral ? 3 : 1.5}
              fill={color}
              opacity={0.85}
            />
          );
        })}

        {/* Viewport Camera Rectangle */}
        <rect
          x={vpX}
          y={vpY}
          width={Math.max(vpW, 12)}
          height={Math.max(vpH, 8)}
          fill="rgba(56, 189, 248, 0.15)"
          stroke="#38BDF8"
          strokeWidth="1"
          strokeDasharray="2,2"
        />
      </svg>
      {/* Title */}
      <div className="absolute bottom-1 right-1.5 text-[8px] font-mono text-slate-400 uppercase tracking-widest pointer-events-none">
        Radar
      </div>
    </div>
  );
}
