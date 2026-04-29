/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0d1117',
        card: '#161b22',
        accentGreen: '#00ff88',
        accentRed: '#ff4d6d',
        accentYellow: '#fbbf24',
        textPrimary: '#e6edf3',
        textSecondary: '#8b949e',
        border: '#30363d',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
