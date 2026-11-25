// SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// Relative base so the built site works from any static folder, offline.
export default defineConfig({
  base: "./",
  plugins: [react()],
  build: { outDir: "dist", assetsInlineLimit: 0, sourcemap: false },
  test: { environment: "node", include: ["src/**/*.test.ts"] },
});
