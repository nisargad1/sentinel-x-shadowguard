/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cyber: {
          dark: '#080C14',
          card: '#0D1424',
          panel: '#131D33',
          border: '#1E2B45',
          cyan: '#00E5FF',
          cyanGlow: 'rgba(0, 229, 255, 0.25)',
          red: '#FF3366',
          redGlow: 'rgba(255, 51, 102, 0.25)',
          amber: '#FFB800',
          emerald: '#00E676'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif']
      }
    },
  },
  plugins: [],
}
