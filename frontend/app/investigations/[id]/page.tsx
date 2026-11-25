import InvestigationDetailClient from "./InvestigationDetailClient";

export function generateStaticParams() {
  return [{ id: "INV-2026-0011" }];
}

export default function InvestigationDetailPage() {
  return <InvestigationDetailClient />;
}
