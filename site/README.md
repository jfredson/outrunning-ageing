# The website

Astro, fully static, on the Sentient Horizons design standard (`sentient-horizons/design/`), served from Cloudflare Workers static assets with a small worker in front for forwarding. Holding version 2026-10-16; the pages built and live at outrunningageing.com 2026-10-17.

## Pages

Built 2026-10-17 against the design standard's skeleton tokens only (no colour or typeface of the site's own, no backdrop), so the site's own skin can land later as the skin half of `src/styles/global.css` without restyling a page. The public names are the tracker pattern's (`design/tracker-pattern.md`, section 4); the top bar carries short handles under rule 4.7 (Branches · Claims · Self-experiments · Reading · Story | Method · Disagree · Source), the scheme the Ledger skin's mock-up shows and John pre-approved on 2026-10-17, with Self-experiments added after Claims at his ruling the same day; the footer, the home page and the claims log still link to the self-experiments page too.

| address | public name | what it is |
|---|---|---|
| `/` | the site's name | the home page, in the tracker pattern's first-screen order: eyebrow, the computed year in figures with its spread and the two numbers beside it (the chance before 2050, the share not this century), the question, one paragraph, the last-checked strip, two buttons; then what a treatment is, the eight branches with live counts and the year each is handled in the middle run, the six kinds of record with live counts, who is asking |
| `/branches/` | The tree | the index of the eight branches, and the stage ladder explained once |
| `/branches/<key>/` | the branch's name | one page per branch with the six things a branch page carries: meaning and the hallmarks it groups; its own number (the year it is handled in the middle run, what is in the clinic, the furthest stage); its treatments by how soon each could move; what would move this; its history; what the story so far says about it |
| `/leaves/<id>/` | the treatment's name | one page per treatment or tool: the paragraph, what would count, who settles it, where it stands with the date, the stage ladder with the record for each rung, the estimate as a range with its reasoning, the revision log, the last three readings, the claims that promise it, the self-experiments that try it, the papers behind it, the Upgrade Tree sibling where one exists, the facts not yet verified, and two buttons to disagree with this one thing. The address never changes once published |
| `/claims/` | The claims log | who promised what, when, with the primary source, what it commits to, the due year and the verdict, beside the treatment each rests on and how far it has got; entries held on coverage only are shown and marked, as the five sourcing rulings of 2026-10-17 say |
| `/self-experiments/` | Other people's self-experiments | who, what they do, what they measure, what they claim, what the public record shows, and the one line the site repeats: a claim about one person is a story, not a record, and it moves nothing on the tree |
| `/story/` | The story so far | the publications log as dated entries, newest first, each saying what it settled or moved, with the ones that moved nothing given equal billing; then the changelog day by day |
| `/reading/` | This week's reading | every weekly reading of the treatments, the claims and the self-experiments against the news, newest first: the latest reading's summary and counts, its items grouped by branch (a claim about the whole question under its own heading), each a card with the verdict, what was found, the line left for the author, and the searches and sources folded away; the flagged items still waiting on the author; earlier readings collapsed; and the key to the four verdicts. The home page's strip reads the latest reading, and each treatment's page shows its last three |
| `/method/` | How the numbers are worked out | the plain account: who is asking, what the computation does, the numbers as they stand with the spread drawn as a live chart, one run written out by hand, the ten settings each with its reason and strongest alternative, where the ranges come from, what counts as a record, who does what, and the working documents linked with prefaces |
| `/disagree/` | Disagree with something | the three forms (a missing treatment with its test; a questioned test or settler; an argued range), each an issue template in `.github/ISSUE_TEMPLATE/`, and what happens next in four steps |
| `/404.html` | | not found |
| `/data/headline.json` | | the computed headline file, `data/headline.json` in the repository, served unchanged from the site since 2026-10-17 so that a reader who knows only the site can fetch the numbers and the parent site can read them from here |
| `/robots.txt` | | allows crawling and promises nothing: there is no sitemap, and every page is reached from the home page and the top bar |

## How it is built

- **The styles are the family's skeleton with this site's own skin.** `src/styles/skin.css` is the "Ledger" skin (paper and ink with a clinical blue, the sepia second mark shared with The Upgrade Tree; light by default; ruled by John 2026-10-17 from `sentient-horizons/design/proposals/outrunning-ageing-skin-2026-10-17.md`), every token for both themes and nothing else. `src/styles/global.css` imports it, then carries `sentient-horizons/design/shell.css` copied unchanged (version noted at the marked line), then this site's own rules. There is no backdrop: the chart on the home page is the picture.
- `src/components/Spread.astro` is the trunk's picture, the spread of escape years, drawn at build time from the headline in `records.json`: five-year bars, the middle estimate as a rule, the fixed promised date as a dashed line in the second mark, the nine-in-ten span as a bracket, the not-this-century share at the edge. Nothing on it is drawn by hand.
- `src/layouts/Base.astro` and `src/components/Nav.astro` are the standard's shell: theme script, two-tier top bar with short handles, four-line footer, then the medical notice John ruled on 2026-10-16, then the family line. `src/components/StageBadge.astro` is The Upgrade Tree's stage pill, copied.
- `src/lib/records.ts` types the JSON that `scripts/export.py` writes to `src/data/records.json` at build time (not committed): every record in full with its links resolved to names and addresses, the computed headline from `data/headline.json` with a worked run added, the story entries and the changelog's days. Every page reads from it; nothing in the browser touches the TOML records, and the export script is the only reader of the data.
- **The headline file is served from the site as well as from the repository.** Every time `scripts/export.py` runs, which is before every `dev` and every `build`, it copies `data/headline.json` byte for byte to `public/data/headline.json` (not committed; listed in `.gitignore` beside the export's JSON), and Astro ships `public/` into `dist/` as it is, so `dist/data/headline.json` goes out with every deploy and answers at outrunningageing.com/data/headline.json. The weekly reading's publish step exports before it builds, so the served copy carries the newest numbers; when there is no computed headline the copy is removed and the address answers like any missing page. The method page links to it under the chart. Adopted 2026-10-17 from the Sentient Horizons lessons review of the same day (lesson 1, the notes); three tests in `scripts/test_compute.py` cover the copy.
- `public/robots.txt` allows crawling and names no sitemap. Until 2026-10-17 it promised one "with the first full version"; the full version went live without one, so the promise was removed (the lessons review's fault 3 for this site) rather than a sitemap added, since every page is reached from the home page and the top bar.
- `worker/redirect.js` runs in front of the static files and sends www.outrunningageing.com, outrunningaging.com and www.outrunningaging.com to the same page at outrunningageing.com with a permanent redirect.
- `wrangler.jsonc` names the worker and carries the four custom-domain routes.

## Commands

    npm ci              install (once)
    npm run dev         export the records and serve locally
    npm run build       export the records and build into dist/
    npm run deploy      build and deploy by hand (needs wrangler logged in)

Every push to `main` that touches `data/`, `scripts/`, `site/` or the changelog runs `.github/workflows/deploy.yml`, which validates, tests, builds and deploys. Preview address: outrunningageing.jfredson.workers.dev.
