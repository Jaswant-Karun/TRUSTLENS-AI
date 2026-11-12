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
        // Dark Navy Sidebar Palette
        navy: {
          950: "#070d1e",
          900: "#0b1329",
          850: "#0f172a",
          800: "#17233f",
          700: "#1e2e50",
          600: "#2a3d66",
        },
        // Restrained Cyan & Blue Accents
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
        accent: {
          50: "#ecfeff",
          100: "#cffafe",
          500: "#06b6d4",
          600: "#0284c7",
          700: "#0369a1",
        },
        // Clean Content Background & Surfaces
        canvas: "#f8fafc",
        cardLight: "#ffffff",
        subtleBorder: "#e2e8f0",
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Courier New", "monospace"],
      },
      boxShadow: {
        subtle: "0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)",
        card: "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)",
      },
    },
  },
  plugins: [],
};
export default config;

