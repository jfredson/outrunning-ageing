# The weekly sweep: the field's news read by date, in its own run

Written 2026-11-09. This is the standalone instruction for a second scheduled run, which does only the
field-wide sweep of `docs/weekly-reading.md`, step 1a part D, one hour before the weekly reading. A fresh
session with no memory of any earlier conversation follows it from top to bottom.

**Why it is its own run.** The cloud search tool allows about 200 web searches in a run, shared by the
main session and all its helpers. On 2026-11-09 the first reading under the fixed briefs
(`data/scans/2026-11-09-2.toml`) used that allowance up part-way: 30 of 85 records had fewer web searches
than the procedure asks, and the sweep ran only two, so its searches of the press-release sites by kind
of event were not run. The comparison of 2026-11-09 (`docs/readings/model-comparison-2026-11-09.md`)
found that the sweep accounts for most of what a reading finds. John ruled the same day: "Split into two
runs". The sweep now has an allowance of its own, and so do the record readers. Whether the allowance is
counted for each run or across the account for the day has not been tested; if this run or the reading
after it is still cut short, it says so under "Limits that cut" and the question goes back to John.

## What this run may and may not do

It writes one file, `docs/readings/sweeps/YYYY-MM-DD.md`, and publishes it. It edits no record, no other
document and nothing under `data/` or `site/`. It moves nothing and logs no publication; the weekly
reading does that, from this file, after opening each source itself.

## The procedure

1. **Orient.** Get the date in John's time zone: `TZ=America/Los_Angeles date +%F`. `cd` into the
   repository and run `git fetch origin && git checkout -B main origin/main`. The window is the one the reading
   will use: it starts seven days before that date and ends on it, both ends included (a sweep on
   2026-11-15 covers 2026-11-08 to 2026-11-15). The test sweep of 2026-11-09 started a day late, on
   2026-11-03, because this sentence was unclear. Read `CLAUDE.md` at the
   root and `docs/reading-briefs/sweep.md`.
2. **Sweep.** Follow `docs/reading-briefs/sweep.md` yourself, word for word, as the reader it addresses,
   with the window filled in, the repository's path, and the output file
   `docs/readings/sweeps/YYYY-MM-DD.md` (add `-2` if that file already exists; a sweep file is never
   edited after it is published). The brief's rule that you edit nothing in the repository gives way in
   one place only: this output file. You may share the sources among helpers, each given the whole brief
   and told which of its sources are theirs; a helper writes only a working file outside the repository,
   and you open every story a helper lists before it goes into the sweep file.
3. **Spend the web searches where only they will do.** The registry, the paper database and the listing
   pages are read with `curl` and cost no search. Start with the filings site's own dated search, which the brief describes and which also costs no
   search (added 2026-11-09, with John's yes, because the test sweep showed that web searches do not
   find company announcements that are only days old). Then run the web searches of the press-release and filings
   sites by kind of event (topline results, did not meet primary endpoint, discontinued, first
   patient dosed, approval, each with the month and year), then the results releases of the large
   companies the records name, then the meetings. If the allowance runs out, say what was not searched.
4. **Head the file.** Before the brief's sections, the file starts with: a title with the date; one
   paragraph giving the window and counts (paper titles returned and read,
   trials first posted that were read, web searches run, pages opened, stories listed).
5. **Publish.** One command:

       python3 scripts/publish.py --push \
         --message "YYYY-MM-DD: weekly sweep, N stories" \
         --fallback-branch claude/sweep-YYYY-MM-DD

   If the push to main is refused the command parks the commit on the fallback branch and says so;
   report the branch and do not retry. The commit message carries no relative date.
6. **Worklog.** If the Time-Assembler connector is reachable, one `progress` entry on the project
   "Outrunning Ageing" (id `50c51ff2-08c5-40de-a8ca-f46b8fd9f8f2`), `repo = "outrunning-ageing"`, titled
   "Weekly sweep YYYY-MM-DD: N stories", with the five most important stories and the limits that cut.
7. **Report.** A short numbered list and nothing else: the five most important stories, each with its
   date and what it bears on; then the counts; then the limits that cut.

Plain language, UK spelling, absolute dates, and no bare ids: a treatment is named in words with its id
beside it.

## The routine

Name "Outrunning Ageing weekly sweep", Sundays at 05:00 Pacific
(`CRON_TZ=America/Los_Angeles 0 5 * * 0`), one hour before the weekly reading, on the same cloud
environment, tools, connector and model (`claude-fable-5-2`) as the reading's routine. The hour is the
session's choice: the reading of 2026-11-09 took 26 minutes with the sweep inside it, so an hour leaves
room; if a sweep is ever still running at 06:00 the reading falls back as part D says. (The test sweep
of 2026-11-09 took 12 minutes. It ran straight after a reading that had used up its allowance and still
had its own, so the allowance is counted for each run. It used 28 searches and left about 170, because
the search tool returns little that is only days old and the press-release sites refuse the cloud
machine: more searches do not find the company announcements, and another road to them is still needed.) The routine's id
is recorded in `docs/weekly-reading-prompt.md`.
