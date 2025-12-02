import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // This makes the server accessible externally (e.g., to ngrok)
    hmr: {
      host: 'unsobered-rankly-leif.ngrok-free.dev', // Set HMR to use the ngrok public host
      protocol: 'wss', // Use WebSocket Secure protocol for HMR over HTTPS
    },
    allowedHosts: ['unsobered-rankly-leif.ngrok-free.dev'],
  },
});
