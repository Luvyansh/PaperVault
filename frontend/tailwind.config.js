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
    // DaisyUI 5 on Tailwind 3: root `daisyui` key is ignored — pass options here.
    // Theme CSS variables come from index.css imports; disable bundled default themes.
    require("daisyui")({
      themes: false,
      logs: false,
    }),
  ],
}