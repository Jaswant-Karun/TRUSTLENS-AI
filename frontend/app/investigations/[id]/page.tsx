"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { InvestigationWorkspace } from "@/components/investigation/InvestigationWorkspace";
import { illustrativeInvestigationFixture } from "@/components/investigation/mockData";
import { InvestigationData } from "@/components/investigation/types";
import { getCampaignDetail } from "@/lib/api";

export default function InvestigationDetailPage() {
  const params = useParams();
  const id = (params?.id as string) || "INV-2026-KYC-11";

  const [investigation, setInvestigation] = useState<InvestigationData>(illustrativeInvestigationFixture);
  const [loading, setLoading] = useState(false);

  // If the ID corresponds to a real campaign number (e.g. "11", "13", "24")
  useEffect(() => {
    const numericId = parseInt(id.replace(/\D/g, ""), 10);
    if (!isNaN(numericId) && numericId > 0 && numericId <= 47) {
      setLoading(true);
      getCampaignDetail(numericId)
        .then((detail) => {
          if (detail && detail.cluster_size) {
            // Adapt real backend campaign dossier into Investigation graph
            const clusterNodeId = `node-camp-${detail.campaign_id}`;
            const adapted: InvestigationData = {
              ...illustrativeInvestigationFixture,
              id: `INV-CAMP-${detail.campaign_id}`,
              title: `Dossier: ${detail.targeted_entity || "Syndicate"} (#${detail.campaign_id})`,
              description: `Observed cluster size of ${detail.cluster_size} messages with cohesion score of ${(detail.cohesion_score * 100).toFixed(1)}%. ${detail.legal_disclaimer}`,
              objectsCount: detail.cluster_size,
              attributes: {
                "Target Entity": detail.targeted_entity || "Unspecified",
                "Cluster Size": `${detail.cluster_size} messages`,
                "Cohesion Score": `${(detail.cohesion_score * 100).toFixed(1)}%`,
                "Primary Tactic": detail.primary_tactic || "Phishing Pretext",
              },
            };
            setInvestigation(adapted);
          }
        })
        .catch(() => {
          // Fall back gracefully to the illustrative preview fixture
        })
        .finally(() => setLoading(false));
    }
  }, [id]);

  return <InvestigationWorkspace investigation={investigation} />;
}
