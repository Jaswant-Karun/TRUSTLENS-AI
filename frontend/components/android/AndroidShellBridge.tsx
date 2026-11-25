"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Capacitor } from "@capacitor/core";
import { App as CapApp } from "@capacitor/app";
import { Network } from "@capacitor/network";
import { StatusBar, Style } from "@capacitor/status-bar";
import { SplashScreen } from "@capacitor/splash-screen";
import {
  FileWarning,
  FolderSearch,
  Globe,
  Image as ImageIcon,
  MessageSquareWarning,
  User,
  WifiOff,
} from "lucide-react";
import { initAuthStorage } from "@/lib/api";
import {
  parseDeepLinkToRoute,
  SharedPayload,
  TrustLensShareIntent,
} from "@/lib/androidCapabilities";

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
  const [isOffline, setIsOffline] = useState(false);
  const [exitHintVisible, setExitHintVisible] = useState(false);
  const lastBackPressRef = useRef<number>(0);

  const handleIncomingShare = React.useCallback(
    (payload: SharedPayload) => {
      if (!payload?.kind) return;
      if (payload.kind === "text" && payload.text) {
        const trimmed = payload.text.trim();
        if (/^https?:\/\/\S+$/i.test(trimmed)) {
          sessionStorage.setItem("trustlens_shared_url", trimmed);
          router.push("/analyze/url");
        } else {
          sessionStorage.setItem("trustlens_shared_text", trimmed);
          router.push("/analyze/text");
        }
      } else if (payload.kind === "image" && payload.base64) {
        sessionStorage.setItem(
          "trustlens_shared_image",
          JSON.stringify({
            base64: payload.base64,
            mimeType: payload.mimeType || "image/jpeg",
          })
        );
        router.push("/analyze/image");
      }
    },
    [router]
  );

  // Hydrate Keystore-backed auth token, network status, deep links, and share intents
  useEffect(() => {
    let mounted = true;
    initAuthStorage().finally(() => {
      if (mounted) onAuthHydrated?.();
    });

    // Network connectivity monitoring (works on both native Android and Web)
    let netHandle: { remove: () => Promise<void> } | null = null;
    if (Capacitor.isNativePlatform()) {
      Network.getStatus()
        .then((s) => {
          if (mounted) setIsOffline(!s.connected);
        })
        .catch(() => {});
      Network.addListener("networkStatusChange", (s) => {
        if (mounted) setIsOffline(!s.connected);
      })
        .then((h) => {
          netHandle = h;
        })
        .catch(() => {});
    } else if (typeof window !== "undefined") {
      setIsOffline(!window.navigator.onLine);
      const goOnline = () => setIsOffline(false);
      const goOffline = () => setIsOffline(true);
      window.addEventListener("online", goOnline);
      window.addEventListener("offline", goOffline);
    }

    let urlHandle: { remove: () => Promise<void> } | null = null;
    let shareHandle: { remove: () => Promise<void> } | null = null;

    if (Capacitor.isNativePlatform()) {
      setIsNative(true);
      StatusBar.setStyle({ style: Style.Dark }).catch(() => {});
      StatusBar.setBackgroundColor({ color: "#050306" }).catch(() => {});
      SplashScreen.hide().catch(() => {});

      // Deep links (trustlens://analyze/url, https://trustlens.ai/investigations, etc.)
      CapApp.addListener("appUrlOpen", ({ url }) => {
        const target = parseDeepLinkToRoute(url);
        if (target) router.push(target);
      })
        .then((h) => {
          urlHandle = h;
        })
        .catch(() => {});

      // Inbound Android Share-Sheet (ACTION_SEND)
      TrustLensShareIntent.getPendingShare()
        .then((p) => handleIncomingShare(p))
        .catch(() => {});
      TrustLensShareIntent.addListener("shareReceived", (p) => {
        handleIncomingShare(p);
      })
        .then((h) => {
          shareHandle = h;
        })
        .catch(() => {});
    }

    return () => {
      mounted = false;
      if (netHandle) void netHandle.remove();
      if (urlHandle) void urlHandle.remove();
      if (shareHandle) void shareHandle.remove();
    };
  }, [onAuthHydrated, router, handleIncomingShare]);

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
      {isOffline && (
        <div
          role="alert"
          className="fixed top-0 left-0 right-0 z-50 flex items-center justify-center gap-2 border-b border-[#FF174F]/60 bg-[#2B0610]/95 px-3 py-1.5 font-mono text-[11px] text-[#FF85A1]"
        >
          <WifiOff className="h-3.5 w-3.5 shrink-0" />
          <span>Offline mode — connect to the internet to run scans or sync intelligence.</span>
        </div>
      )}

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
