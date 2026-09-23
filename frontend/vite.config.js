import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite serves the React app on port 5173 during development.
// Any request that starts with /api is forwarded to the Flask backend on
// port 5001, so the frontend code can simply call fetch("/api/...").
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:5001",
    },
  },
});
