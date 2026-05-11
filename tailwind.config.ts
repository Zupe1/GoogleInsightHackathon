import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: "#020817",
          900: "#0a1628",
          800: "#0f2040",
          700: "#152a52",
          600: "#1e3a6e",
        },
        brand: {
          red:  "#c8102e",
          blue: "#0057a8",
          glow: "#378add",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      boxShadow: {
        glow:     "0 0 20px rgba(55,138,221,0.3)",
        "glow-lg":"0 0 40px rgba(55,138,221,0.4)",
        "glow-red":"0 0 20px rgba(200,16,46,0.4)",
      },
      backgroundImage: {
        "grid-pattern":
          "linear-gradient(rgba(55,138,221,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(55,138,221,0.05) 1px, transparent 1px)",
      },
      backgroundSize: {
        "grid": "40px 40px",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4,0,0.6,1) infinite",
        "fade-in":    "fadeIn 0.3s ease-in-out",
        "slide-in":   "slideIn 0.3s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideIn: {
          "0%":   { transform: "translateX(20px)", opacity: "0" },
          "100%": { transform: "translateX(0)",    opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;

