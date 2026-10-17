# The website

Astro, fully static, on the Sentient Horizons design standard (`sentient-horizons/design/`), served from Cloudflare Workers static assets with a small worker in front for forwarding. Holding version, 2026-10-16.

## Pages

| address | what it is |
|---|---|
| `/` | the home page, in the tracker pattern's first-screen order: eyebrow, the year (in words until computed), the question, one paragraph, the last-checked strip, two buttons; then the three numbers to come, the eight branches with live counts, the six kinds of record with live counts, how the numbers are worked out, who is asking |
| `/404.html` | not found |

The site session adds the tracker pattern's seven pages (`design/tracker-pattern.md`, section 4) plus the claims log and the self-experiments pages.

## How it is built

- **The styles are the family's skeleton with this site's own skin.** `src/styles/skin.css` is the "Ledger" skin (paper and ink with a clinical blue, the sepia second mark shared with The Upgrade Tree; light by default; ruled by John 2026-10-17 from `sentient-horizons/design/proposals/outrunning-ageing-skin-2026-10-17.md`), every token for both themes and nothing else. `src/styles/global.css` imports it, then carries `sentient-horizons/design/shell.css` copied unchanged (version noted at the marked line), then this site's own rules. There is no backdrop: the chart on the home page is the picture.
- `src/components/Spread.astro` is the trunk's picture, the spread of escape years, drawn at build time from the headline in `records.json`: five-year bars, the middle estimate as a rule, the fixed promised date as a dashed line in the second mark, the nine-in-ten span as a bracket, the not-this-century share at the edge. Nothing on it is drawn by hand.
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
