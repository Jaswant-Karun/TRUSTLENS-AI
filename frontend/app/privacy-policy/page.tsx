"use client";

import React, { useEffect, useState } from "react";
import { Lock, ShieldCheck, Trash2, Mail } from "lucide-react";
import { apiFetch } from "@/lib/api";

export default function PrivacyPolicyPage() {
  const [policy, setPolicy] = useState<any>(null);

  useEffect(() => {
    apiFetch<any>("/privacy/policy").then(setPolicy).catch(() => null);
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <div className="space-y-2 border-b border-[#481326] pb-4">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Lock className="w-6 h-6 text-[#FF3D70]" />
          TRUSTLENS AI Privacy Policy
        </h1>
        <p className="text-xs font-mono text-[#A1A1AA]">
          Effective Version: {policy?.version || "2026.1"} • Applicable Frameworks: India DPDP Act &amp; GDPR (where applicable)
        </p>
      </div>

      <section className="cyber-panel p-5 space-y-2 text-xs text-slate-300 leading-relaxed">
        <h2 className="font-mono text-sm font-bold uppercase text-white flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-[#00D68F]" />
          1. Data Collection &amp; Purpose Limitation
        </h2>
        <p>
          TRUSTLENS AI collects only the data strictly required to authenticate your account and analyze suspicious messages, URLs, or screenshots you explicitly submit. We never access SMS inboxes, call logs, contacts, or background camera feeds.
        </p>
        <ul className="list-disc pl-5 space-y-1 text-[#A1A1AA]">
          <li><strong>Account Data:</strong> Email address, full name, and hashed credentials for authenticated access.</li>
          <li><strong>Submitted Content:</strong> Suspicious text, URLs, or screenshots you choose to scan or share into the app.</li>
          <li><strong>Device Push Token (Optional):</strong> Stored only if you explicitly enable Android push notifications.</li>
        </ul>
      </section>

      <section className="cyber-panel p-5 space-y-2 text-xs text-slate-300 leading-relaxed">
        <h2 className="font-mono text-sm font-bold uppercase text-white">
          2. Security, Encryption &amp; Sensitive Redaction
        </h2>
        <p>
          All API traffic is encrypted in transit via HTTPS/TLS (cleartext HTTP is disabled in release builds). On Android, authentication tokens are stored in hardware-backed Android Keystore (<code>EncryptedSharedPreferences</code>), never in plaintext <code>localStorage</code>. Sensitive personal identifiers are redacted before logging or community intelligence export.
        </p>
      </section>

      <section className="cyber-panel p-5 space-y-2 text-xs text-slate-300 leading-relaxed">
        <h2 className="font-mono text-sm font-bold uppercase text-white flex items-center gap-2">
          <Trash2 className="w-4 h-4 text-[#FF3D70]" />
          3. Retention, Export &amp; Deletion Rights
        </h2>
        <p>
          You may export your personal data, delete individual scan records from History, or permanently delete your account and associated records directly inside the app or via <code>/api/v1/privacy</code> endpoints.
        </p>
      </section>

      <section className="cyber-panel p-5 space-y-2 text-xs text-slate-300 leading-relaxed">
        <h2 className="font-mono text-sm font-bold uppercase text-white flex items-center gap-2">
          <Mail className="w-4 h-4 text-[#FF3D70]" />
          4. Privacy &amp; Security Contact
        </h2>
        <p>
          For privacy requests, data deletion inquiries, or vulnerability disclosures, contact{" "}
          <a href="mailto:security@trustlens.ai" className="text-[#FF3D70] underline">
            security@trustlens.ai
          </a>.
        </p>
      </section>
    </div>
  );
}
