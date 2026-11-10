# Trial of a deeper weekly reading on a stronger model (2026-11-09)

Run on 2026-11-09 in a Claude Code session on John's Mac, on his go ("Run the trial"), on the branch
`claude/fable-trial-reading-2026-11-09`. Nothing was published: no record, reading or page on the site
was changed, and the branch was not pushed. The readers' raw output is in
`docs/readings/fable-trial-2026-11-09/`. This is a working document, so it uses the project's own words.

## The question

John asked how the weekly reading could find the most important stories, so that the site can carry
regular news posts and the estimates can be revised when the news bears on them, and whether the new
model Fable 5.2 would do it better. Two things were tested, kept apart on purpose:

1. **The model.** The scheduled readings of 2026-11-01 and 2026-11-08 ran on Sonnet 5.5 (the routine has
   no model set; the run log shows `claude-sonnet-5-5`). The control here repeats the existing procedure
   on Fable 5.2 for the 45 treatments, for the week 2026-10-25 to 2026-11-01.
2. **The design.** The deeper design, also on Fable 5.2, read all 85 records for 2026-10-25 to 2026-11-08
   in one pass. It reads dated sources first (the trial registry's data interface filtered by
   last-updated date, and Europe PMC filtered by publication date), then searches the web, opens every
   in-window result that may bear on a record, and reports results that count against a treatment. One
   more reader swept the field's sources by date without starting from the records.

## The numbers

| | Sonnet 5.5, existing procedure (two scheduled readings) | Fable 5.2, existing procedure (control, treatments, one week) | Fable 5.2, deeper design (all records, two weeks in one pass) |
|---|---|---|---|
| Record readings | 170 (85 a week) | 45 | 85 |
| Quiet | 167 | 33 | 41 |
| Noted | 1 | 2 (1 on web searches alone) | 21 |
| Flagged for John | 2 | 10 | 13 |
| Bears on an estimate | no such verdict | no such verdict | 10 |
| Pages opened, by the readers' own lists | about 10 over two weeks | 43 | 230 |
| Findings dated in the window that the records lack | 1 logged | 1 | 123 (101 from a page that was opened; 26 count against a treatment) |
| Rough size of the run | about 0.8 million tokens a week, five minutes | about 0.8 million tokens, four minutes | about 2 million tokens, eleven minutes |

On the same 45 treatments in the same week, Sonnet 5.5 gave 43 quiet, 1 noted and 1 flagged.

## What each arm found

**The model alone changes how hard the reader looks, not what it can see.** On the existing procedure,
Fable 5.2 opened about eight times as many pages as Sonnet 5.5 and flagged ten older records the entries
lack, several of them trials that failed (an April 2026 rapamycin trial alongside exercise, two NAD
supplement trials). But it found nothing dated in the week except one company's results release, and it
missed both things the week is now known to have held: the danazol trial results posted on 2026-10-27
and Acumen's announcement of 2026-10-30.

