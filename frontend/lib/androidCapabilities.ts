import { Capacitor, registerPlugin } from "@capacitor/core";
import { Camera } from "@capacitor/camera";
import { PushNotifications } from "@capacitor/push-notifications";
import { Share } from "@capacitor/share";
import { apiFetch } from "./api";

export interface SharedPayload {
  kind?: "text" | "image";
  text?: string;
  mimeType?: string;
  base64?: string;
}

interface ShareIntentPluginInterface {
  getPendingShare(): Promise<SharedPayload>;
  addListener(
    eventName: "shareReceived",
    listenerFunc: (payload: SharedPayload) => void
  ): Promise<{ remove: () => Promise<void> }>;
}

export const TrustLensShareIntent =
  registerPlugin<ShareIntentPluginInterface>("TrustLensShareIntent");

const ALLOWED_DEEP_LINK_PREFIXES = [
  "/analyze/text",
  "/analyze/url",
  "/analyze/image",
  "/investigations",
  "/reports",
  "/profile",
  "/methodology",
  "/dashboard",
];

export function parseDeepLinkToRoute(rawUrl: string): string | null {
  try {
    const parsed = new URL(rawUrl);
    // Support both trustlens://analyze/url and https://trustlens.ai/analyze/url
    let candidatePath = parsed.pathname || "/";
    if (parsed.protocol === "trustlens:") {
      candidatePath = `/${parsed.host}${parsed.pathname}`.replace(/\/+$/, "") || "/";
    }
    const matched = ALLOWED_DEEP_LINK_PREFIXES.some(
      (prefix) => candidatePath === prefix || candidatePath.startsWith(`${prefix}/`)
    );
    if (!matched) return "/analyze/text";
    return `${candidatePath}${parsed.search || ""}`;
  } catch {
    return null;
  }
}

export async function hasMediaPermission(kind: "camera" | "photos"): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) return true;
  const status = await Camera.checkPermissions();
  return kind === "camera"
    ? status.camera === "granted"
    : status.photos === "granted" || status.photos === "limited";
}

export async function requestMediaPermission(kind: "camera" | "photos"): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) return true;
  const status = await Camera.requestPermissions({ permissions: [kind] });
  return kind === "camera"
    ? status.camera === "granted"
    : status.photos === "granted" || status.photos === "limited";
}

export async function registerAndroidPushNotifications(): Promise<{
  granted: boolean;
  message: string;
}> {
  if (!Capacitor.isNativePlatform()) {
    return { granted: false, message: "Push notifications are available on Android builds." };
  }

  let perm = await PushNotifications.checkPermissions();
  if (perm.receive === "prompt" || perm.receive === "prompt-with-rationale") {
    perm = await PushNotifications.requestPermissions();
  }
  if (perm.receive !== "granted") {
    return {
      granted: false,
      message: "Notification permission was denied in Android settings.",
    };
  }

  return new Promise((resolve) => {
    let settled = false;
    const finish = (res: { granted: boolean; message: string }) => {
      if (!settled) {
        settled = true;
        resolve(res);
      }
    };

    PushNotifications.addListener("registration", async (token) => {
      try {
        await apiFetch("/notifications/device-token", {
          method: "POST",
          body: JSON.stringify({ platform: "android", device_token: token.value }),
        });
        finish({ granted: true, message: "Android push notifications enabled." });
      } catch {
        finish({
          granted: true,
          message: "Permission granted; device token will sync once signed in.",
        });
      }
    }).catch(() => {});

    PushNotifications.addListener("registrationError", () => {
      finish({
        granted: true,
        message: "Notification permission granted (FCM awaits google-services.json).",
      });
    }).catch(() => {});

    PushNotifications.register().catch(() => {
      finish({
        granted: true,
        message: "Notification permission granted (FCM awaits google-services.json).",
      });
    });

    setTimeout(() => {
      finish({ granted: true, message: "Notification permission granted." });
    }, 3500);
  });
}

export async function shareSanitizedSummary(options: {
  title: string;
  text: string;
  url?: string;
}): Promise<boolean> {
  if (Capacitor.isNativePlatform()) {
    await Share.share({
      title: options.title,
      text: options.text,
      url: options.url,
      dialogTitle: "Share TRUSTLENS AI Assessment",
    });
    return true;
  }
  if (typeof navigator !== "undefined" && navigator.share) {
    await navigator.share(options);
    return true;
  }
  return false;
}
