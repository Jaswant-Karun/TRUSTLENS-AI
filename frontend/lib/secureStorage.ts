import { Capacitor, registerPlugin } from "@capacitor/core";

interface SecureStoragePluginInterface {
  setToken(options: { key: string; value: string }): Promise<void>;
  getToken(options: { key: string }): Promise<{ value: string | null }>;
  clearToken(options: { key: string }): Promise<void>;
}

const TrustLensSecureStorage = registerPlugin<SecureStoragePluginInterface>(
  "TrustLensSecureStorage"
);

const TOKEN_KEY = "trustlens_token";

// In-memory cache so synchronous getStoredToken() works without storing secrets in WebView localStorage.
let memoryToken: string | null = null;
let initialized = false;

export function isNativeAndroid(): boolean {
  return Capacitor.isNativePlatform() && Capacitor.getPlatform() === "android";
}

export async function initAuthStorage(): Promise<string | null> {
  if (typeof window === "undefined") return null;
  if (initialized) return memoryToken;
  initialized = true;

  if (Capacitor.isNativePlatform()) {
    // Purge any legacy WebView localStorage token so secrets never persist in plaintext.
    try {
      window.localStorage.removeItem(TOKEN_KEY);
    } catch {
      // Ignore storage access errors.
    }
    try {
      const res = await TrustLensSecureStorage.getToken({ key: TOKEN_KEY });
      memoryToken = res?.value || null;
      return memoryToken;
    } catch {
      memoryToken = null;
      return null;
    }
  }

  memoryToken = window.localStorage.getItem(TOKEN_KEY);
  return memoryToken;
}

export function getStoredTokenSync(): string | null {
  if (typeof window === "undefined") return null;
  if (Capacitor.isNativePlatform()) {
    return memoryToken;
  }
  return memoryToken ?? window.localStorage.getItem(TOKEN_KEY);
}

export function setStoredTokenSecure(token: string): void {
  memoryToken = token;
  if (typeof window === "undefined") return;
  if (Capacitor.isNativePlatform()) {
    try {
      window.localStorage.removeItem(TOKEN_KEY);
    } catch {
      // Ignore.
    }
    void TrustLensSecureStorage.setToken({ key: TOKEN_KEY, value: token }).catch(() => {});
    return;
  }
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredTokenSecure(): void {
  memoryToken = null;
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(TOKEN_KEY);
  } catch {
    // Ignore.
  }
  if (Capacitor.isNativePlatform()) {
    void TrustLensSecureStorage.clearToken({ key: TOKEN_KEY }).catch(() => {});
  }
}
