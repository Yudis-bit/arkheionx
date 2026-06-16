# ArkheionX Website Deployment

The website is an Astro static build under `site/`. It has no runtime API,
analytics, remote font dependency, or secret configuration.

## Build locally

Requirements:

- Node.js 20 or newer
- npm

```bash
cd site
npm install
npm run build
cd ..
```

The static output is written to `site/dist/`. Verify both install surfaces:

```bash
test -f site/dist/install
test -f site/dist/install.html
bash -n site/dist/install
grep -q "Install ArkheionX" site/dist/install.html
```

Astro uses file-format output because two public resources share the install
name:

- `/install` is the Bash endpoint used by `curl`.
- `/install.html` is the browser page.

The Nginx rule below sends browser requests for `/install` to the HTML page and
serves the Bash file to command-line clients.

## Deploy the static dist

Use immutable release directories and a `current` symlink:

```bash
release_id="$(date -u +%Y%m%d%H%M%S)"
sudo mkdir -p "/var/www/arkheionx/releases/$release_id"
sudo cp -a site/dist/. "/var/www/arkheionx/releases/$release_id/"
sudo ln -sfn "/var/www/arkheionx/releases/$release_id" /var/www/arkheionx/current
sudo chown -R root:root "/var/www/arkheionx/releases/$release_id"
sudo find "/var/www/arkheionx/releases/$release_id" -type d -exec chmod 0755 {} \;
sudo find "/var/www/arkheionx/releases/$release_id" -type f -exec chmod 0644 {} \;
```

The source installer does not need its executable bit on the web server. Nginx
serves it as text and the client runs it with Bash.

## Nginx

Create `/etc/nginx/sites-available/arkheionx.dev`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name arkheionx.dev www.arkheionx.dev;

    root /var/www/arkheionx/current;
    index index.html;

    location = /install {
        if ($http_accept ~* "text/html") {
            return 302 /install.html;
        }

        default_type text/plain;
        add_header X-Content-Type-Options nosniff always;
        try_files /install =404;
    }

    location / {
        try_files $uri $uri.html $uri/ =404;
    }

    location ~* \.(css|js|svg|png|jpg|jpeg|webp|ico)$ {
        expires 1h;
        add_header Cache-Control "public, max-age=3600";
        try_files $uri =404;
    }
}
```

Enable and test it:

```bash
sudo ln -s /etc/nginx/sites-available/arkheionx.dev /etc/nginx/sites-enabled/arkheionx.dev
sudo nginx -t
sudo systemctl reload nginx
```

Avoid a long cache lifetime on `/install`; updates should become visible
immediately after deployment.

## DNS records

Create records at the authoritative DNS provider:

| Type | Name | Value |
|---|---|---|
| `A` | `@` | Server IPv4 address |
| `AAAA` | `@` | Server IPv6 address, if configured |
| `CNAME` | `www` | `arkheionx.dev` |

Wait for DNS resolution before requesting a certificate:

```bash
dig +short A arkheionx.dev
dig +short AAAA arkheionx.dev
dig +short CNAME www.arkheionx.dev
```

## Certbot

Install the Nginx plugin from the operating system package manager, then run:

```bash
sudo certbot --nginx -d arkheionx.dev -d www.arkheionx.dev
sudo certbot renew --dry-run
```

Re-run `sudo nginx -t` after certificate changes.

## Install endpoint verification

Verify the browser and shell representations independently:

```bash
curl -fsS -H 'Accept: text/html' -o /tmp/arkheionx-install-page https://arkheionx.dev/install
grep -q '<title>Install ArkheionX' /tmp/arkheionx-install-page

curl -fsS -H 'Accept: */*' -o /tmp/arkheionx-install-script https://arkheionx.dev/install
bash -n /tmp/arkheionx-install-script
grep -q 'Yudis-bit/arkheionx.git' /tmp/arkheionx-install-script
grep -q 'BRANCH="main"' /tmp/arkheionx-install-script
```

Do not execute the installer as part of a production website smoke test unless
the test runs in an isolated disposable user environment.

## Website verification

```bash
curl -fsSI https://arkheionx.dev/
curl -fsS https://arkheionx.dev/ | grep -q 'Deterministic review artifacts'
curl -fsS https://arkheionx.dev/docs | grep -q 'Build a review surface'
curl -fsS https://arkheionx.dev/security | grep -q 'Use only with authorization'
```

Also inspect desktop and mobile layouts in a browser, verify keyboard focus,
and check that no request leaves the site origin during a normal page load.

## Rollback

List deployed releases and repoint `current` to the last known-good directory:

```bash
ls -1 /var/www/arkheionx/releases
sudo ln -sfn /var/www/arkheionx/releases/PREVIOUS_RELEASE_ID /var/www/arkheionx/current
sudo nginx -t
sudo systemctl reload nginx
```

Repeat the website and install endpoint verification after rollback.

## Secret handling

- Do not commit deployment credentials, SSH keys, certificate material, or
  provider tokens.
- The static build requires no secrets.
- No Cloudflare token is configured. Add one only after a separate deployment
  design and secret-storage decision.
- Keep server-specific values in deployment infrastructure, not in this
  repository.
