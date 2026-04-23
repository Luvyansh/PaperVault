/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"], // Tells Shadcn to look for the "dark" class we just added
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "var(--border)",
        input: "var(--input)",
        ring: "var(--ring)",
        background: "var(--background)",
        foreground: "var(--foreground)",
        destructive: {
          DEFAULT: "var(--destructive)",
          foreground: "var(--destructive-foreground)",
        },
      },
    },
  },
  plugins: [
    require("tailwindcss-animate"),
    require("daisyui"),
  ],
  daisyui: {
    themes: [
      {
        luxury: {
          "color-scheme": "dark",
          "base-100": "oklch(14.076% 0.004 285.822)",
          "base-200": "oklch(20.219% 0.004 308.229)",
          "base-300": "oklch(23.219% 0.004 308.229)",
          "base-content": "oklch(75.687% 0.123 76.89)",
          "primary": "oklch(0.202 0.000 0.0)",
          "primary-content": "oklch(1.000 0.000 0.0)",
          "secondary": "oklch(27.581% 0.064 261.069)",
          "secondary-content": "oklch(85.516% 0.012 261.069)",
          "accent": "oklch(36.674% 0.051 338.825)",
          "accent-content": "oklch(87.334% 0.01 338.825)",
          "neutral": "oklch(24.27% 0.057 59.825)",
          "neutral-content": "oklch(93.203% 0.089 90.861)",
          "info": "oklch(79.061% 0.121 237.133)",
          "success": "oklch(78.119% 0.192 132.154)",
          "warning": "oklch(86.127% 0.136 102.891)",
          "error": "oklch(71.753% 0.176 22.568)",
        },
      },
    ],
  },
}