**The design is what finds the week's news.** Checked by this session against the registry, the papers'
registration records or a web search (not just taken from a reader's report):

| Date | What | Checked against | Sonnet 5.5 readings |
|---|---|---|---|
| 2026-10-27 | The registry posted results for the low-dose danazol trial and changed it to stopped early for too few patients (18 enrolled). The records call it completed. | Registry record NCT03312400 | Quiet both weeks |
| 2026-11-02 | Vertex put its effort into a successor to the insulin-making cell therapy the entry is built on, with late-stage trials in 2027. | Web search; one third-party summary. The company's own release was not opened by this session. | Quiet |
| 2026-11-05 | A study of kidney transplant recipients found no gain in length of life on rapamycin. Three readers found it independently. | Crossref record of the paper | Not mentioned |
| 2026-11-06 | A 1,200-person trial of two existing drugs against placebo, with healthy ageing as the aim, was first registered. The site has no record for it. Two readers found it independently. | Registry record NCT07923630 (arms: semaglutide, dapagliflozin, placebo) | Could not be found: no record to search from |
| 2026-11-07 | The full results of the 6,376-person trial of an inflammation-only heart drug were published and presented: no fewer heart attacks or strokes. Two readers found it independently. | Web search (several outlets). The journal page was not opened. | Quiet |
| 2026-10-30 and 2026-11-03 | Two new trials registered with a marker of ageing as the main measure. | Registry records NCT07906041 and NCT07912164 | Not mentioned |
| 2026-11-05 | A metformin-against-ageing trial in 166 people without diabetes, results posted 2026-07-02 with no effect on either main measure, entry updated in the window. | Registry record NCT04264897 (p 0.576 and 0.88) | Not mentioned |

Older facts the records lack, also checked: Japan's health ministry gave conditional, time-limited
approval on 2026-03-06 to two treatments made from stem cells, one for Parkinson's disease and one for
heart failure (web search, several outlets). Whether a conditional approval meets a test worded "a
regulator approves" is John's ruling, on two entries.

Reported by a reader and not checked by this session: a death in a first human trial of an in-body gene
editor (the paper exists in the journal Cell, dated October 2026; the death was not confirmed here);
that two sister trials of the heart drug were stopped (sources disagree); the many "noted" animal papers.

## What the deeper design still missed

**Acumen's announcement of 2026-10-30** (its amyloid antibody missed its main measure and development
stopped; confirmed here by a web search) was caught by no reader in this trial: not the amyloid entry's
reader, not the field-wide sweep, not the control. The reasons are plain. The entry names the approved
antibodies, not Acumen's. The registry entry did not change in the window and no paper exists. The
sweep could not open STAT or Fierce Biotech, which refuse automated readers even from the Mac. The
announcement was a company release on a newswire. So the dated sources need one more: the newswires
(GlobeNewswire, Business Wire, PR Newswire) searched by date and by each entry's kind of treatment, not
only by the names in its notes.

## Other limits and faults of the trial

- **A safety filter stopped one reader.** Fable 5.2 carries extra safety measures on subjects that could
  be misused. The reader for the worn-out-cells and damaged-DNA treatments finished its reading and was
  stopped while writing its results, which were lost. Two smaller readers, told to save after every
  record and to keep to news-level wording, reread the group and both got through. A scheduled run on
  this model needs both habits and a retry, or it will sometimes publish an incomplete reading.
- **The comparison is not like for like.** The deeper design read two weeks in one pass, knowing nothing
  of the earlier readings, on a Mac that can open pages the cloud routine cannot. Some of its gain over
  the scheduled readings comes from the Mac, not the design or the model.
- **The blinding had a hole.** The publications folder already held the Alnylam release that the reading
  of 2026-11-01 logged, so readers could see one thing an earlier reading found.
- **One control reader stepped outside the existing procedure** with one dated query to Europe PMC, and
  said so; that record is counted as quiet on web searches alone.
- **Volume.** 123 in-window findings in two weeks is far more than John can rule on. Most are neutral
  (sales figures, animal papers, registry housekeeping). Only about ten were checked by this session.
  The false-alarm rate of the rest is not known.
- **Three records in one group got one web search each,** not two.

## What follows, for John to rule

Nothing here is applied. In order of how much the trial supports each:

1. **Dated sources first, in the procedure.** The registry by last-updated and first-posted date, Europe
   PMC by publication date, and (from the Acumen miss) the newswires by date. This is the change that
   found the news; the model alone did not.
2. **A place for results that count against, and for what bears on an estimate.** Ten such items in two
   weeks, each written as which way it cuts and why. The ruling stays John's.
3. **A field-wide sweep each week,** so that a story with no record (the new healthy-ageing trial) can be
   found, and a ranked shortlist of story candidates at the end of each reading. Regular news posts also
   need a post kind that rests on a logged publication without a record change, which changes John's
   rule of 2026-10-18.
4. **A filter between the readers and John.** With this much found, the assembling reader must rank and
   cut, and a miss check by a non-Claude model each month would measure what is still missed.
5. **The model.** Fable 5.2 read more carefully on either design, but costs more and can be stopped by
   its safety filter on this subject. Whether the cloud routine accepts it is untested. A cheaper test
   worth running before deciding: the deeper design on Sonnet 5.5, to see how much of the gain the
   design gives on its own.
6. **The backlog.** The trial turned up about twenty older facts the entries lack (the two Japanese
   approvals, the failed NAD and metformin trials, the danazol status). They want a dated batch, as the
   first reading's nineteen did.

## Added the same day: the deeper design on Sonnet 5.5

