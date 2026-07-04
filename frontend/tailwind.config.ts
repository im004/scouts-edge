import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        pitch: "#10251f",
        ink: "#0b1115",
        panel: "#111c22",
        line: "#263841",
        mint: "#48d597",
        amber: "#f7c66a",
        coral: "#ff7a70"
      }
    }
  },
  plugins: []
};

export default config;
