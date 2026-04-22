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
        icons: [
          { src: "icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "icon-512.png", sizes: "512x512", type: "image/png" }
        ]
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,ico,png,svg,woff2}"],
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
    },
  },
});
