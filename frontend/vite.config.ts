import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// In development the UI calls the services through this proxy, so the browser
// sees one origin (no CORS). In Docker, nginx does the same (see nginx.conf).
const services = {
  "/api/chat": "http://localhost:8001",
  "/api/analytics": "http://localhost:8002",
  "/api/ingestion": "http://localhost:8003",
};

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: Object.fromEntries(
      Object.entries(services).map(([prefix, target]) => [
        prefix,
        { target, changeOrigin: true, rewrite: (path: string) => path.replace(prefix, "") },
      ]),
    ),
  },
  test: { environment: "node" },
});
