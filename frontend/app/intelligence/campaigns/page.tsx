"use client";

import React from "react";
import { PageHeader, MetricCard } from "@/components/ui";
import KillChainGraph from "@/components/KillChainGraph";
import { Network, Layers, ShieldAlert, Cpu } from "lucide-react";

export default function CampaignIntelligencePage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Scam Campaign Discovery & Attribution Hub"
        description="Unsupervised HDBSCAN density clustering on multilingual sentence embeddings connecting isolated deceptive communications into coordinated clusters."
        badge={{ text: "Model 4: 47 Active Clusters", variant: "amber" }}
      />

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Discovered Clusters"
          value={47}
          subtitle="HDBSCAN density groups"
          icon={Network}
          accentColor="blue"
        />
        <MetricCard
          title="Peak Cluster Size"
          value={254}
          subtitle="Messages in largest group"
          icon={Layers}
          accentColor="rose"
        />
        <MetricCard
          title="Max Cohesion Score"
          value="88.4%"
          subtitle="Embedding proximity index"
          icon={ShieldAlert}
          accentColor="emerald"
        />
        <MetricCard
          title="Clustering Engine"
          value="Online"
          subtitle="Zero-shot semantic grouping"
          icon={Cpu}
          accentColor="cyan"
        />
      </div>

      {/* Constellation Network Graph & Campaign Dossier Flow */}
      <KillChainGraph id="campaign-intelligence" />
    </div>
  );
}
