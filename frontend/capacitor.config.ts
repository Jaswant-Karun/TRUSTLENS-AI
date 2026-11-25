import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "ai.trustlens.mobile",
  appName: "TRUSTLENS AI",
  webDir: "out",
  backgroundColor: "#050306",
  server: {
    androidScheme: "https",
  },
  android: {
    allowMixedContent: false,
    backgroundColor: "#050306",
  },
  plugins: {
    StatusBar: {
      style: "DARK",
      backgroundColor: "#050306",
    },
    SplashScreen: {
      backgroundColor: "#050306",
      launchShowDuration: 1200,
      showSpinner: false,
    },
  },
};

export default config;
