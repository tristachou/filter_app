import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // This is crucial for Docker
    host: '0.0.0.0', 
    port: 5173,
    allowedHosts: [
      'ec2-3-107-90-126.ap-southeast-2.compute.amazonaws.com',
      'filterapp.cab432.com',
    ],
    // The proxy section is removed because Nginx is handling all routing.
  }
})