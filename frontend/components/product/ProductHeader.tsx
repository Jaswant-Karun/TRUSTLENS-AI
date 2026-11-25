"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LogOut, ShieldCheck, User as UserIcon } from "lucide-react";
import {
  getCurrentUser,
  getStoredToken,
  logoutUser,
  UserProfile,
} from "@/lib/api";
import { RadialNavigation } from "./RadialNavigation";
import { GlowButton } from "./GlowButton";

export function ProductHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [checkedAuth, setCheckedAuth] = useState(false);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setUser(null);
      setCheckedAuth(true);
      return;
    }
    getCurrentUser()
      .then((profile) => setUser(profile))
      .catch(() => setUser(null))
      .finally(() => setCheckedAuth(true));
  }, [pathname]);

  const handleLogout = () => {
    logoutUser();
    setUser(null);
    router.push("/");
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#481326]/70 bg-[#050306]/85 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Left: Compact Radial Navigation Launcher */}
        <div className="flex items-center gap-3">
          <RadialNavigation variant="launcher" />
          <span className="hidden sm:inline-block font-mono text-[11px] uppercase tracking-[0.18em] text-[#A1A1AA]">
            NAV WHEEL
          </span>
        </div>

        {/* Center: Futuristic TRUSTLENS AI Brand Wordmark */}
        <Link
          href="/"
          className="group flex items-center gap-2.5 focus-visible:outline-none"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-md border border-[#FF174F]/70 bg-[#170A12] shadow-[0_0_14px_rgba(255,23,79,0.28)] group-hover:shadow-[0_0_20px_rgba(255,23,79,0.5)] transition-shadow">
            <ShieldCheck className="h-4 w-4 text-[#FF3D70]" />
          </span>
          <span className="font-mono text-sm sm:text-base font-bold tracking-[0.26em] text-white">
            TRUST<span className="text-[#FF174F]">LENS</span> AI
          </span>
        </Link>

        {/* Right: Auth State / Profile / Sign In / Logout */}
        <div className="flex items-center gap-2.5">
          {!checkedAuth ? (
            <div className="h-9 w-24 rounded-lg bg-[#10070D] border border-[#481326] animate-pulse" />
          ) : user ? (
            <>
              <Link
                href="/profile"
                className="hidden sm:inline-flex items-center gap-2 rounded-lg border border-[#481326] bg-[#10070D] px-3 py-1.5 text-xs font-mono text-white hover:border-[#FF174F] transition-colors"
              >
                <UserIcon className="h-3.5 w-3.5 text-[#FF3D70]" />
                <span className="max-w-[130px] truncate">{user.full_name || user.email}</span>
                <span className="rounded bg-[#FF174F]/20 px-1.5 py-0.5 text-[10px] uppercase text-[#FF3D70]">
                  {user.role}
                </span>
              </Link>
              <GlowButton
                variant="secondary"
                size="sm"
                onClick={handleLogout}
                aria-label="Log out"
              >
                <LogOut className="h-3.5 w-3.5" />
                <span className="hidden xs:inline">LOGOUT</span>
              </GlowButton>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="inline-flex items-center justify-center rounded-lg border border-[#481326] bg-[#10070D] px-3.5 py-2 text-xs font-mono font-semibold uppercase tracking-wider text-white hover:border-[#FF174F] transition-colors min-h-[38px]"
              >
                SIGN IN
              </Link>
              <Link
                href="/register"
                className="hidden sm:inline-flex items-center justify-center rounded-lg bg-gradient-to-r from-[#FF174F] to-[#C2185B] px-4 py-2 text-xs font-mono font-semibold uppercase tracking-wider text-white border border-[#FF3D70]/60 shadow-[0_0_16px_rgba(255,23,79,0.3)] hover:brightness-110 transition-all min-h-[38px]"
              >
                GET STARTED
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
