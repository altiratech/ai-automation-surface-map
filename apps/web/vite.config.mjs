import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const repoRoot = path.resolve(import.meta.dirname, "../..");
const surfaceMapPath = path.resolve(
  repoRoot,
  "artifacts/ria_marketing_rule_review.surface_map.json",
);
const surfaceMapAnnualPath = path.resolve(
  repoRoot,
  "artifacts/ria_annual_adv_update.surface_map.json",
);

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@surface-map": surfaceMapPath,
      "@surface-map-annual": surfaceMapAnnualPath,
    },
  },
  server: {
    fs: {
      allow: [repoRoot],
    },
  },
});
