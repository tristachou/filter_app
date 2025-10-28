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
      'n11696630-696058442.ap-southeast-2.elb.amazonaws.com',
      'ec2-54-79-172-183.ap-southeast-2.compute.amazonaws.com',
      'webfilterapp.cab432.com',
    ],
    // The proxy section is removed because Nginx is handling all routing.
  }
})