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

## The medical notice

Every public page ends with the one-line notice John ruled on 2026-10-16: the site records
what has been shown and what has been promised; it recommends nothing, and nothing on it is
medical advice. It lives in the footer, above the family line, and no page drops it.

## End of a session

Worklog entry on the TimeAssembler project "Outrunning Ageing" with `repo = outrunning-ageing`,
the roadmap kept to the next few real moves, a dated line in `CHANGELOG.md` for anything that
changed the record or the site, and the daily reflection, as the workspace `CLAUDE.md` says.
