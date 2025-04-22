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
        mono: ['Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      colors: {
        accent: {
          DEFAULT: '#00FFFF',
          light: '#66FFFF',
          dark: '#00CCCC',
        },
        gray: {
          900: '#111827',
          800: '#1F2937',
          700: '#374151',
        },
        black: '#000000',
        white: '#FFFFFF',
        green: {
          400: '#4ADE80',
        },
      },
    },
  },
  darkMode: 'class',
  plugins: [],
}
