/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './templates/**/*.html',
    './node_modules/flowbite/**/*.js'
  ],
  theme: {
    extend: {
      fontFamily: {
        bangla: ["Hind Siliguri"],
        sans: ["Manrope", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Manrope", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        /* Legacy dashboard/blog palette - kept untouched so admin_panel + blog keep working */
        primary: { "50": "#f0f9ff", "100": "#e0f2fe", "200": "#bae6fd", "300": "#7dd3fc", "400": "#38bdf8", "500": "#0ea5e9", "600": "#0284c7", "700": "#0369a1", "800": "#075985", "900": "#0c4a6e", "950": "#082f49" },

        secondary: { "50": "#f8fafc", "100": "#f1f5f9", "200": "#e2e8f1", "300": "#cbd5e1", "400": "#94a3b8", "500": "#64748b", "600": "#475569", "700": "#334155", "800": "#1e293b", "900": "#0f172a", "950": "#020617" },

        /* ============ Beginners Hut brand palette ============ */
        /* Deep Green #087F5B is the anchor -> brand-700 */
        brand: {
          "50": "#EAF7F2",
          "100": "#D1EFE3", // Soft Green #E8F5EF family
          "200": "#A9DFC9",
          "300": "#71C8A9",
          "400": "#34AC84",
          "500": "#20A66A", // Fresh Green
          "600": "#128F5B",
          "700": "#087F5B", // Primary Deep Green
          "800": "#076248",
          "900": "#064E3A",
          "950": "#022C21",
        },
        /* Vibrant Orange #FF7A00 -> accent-500 */
        accent: {
          "50": "#FFF5EB",
          "100": "#FFE7D1",
          "200": "#FFCEA3",
          "300": "#FFAE66",
          "400": "#FF9533",
          "500": "#FF7A00",
          "600": "#E06900",
          "700": "#B85400",
          "800": "#8F4200",
          "900": "#6B3200",
        },
        /* Bright Yellow #FFC928 -> sun-500 */
        sun: {
          "50": "#FFFBEB",
          "100": "#FFF5CC",
          "200": "#FFE992",
          "300": "#FFDD57",
          "400": "#FFD13C",
          "500": "#FFC928",
          "600": "#E0A912",
          "700": "#B8850C",
          "800": "#8F670A",
          "900": "#6B4E08",
        },
        /* Deep Charcoal #10231D -> ink-900 */
        ink: {
          "50": "#F4F7F6",
          "100": "#E6ECEA",
          "200": "#CBD9D4",
          "300": "#9DB3AA",
          "400": "#6E8A80",
          "500": "#4A655C",
          "600": "#334B43",
          "700": "#20362F",
          "800": "#16302A",
          "900": "#10231D", // Deep Charcoal
          "950": "#071511",
        },

        /* ============ Semantic theme colors (CSS variables) ============
           Light values live in static/src/input.css :root, dark in .dark */
        'bh-bg': 'rgb(var(--bh-bg) / <alpha-value>)',
        'bh-surface': 'rgb(var(--bh-surface) / <alpha-value>)',
        'bh-surface-2': 'rgb(var(--bh-surface-2) / <alpha-value>)',
        'bh-line': 'rgb(var(--bh-line) / <alpha-value>)',
        'bh-text': 'rgb(var(--bh-text) / <alpha-value>)',
        'bh-muted': 'rgb(var(--bh-muted) / <alpha-value>)',
        'bh-faint': 'rgb(var(--bh-faint) / <alpha-value>)',
      },
      borderRadius: {
        '4xl': '2rem',
        '5xl': '2.5rem',
      },
      boxShadow: {
        card: '0 1px 2px rgb(16 35 29 / 0.04), 0 8px 24px -12px rgb(16 35 29 / 0.12)',
        'card-hover': '0 2px 4px rgb(16 35 29 / 0.06), 0 24px 48px -20px rgb(16 35 29 / 0.22)',
        glow: '0 10px 40px -12px rgb(8 127 91 / 0.45)',
        'glow-accent': '0 10px 40px -12px rgb(255 122 0 / 0.45)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'brand-gradient': 'linear-gradient(135deg, #087F5B 0%, #20A66A 100%)',
        'accent-gradient': 'linear-gradient(135deg, #FF7A00 0%, #FFC928 100%)',
        'grid-pattern':
          "linear-gradient(to right, rgb(var(--bh-line) / 0.7) 1px, transparent 1px), linear-gradient(to bottom, rgb(var(--bh-line) / 0.7) 1px, transparent 1px)",
      },
      maxWidth: {
        container: '1280px',
      },
      transitionTimingFunction: {
        smooth: 'cubic-bezier(0.22, 1, 0.36, 1)',
      },
      keyframes: {
        marquee: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'pulse-ring': {
          '0%': { transform: 'scale(0.9)', opacity: '0.7' },
          '70%': { transform: 'scale(1.5)', opacity: '0' },
          '100%': { transform: 'scale(1.5)', opacity: '0' },
        },
      },
      animation: {
        marquee: 'marquee 40s linear infinite',
        'fade-up': 'fade-up 0.6s cubic-bezier(0.22, 1, 0.36, 1) both',
        shimmer: 'shimmer 2.5s linear infinite',
        'pulse-ring': 'pulse-ring 2.4s cubic-bezier(0.24, 0, 0.38, 1) infinite',
      },
    },
  },
  plugins: [
    require('flowbite/plugin')({
      charts: true,
    }),

  ]
}