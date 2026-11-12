import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TRUSTLENS AI — Digital Fraud Intelligence Platform",
  description: "Advanced Multilingual Digital Fraud Intelligence & Prevention Platform. Detect the deception before people lose their money.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-slate-200 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
