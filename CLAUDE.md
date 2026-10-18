# Outrunning Ageing — instructions for Claude

These two rules come from The Belt Equation (`~/Code/belt-equation/CLAUDE.md`, where they
moved on 2026-10-12 from memory notes that had loaded for every project). They apply here
because this repository is built the same way: a public data-and-documentation project with
one author. The workspace `CLAUDE.md` in `~/Code` still applies on top, including plain
language everywhere, no bare ids without a plain label, and absolute year-month-day dates. A
commit hook (`.githooks/commit-msg`, turned on with `git config core.hooksPath .githooks`)
refuses a commit message with a month-name, slash or relative date.

## Commit on main and push

In an interactive session, commit on `main` and push at the end of each working session,
without asking. Ruled by John 2026-09-08 for The Belt Equation, after a background-job
session left a review commit on a side branch and asked him to merge it. The repository is
a public documentation-and-data project with one author, so a branch-and-merge step is a
chore with no review benefit.

Background-job sessions cannot push to `main`. If a task here runs as a background job,
say up front that the result will land on a branch, and open a pull request so the merge
is one click.

## Design

The site wears its own skin, "Ledger" (paper and ink with a clinical blue; ruled by John 2026-10-17
from the proposal in `sentient-horizons/design/proposals/outrunning-ageing-skin-2026-10-17.md`),
on the family's shared skeleton (design standard, section 3a). `site/src/styles/skin.css` holds
this site's tokens for both themes and nothing else; `site/src/styles/global.css` imports it, then
carries `sentient-horizons/design/shell.css` copied unchanged with the version noted, then this
site's own rules below the marked line. Never edit the skeleton here; update the copy when the
standard changes. Light is the default theme; there is no backdrop; the chart of the spread of
escape years (`site/src/components/Spread.astro`, read from the headline file) is the picture, and
stands on the paper between double rules as "Sheet I". Every colour is a token; data is coloured
with `--accent-3`; the sepia `--accent-2` marks the promised date and nothing else. No web fonts.

## Every design choice comes with confidence and an alternative

Ruled by John 2026-09-08. Before asking John to accept any design choice (a record field, a
method, a file layout, a name), give him, as a short table or list:

1. The choice.
2. How confident you are (high, moderate or low), with a sentence on why.
3. Whether it is standard practice or a judgment call.
4. The strongest alternative and what it would cost.

Flag any proposal you would change yourself on reflection. Nothing is settled until John
says so; a proposal that has not been ruled is written up as proposed, with the date, in the
document it belongs to (`docs/record-schema.md` for the record layout, `docs/method.md` for
the headline). Do not reopen what the kickoff document (`docs/2026-10-16-kickoff.md`)
already proposes, and John accepted on 2026-10-16, without saying why.

## Three things specific to this repository

- **Leaf ids are public addresses.** A leaf's `id` is the last part of its page address
  (`/leaves/drug-clears-aged-cells-from-a-person/`) and is never renamed once committed.
  Retire it in `data/retired.toml` and point at the replacement instead. The same holds for
  the branch keys, the claim, self-experiment and publication ids, which are anchors on their
  pages. The validator checks this against the repository's history.
- **Facts from memory are marked.** A claim written without checking it against a source
  goes in the record's `verify` list, and a later session clears it. The stage records, the
  ranges, the claims log and the publications log are only as good as their sources, and a
  quoted promise is only as good as the recording it came from.
- **Nothing about John's own health goes into the record without his ruling.** John ruled on
  2026-10-16 that his own track stays private in version one. The schema has no field for it,
  so it cannot arrive by accident; the self-experiments record is for other people's public
  self-experiments. If he rules a piece public, it enters that record by a dated entry under
  the same rules as everyone else's, and never otherwise. Nothing from the private Longevity
  project, the Health folder or the clinical encounters moves here.

## Public pages use no internal vocabulary

The Sentient Horizons design standard (section 1a, ruled by John 2026-10-08) applies: the
words "node", "leaf", "trunk", "scan", "ledger", "schema" and "settler" stay in `docs/` and
`scripts/`. On a public page a treatment is a treatment, a branch is a branch, the test is
"what would count", and "hallmark", "senolytic" and "epigenetic" each get their plain meaning
before the word, if the word is used at all. UK spelling throughout ("ageing"), as the kickoff
rules and as The Upgrade Tree's record already uses.

## No disclaimers, and no raw record text on public pages

John ruled on 2026-10-18 that the site carries no disclaimer of the "a record, not a guide"
or "not medical advice" kind, on any page or in the footer: nothing on it can be read as a
guide, since it is plainly a record of the science as it stands. That reverses kickoff
decision 9 (the one-line medical notice); the kickoff document is left as written. The same
ruling cut every line saying the author's own health record is not on the site. Do not add
either back.

He ruled the same day that anything on the public site is a public version of the internal
record, passed through a presentation he has discussed; git keeps the raw text and the site
does not show it. So the story page no longer prints `CHANGELOG.md`. Before showing any other
raw record text on a page, ask him.

Two more rulings of 2026-10-18 follow from it:

- **Record prose is written for visitors.** Notes, revision reasons, a claim's verdict reason,
  a publication's finding, and every line of a weekly reading except its search queries are
  printed on the site as written, so they are written for a visitor from the start: plain
  words, no internal names ("leaf", "settler", "session", "batch", "verify list"), no file,
  field or record ids, no ladder keys, no "item 13" or "the rulings document". A review is
  "an outside review on 2026-10-17 argued ... and John ruled ..."; another record is named in
  words. The full rule is "Writing for visitors" in `docs/record-schema.md`; the weekly
  reading follows it too (`docs/weekly-reading.md`, step 1). Every existing one was rewritten
  that way on 2026-10-18, wording only. The search queries stay as run.
- **No file names or version lines on public pages.** The pages do not say which file a record
  is or which commit the site was built from; the repository link in the footer is enough.
- **The story page's "what changed" section is built from the records' own flags only**
  (stage revisions, estimate-year revisions, papers' logged dates, the readings), one plain
  line per day, with "the site's wording changed" for a day with only wording changes. Nothing
  in it is copied from `CHANGELOG.md`.

## End of a session

Worklog entry on the TimeAssembler project "Outrunning Ageing" with `repo = outrunning-ageing`,
the roadmap kept to the next few real moves, a dated line in `CHANGELOG.md` for anything that
changed the record or the site, and the daily reflection, as the workspace `CLAUDE.md` says.
