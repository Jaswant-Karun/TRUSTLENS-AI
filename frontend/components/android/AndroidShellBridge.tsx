"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Capacitor } from "@capacitor/core";
import { App as CapApp } from "@capacitor/app";
import { StatusBar, Style } from "@capacitor/status-bar";
import { SplashScreen } from "@capacitor/splash-screen";
import {
  FileWarning,
  FolderSearch,
  Globe,
  Image as ImageIcon,
  MessageSquareWarning,
  User,
} from "lucide-react";
import { initAuthStorage } from "@/lib/api";

const ROOT_EXIT_ROUTES = new Set(["/", "/dashboard", "/analyze/text", "/login"]);

const MOBILE_TABS = [
  { href: "/analyze/text", label: "Text", icon: MessageSquareWarning },
  { href: "/analyze/url", label: "URL", icon: Globe },
  { href: "/analyze/image", label: "Image", icon: ImageIcon },
  { href: "/investigations", label: "Cases", icon: FolderSearch },
  { href: "/reports", label: "Reports", icon: FileWarning },
  { href: "/profile", label: "Profile", icon: User },
];

interface AndroidShellBridgeProps {
  onAuthHydrated?: () => void;
}

export function AndroidShellBridge({ onAuthHydrated }: AndroidShellBridgeProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [isNative, setIsNative] = useState(false);
  const [exitHintVisible, setExitHintVisible] = useState(false);
  const lastBackPressRef = useRef<number>(0);

  // Hydrate Keystore-backed auth token and configure native status bar / splash screen
  useEffect(() => {
    let mounted = true;
    initAuthStorage().finally(() => {
      if (mounted) onAuthHydrated?.();
    });

    if (Capacitor.isNativePlatform()) {
      setIsNative(true);
      StatusBar.setStyle({ style: Style.Dark }).catch(() => {});
      StatusBar.setBackgroundColor({ color: "#050306" }).catch(() => {});
      SplashScreen.hide().catch(() => {});
    }

    return () => {
      mounted = false;
    };
  }, [onAuthHydrated]);

  // Handle Android hardware / gesture back button properly
  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;

    let listenerHandle: { remove: () => Promise<void> } | null = null;

    CapApp.addListener("backButton", ({ canGoBack }) => {
      const normalizedPath = pathname.replace(/\/+$/, "") || "/";
      if (!ROOT_EXIT_ROUTES.has(normalizedPath)) {
        if (canGoBack && window.history.length > 1) {
          router.back();
        } else {
          router.push("/analyze/text");
        }
        return;
      }

      const now = Date.now();
      if (now - lastBackPressRef.current < 2000) {
        CapApp.exitApp();
      } else {
        lastBackPressRef.current = now;
        setExitHintVisible(true);
        setTimeout(() => setExitHintVisible(false), 2000);
      }
    }).then((handle) => {
      listenerHandle = handle;
    });

    return () => {
      if (listenerHandle) {
        void listenerHandle.remove();
      }
    };
  }, [pathname, router]);

  return (
    <>
      {exitHintVisible && (
        <div
          role="status"
          className="fixed bottom-20 left-1/2 z-50 -translate-x-1/2 rounded-full border border-[#FF174F]/60 bg-[#10070D]/95 px-4 py-2 font-mono text-xs text-white shadow-[0_0_20px_rgba(255,23,79,0.35)]"
        >
          Press back again to exit TRUSTLENS AI
        </div>
      )}

      {/* Native-style bottom tab navigation on Android & mobile viewports */}
      <nav
        aria-label="Mobile primary navigation"
        className={`${
          isNative ? "flex" : "flex md:hidden"
        } fixed bottom-0 left-0 right-0 z-40 items-center justify-around border-t border-[#481326] bg-[#050306]/95 px-1 py-2 backdrop-blur-md`}
      >
        {MOBILE_TABS.map((tab) => {
          const Icon = tab.icon;
          const active =
            pathname === tab.href ||
            (tab.href !== "/" && pathname.startsWith(tab.href));
          return (
            <Link
              key={tab.href}
              href={tab.href}
              aria-current={active ? "page" : undefined}
              className={`flex min-w-[52px] flex-col items-center gap-0.5 rounded-lg px-2 py-1 font-mono text-[10px] transition-colors ${
                active
                  ? "bg-[#FF174F]/15 text-[#FF3D70]"
                  : "text-[#A1A1AA] hover:text-white"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </Link>
          );
        })}
      </nav>
    </>
  );
}
