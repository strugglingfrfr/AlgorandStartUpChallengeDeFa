import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Polyfill Node globals for browser
export default defineConfig({
  plugins: [react()],
  define: {
    global: 'globalThis',
  },
  optimizeDeps: {
    include: ['buffer', 'process'],
  },
})
