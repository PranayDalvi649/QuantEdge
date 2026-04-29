/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#06090f',
        card: 'rgba(16, 21, 32, 0.65)',
        accentGreen: '#00ffaa',
        accentRed: '#ff3366',
        accentYellow: '#ffd700',
        textPrimary: '#f0f6fc',
        textSecondary: '#8b949e',
        border: 'rgba(255, 255, 255, 0.08)',
        chartArea: 'rgba(0, 255, 170, 0.1)',
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glow-green': '0 0 20px rgba(0, 255, 170, 0.4)',
        'glow-red': '0 0 20px rgba(255, 51, 102, 0.4)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      }
    },
  },
  plugins: [],
}
