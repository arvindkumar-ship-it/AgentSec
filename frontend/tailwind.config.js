/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      // colors: {
      //   surface: "#0d0f14",
      //   panel: "#13161d",
      //   border: "#1e2330",
      //   accent: "#6366f1",
      //   "accent-dim": "#4f46e5",
      //   danger: "#ef4444",
      //   warn: "#f59e0b",
      //   safe: "#22c55e",
      //   muted: "#6b7280",
      //   subtle: "#9ca3af",
      // },
      colors: {
      surface: "#e8e6e1",
      panel: "#f4f2ee",
      border: "#d9d6cf",
      accent: "#6366f1",
      "accent-dim": "#4f46e5",
      danger: "#ef4444",
      warn: "#f59e0b",
      safe: "#22c55e",
      muted: "#6b7280",
      subtle: "#4b5563",
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
