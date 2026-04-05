module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'aqi': {
          'good': '#2ecc71',
          'fair': '#f1c40f',
          'moderate': '#e67e22',
          'poor': '#e74c3c',
          'very-poor': '#8b0000',
          'severe': '#4b0000'
        }
      },
      animation: {
        'pulse-soft': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 3s linear infinite',
      }
    },
  },
  plugins: [],
}
