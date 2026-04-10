import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0f1115",
        panel: "#1a1d23",
        "panel-2": "#252932",
        accent: "#ff3e3e",
        "accent-hover": "#e03030",
        muted: "#8a95a8",
        line: "#343844",
        "green-ok": "#059669",
      },
      fontFamily: {
        sans: ["Outfit", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
