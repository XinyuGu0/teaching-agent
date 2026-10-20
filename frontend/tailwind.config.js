/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#409eff',
          foreground: '#ffffff',
        },
        background: '#ffffff',
        foreground: '#1f2937',
        muted: {
          DEFAULT: '#f3f4f6',
          foreground: '#6b7280',
        },
      },
      animation: {
        'marquee': 'marquee var(--duration) linear infinite',
      },
      keyframes: {
        marquee: {
          from: { transform: 'translateX(0)' },
          to: { transform: 'translateX(calc(-100% - var(--gap)))' },
        },
      },
    },
  },
  plugins: [],
}