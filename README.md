# Outrunning Ageing

Every year you live, medicine gets a little better. Right now it does not get better fast enough: for a person in middle age, the years they can expect to have left fall by about a year every year, less the small gains new treatments add. "Longevity escape velocity" is the name for the moment that stops being true: the point when medicine adds more than a year of healthy life for every year that passes, so that someone who keeps up with the best available care finds their remaining life expectancy holding steady or rising instead of falling. The phrase borrows the rocket's idea of a speed at which you stop falling back.

Outrunning Ageing (outrunningageing.com; outrunningaging.com, the American spelling, forwards to it) is a public tracker for the question **when, if ever, does the rate of repair overtake the rate of ageing?** It does for that question what The Belt Equation does for a settled solar system and The Quiet Galaxy does for the empty sky: it takes a question people file under science fiction, or under marketing, and breaks it into pieces anyone can argue about, with a number at the top that is computed from the pieces and never chosen by hand. It also keeps a dated record of who promised what and when, and holds those promises against what has actually been shown.

**Where it stands on 2026-10-17.** The site has been live at outrunningageing.com since 2026-10-17, after a holding page on 2026-10-16, in its own skin, "Ledger" (paper and ink with a clinical blue). The headline, computed on 2026-10-17, is **2058**, with a 3.4 per cent chance before 2050 and no run after 2100; nine runs in ten land between 2050 and 2068. The record holds 8 branches, 44 treatments and tools (5 already in the clinic), 31 claims, 9 self-experiments, 51 publications and 1 weekly reading, and no statement still marked to be checked against a source (the last 76 were sourced or removed on 2026-10-17). The weekly reading runs on Sundays at 06:00 Pacific; the first was run by hand on 2026-10-17 and the first unattended run is due 2026-10-18. The newest entry in `CHANGELOG.md` says what changed last and what is left for the author to rule on. This paragraph is rewritten, with its date, whenever one of these facts changes.

## The headline

Three numbers, computed from the records and never typed in:

1. **The year.** The middle estimate of the year escape velocity arrives under the project's current estimates, shown with its spread: "2058, and anywhere from 2050 to 2068", as computed on 2026-10-17. The computed file is `data/headline.json`, and the site serves the same file at outrunningageing.com/data/headline.json.
2. **The chance it arrives before 2050.** A fixed, stated date, chosen because the loudest promises on the claims log all land before it. The date is a project constant, changed only at a yearly review and logged when it changes.
3. **Beside them, the share of runs in which it does not arrive before 2100**, said in public as "not this century". This is the honest width of the argument.

How they are computed: every leaf (a specific treatment, result or measuring tool, see below) carries the project's estimate of the year it reaches the clinic, as a range with the reasoning beside it. The compute script plays the tree out many thousands of times. In each run it draws a year for every leaf, works out the year each branch counts as handled, takes the latest handled year across the branches marked required, and adds a drawn lag for the treatments to spread from the clinic to ordinary people. The year that comes out is that run's escape year; the middle of all the runs is the headline. The method, with every parameter proposed and its alternative, is in `docs/method.md`.

## The tree

Eight branches, fixed, changed only at a yearly review. The published science groups ageing into twelve "hallmarks" (López-Otín and colleagues, 2013 and 2023); seven of the branches group those twelve into kinds of damage that repair would have to address, and the eighth is for proving that anything works:

| branch | what it covers |
|---|---|
| Worn-out cells | cells that have stopped dividing but will not die, and poison their neighbours |
| Damaged DNA | mutations and shortened chromosome ends |
| The cell's settings | the marks that tell a cell which genes to read, which drift with age |
| Broken proteins and waste | misfolded proteins, failed recycling, waste that builds up inside and between cells |
| Energy and fuel sensing | the cell's power plants and the pathways that sense food |
| Replacing lost cells and parts | stem cells that run out, tissue not replaced, organs that fail |
| Inflammation and the body's messaging | low-grade chronic inflammation, the gut's microbes, the signals cells send each other |
| Measuring ageing | the tools that say whether any of the above worked without waiting decades |

