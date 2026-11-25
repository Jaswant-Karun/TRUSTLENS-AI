"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  CheckCircle2,
  FolderSearch,
  History,
  LogOut,
  Shield,
  User as UserIcon,
} from "lucide-react";
import {
  getCurrentUser,
  getStoredToken,
  logoutUser,
  UserProfile,
} from "@/lib/api";
import { NeonFrame } from "@/components/product/NeonFrame";
import { GlowButton } from "@/components/product/GlowButton";

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setLoading(false);
      return;
    }
    getCurrentUser()
      .then((u) => setUser(u))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const handleLogout = () => {
    logoutUser();
    router.push("/");
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12 font-mono text-xs text-[#A1A1AA]">
        Loading profile...
      </div>
    );
  }

  if (!user) {
    return (
      <div className="mx-auto flex max-w-md flex-1 items-center justify-center px-4 py-12">
        <NeonFrame className="w-full p-6 sm:p-8 text-center">
          <UserIcon className="mx-auto mb-3 h-10 w-10 text-[#FF3D70]" />
          <h1 className="font-mono text-lg font-bold uppercase tracking-wider text-white">
            Authentication Required
          </h1>
          <p className="mt-2 text-xs text-[#A1A1AA]">
            Sign in to view your TRUSTLENS AI profile, role permissions, and
            saved investigations.
          </p>
          <div className="mt-6 flex gap-3 justify-center">
            <Link href="/login?next=/profile">
              <GlowButton variant="primary">SIGN IN</GlowButton>
            </Link>
            <Link href="/register">
              <GlowButton variant="secondary">SIGN UP</GlowButton>
            </Link>
          </div>
        </NeonFrame>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-8 sm:px-6">
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {/* Identity Card (Inspired by Reference Profile Card) */}
        <NeonFrame className="p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-3.5">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-[#FF174F] to-[#C2185B] font-mono text-lg font-bold text-white shadow-[0_0_16px_rgba(255,23,79,0.4)]">
                {(user.full_name || user.email || "U")[0].toUpperCase()}
              </div>
              <div className="min-w-0">
                <h1 className="truncate font-mono text-sm font-bold uppercase tracking-wider text-white">
                  {user.full_name || "TRUSTLENS USER"}
                </h1>
                <p className="truncate text-xs text-[#A1A1AA]">{user.email}</p>
              </div>
            </div>

            <div className="mt-4 inline-flex items-center gap-1.5 rounded-full border border-[#00D68F]/40 bg-[#00D68F]/10 px-2.5 py-1 text-[11px] font-mono text-[#00D68F]">
              <CheckCircle2 className="h-3.5 w-3.5" />
              <span>ACTIVE SESSION</span>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-[#481326]">
            <GlowButton variant="secondary" size="sm" className="w-full" onClick={handleLogout}>
              <LogOut className="h-3.5 w-3.5" />
              SIGN OUT
            </GlowButton>
          </div>
        </NeonFrame>

        {/* Profile Details */}
        <NeonFrame className="p-6 md:col-span-2">
          <div className="flex items-center justify-between border-b border-[#481326] pb-3">
            <h2 className="font-mono text-xs font-bold uppercase tracking-widest text-white">
              Account & Security Details
            </h2>
            <span className="inline-flex items-center gap-1 rounded bg-[#FF174F]/15 px-2 py-0.5 font-mono text-[10px] uppercase text-[#FF3D70]">
              <Shield className="h-3 w-3" />
              {user.role}
            </span>
          </div>

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="rounded-lg border border-[#481326]/70 bg-[#050306]/70 p-3.5">
              <div className="font-mono text-[10px] uppercase tracking-wider text-[#A1A1AA]">
                User ID
              </div>
              <div className="mt-1 truncate font-mono text-xs text-white">
                {user.user_id}
              </div>
            </div>
            <div className="rounded-lg border border-[#481326]/70 bg-[#050306]/70 p-3.5">
              <div className="font-mono text-[10px] uppercase tracking-wider text-[#A1A1AA]">
                Role & Access
              </div>
              <div className="mt-1 font-mono text-xs uppercase text-white">
                {user.role}
              </div>
            </div>
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/history">
              <GlowButton variant="secondary" size="sm">
                <History className="h-3.5 w-3.5" />
                SCAN HISTORY
              </GlowButton>
            </Link>
            <Link href="/investigations">
              <GlowButton variant="secondary" size="sm">
                <FolderSearch className="h-3.5 w-3.5" />
                INVESTIGATIONS
              </GlowButton>
            </Link>
            <Link href="/settings">
              <GlowButton variant="ghost" size="sm">
                SETTINGS
              </GlowButton>
            </Link>
          </div>
        </NeonFrame>
      </div>
    </div>
  );
}
