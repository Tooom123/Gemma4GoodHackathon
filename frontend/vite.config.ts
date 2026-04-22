import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.ico", "robots.txt"],
      manifest: {
        name: "LangBridge",
        short_name: "LangBridge",
        description: "Apprenez la langue locale avec des simulations réelles",
        theme_color: "#1d4ed8",
        background_color: "#ffffff",
        display: "standalone",
        start_url: "/",
        lang: "fr",
        icons: [
          { src: "icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "icon-512.png", sizes: "512x512", type: "image/png" },
          { src: "icon-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
        ],
      },
      workbox: {
        // Cache all static assets
        globPatterns: ["**/*.{js,css,html,ico,png,svg,woff2,json}"],
        // Cache scenarios API responses (stale-while-revalidate)
        runtimeCaching: [
          {
            urlPattern: /^http:\/\/localhost:8000\/scenarios\//,
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "scenarios-cache",
              expiration: { maxEntries: 50, maxAgeSeconds: 60 * 60 * 24 * 7 },
            },
          },
          {
            urlPattern: /^http:\/\/localhost:8000\/progress\//,
            handler: "NetworkFirst",
            options: {
              cacheName: "progress-cache",
              networkTimeoutSeconds: 5,
              expiration: { maxEntries: 20, maxAgeSeconds: 60 * 60 * 24 },
            },
          },
        ],
      },
    }),
  ],
  server: {
    port: 5173,
    proxy: {
      "/chat": "http://localhost:8000",
      "/scenarios": "http://localhost:8000",
      "/progress": "http://localhost:8000",
      "/tts": "http://localhost:8000",
      "/whisper": "http://localhost:8000",
    },
  },
});
