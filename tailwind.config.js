/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        accent: {
          DEFAULT: '#00FFFF',
          light: '#66FFFF',
          dark: '#00CCCC',
        },
      },
    },
  },
  darkMode: 'class',
  plugins: [],
}
