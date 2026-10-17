# The website

Astro, fully static, on the Sentient Horizons design standard (`sentient-horizons/design/`), served from Cloudflare Workers static assets with a small worker in front for forwarding. Holding version, 2026-10-16.

## Pages

| address | what it is |
|---|---|
| `/` | the home page, in the tracker pattern's first-screen order: eyebrow, the year (in words until computed), the question, one paragraph, the last-checked strip, two buttons; then the three numbers to come, the eight branches with live counts, the six kinds of record with live counts, how the numbers are worked out, who is asking |
| `/404.html` | not found |

The site session adds the tracker pattern's seven pages (`design/tracker-pattern.md`, section 4) plus the claims log and the self-experiments pages.

## How it is built

- `src/styles/global.css` is `design/deep-field.css` copied unchanged (version 2.0.1), with this site's own rules below the marked line. The site's own skin, when John rules it, replaces the skin half of that file; see the design standard's section 3a.
- `src/layouts/Base.astro` and `src/components/Nav.astro` are the standard's shell: theme script, two-tier top bar, four-line footer, then the medical notice John ruled on 2026-10-16, then the family line.
- `src/lib/records.ts` types the JSON that `scripts/export.py` writes to `src/data/records.json` at build time (not committed). Every page reads from it; nothing in the browser touches the TOML records.
- `worker/redirect.js` runs in front of the static files and sends www.outrunningageing.com, outrunningaging.com and www.outrunningaging.com to the same page at outrunningageing.com with a permanent redirect.
- `wrangler.jsonc` names the worker and carries the four custom-domain routes.

## Commands

    npm ci              install (once)
    npm run dev         export the records and serve locally
    npm run build       export the records and build into dist/
    npm run deploy      build and deploy by hand (needs wrangler logged in)

Every push to `main` that touches `data/`, `scripts/`, `site/` or the changelog runs `.github/workflows/deploy.yml`, which validates, tests, builds and deploys. Preview address: outrunningageing.jfredson.workers.dev.
