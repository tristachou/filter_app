import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // This is crucial for Docker
    host: '0.0.0.0', 
    allowedHosts: [
      'ec2-52-63-176-232.ap-southeast-2.compute.amazonaws.com',
      'filterapp.cab432.com',
    ],
    port: 5173,
    // Configure the reverse proxy
    proxy: {
      // Requests to /api will be sent to the backend
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
