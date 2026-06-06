import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://arkheionx.dev",
  output: "static",
  trailingSlash: "never",
  build: {
    format: "file"
  }
});
