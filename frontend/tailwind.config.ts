import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#050306",
          panel: "#10070D",
          panelAlt: "#170A12",
          red: "#FF174F",
          crimson: "#C2185B",
          pink: "#FF3D70",
          border: "#481326",
          muted: "#A1A1AA",
          success: "#00D68F",
          warning: "#FFB020",
        },
        // Preserved aliases mapped into dark cyber tokens for seamless component compatibility
        navy: {
          950: "#050306",
          900: "#0A0408",
          850: "#10070D",
          800: "#170A12",
          700: "#260E1B",
          600: "#481326",
        },
        brand: {
          50: "#fff1f4",
          100: "#ffe4ea",
          500: "#FF174F",
          600: "#C2185B",
          700: "#9E1248",
        },
        accent: {
          50: "#fff1f5",
          100: "#ffe4ec",
          500: "#FF3D70",
          600: "#FF174F",
          700: "#C2185B",
        },
        canvas: "#050306",
        cardLight: "#10070D",
        subtleBorder: "#481326",
        threatq: {
          bg: "#050306",
          nav: "#10070D",
          canvas: "#050306",
          panel: "#10070D",
          border: "#481326",
          timeline: "#170A12",
          accent: "#FF174F",
          cyan: "#FF3D70",
          text: "#FFFFFF",
          muted: "#A1A1AA",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Courier New", "monospace"],
      },
      boxShadow: {
        subtle: "0 1px 3px 0 rgba(0, 0, 0, 0.4)",
        card: "0 8px 24px -4px rgba(0, 0, 0, 0.65)",
        neon: "0 0 22px rgba(255, 23, 79, 0.25)",
        "neon-strong": "0 0 32px rgba(255, 23, 79, 0.42)",
      },
    },
  },
  plugins: [],
};
export default config;
