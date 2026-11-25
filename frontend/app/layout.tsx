import type { Metadata } from "next";
import { ToastProvider } from "@/components/ui/Toast";
import { AppShell } from "@/components/AppShell";
import "./globals.css";

export const metadata: Metadata = {
  applicationName: "TRUSTLENS AI",
  title: "TRUSTLENS AI — Multilingual Digital Fraud Intelligence Platform",
  description:
    "Detect suspicious messages, malicious URLs and emerging digital fraud campaigns using intelligent multilingual analysis and real-world threat intelligence.",
  icons: {
    icon: "/icon.svg",
    apple: "/apple-icon.svg",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#050306] text-white antialiased min-h-screen">
        <ToastProvider>
          <AppShell>{children}</AppShell>
        </ToastProvider>
      </body>
    </html>
  );
}