Under each branch hang **leaves**: one specific drug, procedure, gene therapy or accepted measurement that would have to arrive. Every leaf has a plain name, a test of what would count (written so that two readers agree), who settles it, a stage on the same five-rung ladder The Upgrade Tree uses (idea only, shown in animals, first human, in clinical use, in wide use), the project's estimate of when it reaches the clinic, and a dated record of every change. Five leaves are shared with The Upgrade Tree's lifespan-and-repair branch and the two records point at each other.

## Six kinds of record

The data is the project. Six record kinds, each a plain-text TOML file per record under `data/`, laid out so a change shows as a one-line diff:

1. **Branches** (`data/branches.toml`): the eight, in order, with the hallmarks each groups and the rule for when it counts as handled.
2. **Leaves** (`data/leaves/`): described above; one file per leaf, named for its id, which is also its page address and is never renamed.
3. **The claims log** (`data/claims/`): who said what about when, with the primary source, what it commits to, and a verdict filled in as dates pass. It sits beside the headline and moves no number.
4. **Other people's public self-experiments** (`data/experiments/`): who, what they do, what they measure, what they claim, what the public record shows. A claim about one person is a story, not a record, and it moves no leaf.
5. **The publications log** (`data/papers/`): append-only and dated, each entry saying which leaf or branch it bears on and whether it moved anything.
6. **The weekly reading** (`data/scans/`): every leaf, every claim and every self-experiment read against the week's news once a week, with the searches made and a verdict per record, including the weeks when nothing moved. The reading may move a leaf one rung on a record of the kind the leaf itself names and may log a paper; everything else it leaves for the author. How it runs, with every choice and its alternative, is in `docs/weekly-reading.md`; the scheduled task's prompt is `docs/weekly-reading-prompt.md`. It runs as a scheduled task on Sundays at 06:00 Pacific; the first reading was run by hand on 2026-10-17, and the first unattended run is due 2026-10-18.

The record layout and the rules the validator enforces are in `docs/record-schema.md`.

## Layout

- `docs/` holds the plans and definitions. `docs/2026-10-16-kickoff.md` is the original outline, kept as the record of where the project started. `docs/record-schema.md` is the record layout. `docs/method.md` is how the headline is computed. `docs/weekly-reading.md` is how the records are read against the news each week, and `docs/weekly-reading-prompt.md` the scheduled task's prompt.
- `data/` holds the records (above).
- `scripts/compute.py` validates the records (`validate`) and computes the headline (`run`). `scripts/test_compute.py` tests it. `scripts/export.py` turns the records into the JSON the site reads. `scripts/publish.py` validates, tests, exports, builds and, with `--push`, commits and pushes main in one command, parking the commit on a fallback branch when the push is refused. Plain Python, standard library only.
- `site/` is the website: Astro, fully static, on the Sentient Horizons design standard in the site's own skin, "Ledger", served from Cloudflare Workers. The build also serves the computed headline file at outrunningageing.com/data/headline.json (since 2026-10-17; `site/README.md` says how).
- `CHANGELOG.md` has a dated line for every change to the records or the site.

## Deploying

Every push to `main` that touches the records, the scripts or the site runs `.github/workflows/deploy.yml`, which validates, tests, builds and deploys to Cloudflare Workers. It needs two repository secrets, `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. The holding page went live this way on 2026-10-16, and the full site on 2026-10-17. By hand from a machine with wrangler logged in: `cd site && npm ci && npm run deploy`. `site/wrangler.jsonc` carries the custom domains; `site/worker/redirect.js` forwards www and the American-spelled address to outrunningageing.com.

## Licences

The data under `data/` is free to reuse with credit under Creative Commons Attribution 4.0 (`LICENSE-DATA`). The scripts and the site are under the MIT licence (`LICENSE`).

## A note on what this is not

The site records what has been shown and what has been promised. It recommends nothing, and nothing on it is medical advice. The author's own health record is not part of it.

## Author

John Fredrickson. A Sentient Horizons project, kicked off 2026-10-16.
