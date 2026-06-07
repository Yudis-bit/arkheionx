import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://arkheionx.dev",
  output: "static",
  trailingSlash: "never",
  build: {
    format: "file"
  },
  // Common typo / legacy aliases. In a static build these emit lightweight
  // meta-refresh HTML pages, so they work behind plain Nginx. Server-level
  // 301 rewrites are documented in docs/SITE_NGINX_NOTES.md and are preferred
  // when available.
  redirects: {
    "/docs/bugbounty": "/docs/bug-bounty",
    "/docs/howitworks": "/docs/how-it-works",
    "/docs/cli": "/docs/cli-reference",
    "/docs/commands": "/docs/cli-reference",
    "/docs/quick-start": "/docs/quickstart",
    "/docs/get-started": "/docs/getting-started",
    "/docs/safety": "/docs/safety-model",
    "/docs/v4-release": "/docs/v4"
  }
});
