module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      animation: {
        'fade-in': 'fadeIn 1.5s ease-out forwards',
        'logo-glow': 'glowPulse 2s infinite ease-in-out',
        'pulse-slow': 'pulse 3s ease-in-out infinite'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        glowPulse: {
          '0%, 100%': {
            filter: 'drop-shadow(0 0 0 rgba(255,255,255,0))',
          },
          '50%': {
            filter: 'drop-shadow(0 0 12px rgba(255,255,255,0.8))',
          },
        },
      },
    },
  },
  plugins: [],
};

