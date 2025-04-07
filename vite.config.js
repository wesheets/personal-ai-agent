import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/ui-v2/',
  build: {
    outDir: 'dist',
  },
  server: {
    historyApiFallback: {
      rewrites: [
        { from: /^\/ui-v2\/.*/, to: '/ui-v2/index.html' },
      ],
    },
  },
})
