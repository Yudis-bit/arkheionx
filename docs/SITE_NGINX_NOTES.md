# Site Nginx notes

How to serve the static Arkheionx site (`site/dist/`) behind Nginx so missing
routes and common typo routes feel professional instead of returning the default
Nginx error page.

The site is built with Astro `build.format: "file"`, so routes are served as
`.html` files (for example `/docs/bug-bounty` → `docs/bug-bounty.html`).

## Two layers of alias handling

1. **Static redirect pages (already built):** Astro emits lightweight
   meta-refresh HTML for the aliases in `astro.config.mjs` (for example
   `dist/docs/bugbounty.html` redirects to `/docs/bug-bounty`). These work behind
   plain Nginx with no extra config.
2. **Server-level 301 rewrites (preferred):** instant, no redirect flash, and
   SEO-friendly. Use the `rewrite` rules below when you control the Nginx config.

## Recommended server block

```nginx
server {
    listen 443 ssl;
    server_name arkheionx.dev;
    root /var/www/arkheionx.dev;
    index index.html;

    # Custom, on-brand 404 page.
    error_page 404 /404.html;

    # Common typo / legacy aliases -> canonical routes (instant 301).
    rewrite ^/docs/bugbounty/?$   /docs/bug-bounty   permanent;
    rewrite ^/docs/howitworks/?$  /docs/how-it-works permanent;
    rewrite ^/docs/cli/?$         /docs/cli-reference permanent;
    rewrite ^/docs/commands/?$    /docs/cli-reference permanent;
    rewrite ^/docs/quick-start/?$ /docs/quickstart   permanent;
    rewrite ^/docs/get-started/?$ /docs/getting-started permanent;
    rewrite ^/docs/safety/?$      /docs/safety-model permanent;
    rewrite ^/docs/v4-release/?$  /docs/v4           permanent;

    # Normalize a trailing slash on canonical routes (e.g. /docs/bug-bounty/).
    rewrite ^/(.+)/$ /$1 permanent;

    # Static route fallback: try the path, a directory, the .html file, then 404.
    location / {
        try_files $uri $uri/ $uri.html /404.html;
    }
}
```

## Minimal version

If you only change two things, change these:

```nginx
error_page 404 /404.html;
location / { try_files $uri $uri/ $uri.html /404.html; }
```

With just this, the Astro-built alias pages still work (via meta refresh) and
unknown routes show the on-brand `/404.html` instead of the default Nginx page.

## Verify after deploy

```sh
curl -I https://arkheionx.dev/docs/bug-bounty      # 200
curl -I https://arkheionx.dev/docs/bugbounty       # 301 -> /docs/bug-bounty
curl -I https://arkheionx.dev/docs/cli             # 301 -> /docs/cli-reference
curl -I https://arkheionx.dev/this-route-does-not-exist  # 404 -> on-brand page
```

The 404 page itself is local/static only: no RPC, no live-chain calls, no
analytics, and no network calls. See [`SITE_VISUAL_QA.md`](SITE_VISUAL_QA.md).
