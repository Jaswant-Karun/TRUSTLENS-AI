import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "TRUSTLENS AI — Multilingual Digital Fraud Intelligence",
    short_name: "TRUSTLENS AI",
    description:
      "Detect suspicious messages, malicious URLs and emerging digital fraud campaigns using multilingual ML analysis.",
    start_url: "/",
    display: "standalone",
    background_color: "#050306",
    theme_color: "#050306",
    icons: [
      {
        src: "/icon.svg",
        sizes: "any",
        type: "image/svg+xml",
      },
    ],
  };
}