On John's go ("Run it on Sonnet"), the deeper design was run again on Sonnet 5.5: the same briefs, the
same groups of records, the same window (2026-10-25 to 2026-11-08), nine readers. These readers worked
from a fresh copy of the records and their own folder, so they could not see the Fable 5.2 results or
this write-up. Their raw output is in `docs/readings/fable-trial-2026-11-09/deeper-design-sonnet/`.

| | Deeper design, Fable 5.2 | Deeper design, Sonnet 5.5 |
|---|---|---|
| Quiet | 41 of 85 | 65 of 85 |
| Noted | 21 | 14 |
| Bears on an estimate | 10 | 4 |
| Flagged for John | 13 | 2 |
| Pages opened, by the readers' own lists | 230 | 91 |
| Findings dated in the window that the records lack | 123 (26 against a treatment) | 61 (6 against a treatment) |
| Records scored worth a news post | 14 | 3 |
| Stories in the field-wide sweep | 23 | 16 |
| Rough size of the run | about 2 million tokens, eleven minutes | about 1.2 million tokens, five minutes |
| Readers stopped by a safety filter | 1 of 8, reread by two smaller readers | none |

The same checklist, scored from the output files (a word search of each run's files, then read):

| Story | Fable 5.2 | Sonnet 5.5 |
|---|---|---|
| Danazol trial results posted and status changed, 2026-10-27 | found | found |
| Vertex's change of course, 2026-11-02 | found | found, from the company's own exhibit |
| Rapamycin and length of life in transplant recipients, 2026-11-05 | found, by three readers | found, by one |
| Full results of the inflammation-only heart drug trial, 2026-11-07 | found | found |
| Negative metformin trial in 166 people (entry updated 2026-11-05) | found | found |
| New trial of gut microbes on an ageing clock, registered 2026-11-03 | found | found |
| NAD supplement trial highlighted 2026-11-06 | found, by a record reader and the sweep | found by the sweep only; the entry's own reader did not attach it |
| New 1,200-person healthy-ageing trial, registered 2026-11-06 | found, by two readers | missed |
| New trial of a weight-loss drug on a brain-age measure, registered 2026-10-30 | found | missed |
| Japan's conditional approvals of 2026-03-06 (older than the window) | found | missed |
| Account of resetting genes given outside any trial (older than the window) | flagged | missed |
| Acumen's announcement of 2026-10-30 | missed | missed |

**What this shows.** With the dated sources in front of it, Sonnet 5.5 found seven of the nine checked
stories dated in or highlighted in the window, against the scheduled readings' none. So most of the gain
comes from the design. What Fable 5.2 adds is the wider look: it opened two and a half times as many
pages, found the two stories that had no record to start from, weighed ten items against the estimates
where Sonnet 5.5 weighed four, and turned up nearly all of the older facts the entries lack (thirteen
flags against two). Where a page failed to load, Fable 5.2 usually found another road and Sonnet 5.5
usually stopped and called the record quiet; its claims reader returned sixteen of sixteen quiet and
said its verdicts "rest on absence".

**Where Sonnet 5.5 was better.** No reader was stopped by a safety filter. On the claim that two sister
trials of the heart drug were halted, it noticed that the reports it opened disagree and marked the claim
unverified, where the Fable 5.2 reader reported it as a fact; a web search in this session found the same
disagreement. It also produced half the volume for John to rule on.

**Limits.** One run of each model, so some of the difference is chance. The same single leak applies to
both (the publications folder holds one release an earlier reading logged). The checklist was drawn from
what the Fable 5.2 run found and this session then verified, which favours Fable 5.2: a story only
Sonnet 5.5 found would not be on it. Reading the Sonnet 5.5 reports for such stories turned up small
ones only (two cartilage trial records updated 2026-11-05, a 26-person drug-combination pilot marked
completed 2026-10-30, a paper of 2026-11-05 on silencing one gene in human blood stem cells).

**What it means for the choice of model (for John to rule).** Three workable arrangements, cheapest
first: (a) Sonnet 5.5 on the deeper design every week, which already finds most of the week's news;
(b) the same, with Fable 5.2 for the field-wide sweep and the assembling reader only, since stories with
no record and the weighing against estimates are where it earned its cost; (c) Fable 5.2 throughout,
with readers that save after every record and a retry for one that is stopped. Either way the newswires
still have to be added, because neither model on this design caught the Acumen announcement. The
backlog of older facts is a separate, one-off job that suits Fable 5.2 and does not need a weekly run.
