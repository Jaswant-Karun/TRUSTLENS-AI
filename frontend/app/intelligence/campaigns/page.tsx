"use client";

import React from "react";
import { PageHeader } from "@/components/ui";
import KillChainGraph from "@/components/KillChainGraph";

export default function CampaignIntelligencePage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Scam Campaign Discovery & Attribution Hub"
        description="Unsupervised HDBSCAN density clustering on multilingual sentence embeddings connecting isolated deceptive communications into coordinated clusters."
        badge={{ text: "Model 4: 47 Active Clusters", variant: "amber" }}
      />

      {/* Constellation Network Graph & Campaign Dossier Flow */}
      <KillChainGraph id="campaign-intelligence" />
    </div>
  );
}
