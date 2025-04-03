import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    host: true, // Listen on all addresses
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false, // ✅ Sourcemaps disabled for Chakra UI + Vercel compatibility
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'public/index.html'),
      },
    },
  },
  root: '.',
  publicDir: 'public',
});
