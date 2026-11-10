# The ZEUS estimate post: sources and checks

The post: `site/src/content/news/2026-11-09-zeus-moves-heart-estimate-later.md`, an "estimate revised"
post, drafted 2026-11-09 by Claude on John's ruling of that day. **Not published.** It sits on its own
branch and pull request; merging it to `main` deploys it, and John approves it first (tracker pattern,
rule 4.18). The checker allows it until 2026-11-23, fourteen days after the record's change.

## Which posts the rulings call for

- **Estimate revised:** yes. The heart-attack entry's estimate for wide use moved on 2026-11-09 from
  2027, 2032, 2050 to 2028, 2035, 2055 (commit `c3da8f0` on `main`).
- **Headline moved:** no. The rerun of 2026-11-09 gave 2058 and 4.27 per cent before 2050, the same as
  before, because the headline reads the year this treatment first reached patients (colchicine's
  approval in 2023), not its wide-use estimate.
- A point for John: rule 4.18 says a change is news when it moves a headline number, a stage, a count or
  a notable first, and this change moves none of them, only a range on one entry's page. John's ruling of
  2026-11-09 asked for the post all the same, so it is drafted; whether it goes out is his call.

## Promotion gate (rule 3.3, part 4)

`python3 scripts/compute.py validate` on 2026-11-09, after the change: "0 claim(s) marked to verify",
and a search of every record for a `verify` field found none. No record carries an open check.

## Facts, each against its source (opened 2026-11-09)

- The American College of Cardiology's report of the presentation
  (https://www.acc.org/latest-in-cardiology/articles/2026/11/06/14/37/sat-935am-zeus-aha-2026, dated
  2026-11-07): 6,376 people; monthly injection; median follow-up 33 months ("a little under three
  years"); 17.6 against 17.7 per cent for heart death, heart attack or stroke; presented at the American
  Heart Association's meeting and published the same day in the New England Journal of Medicine; patients
  with hardened arteries, chronic kidney disease and inflammation; about ten years older than the earlier
  trial's.
- Mass General Brigham's release (https://www.eurekalert.org/news-releases/1150801, 2026-11-07): Ridker
  led the trial; the drug lowered the inflammation signal but not events; the population was a decade
  older with kidney disease, diabetes and heart failure, and "the horse may already have been out of the
  barn" (paraphrased in the post, not quoted); the earlier trial of a drug on a similar pathway worked;
  colchicine "underutilized" (paraphrased as "not being prescribed as often as it should be").
- The paper itself (https://doi.org/10.1056/NEJMoa2612126): the journal's page showed a check for
  automated visitors and was not read. Its title, date (2026-11-07) and authors were read from the
  record the journal filed with Crossref, the DOI registry. The link is the paper's permanent address
  and opens for a person in a browser.
- Novo Nordisk's announcement of 2026-07-31 (opened 2026-11-09, page answers): the top-line result, and
  the two further trials in heart failure and after a heart attack due in the first half of 2027.
- Colchicine's 2020 trial (5,522 people, about a third fewer heart attacks and strokes), its approval of
  2023-06-16 and the 2025 colchicine trial with no benefit after a heart attack: all from the treatment's
  own record, whose approval link (the regulator's approval package) was opened and answers.

## Link what you name (rule 4.17)

Every first mention linked; each address answered on 2026-11-09: colchicine (Wikipedia); the ZEUS trial
(its registry entry, https://clinicaltrials.gov/study/NCT05021835, read through the registry's data
interface: "ZEUS", completed); Novo Nordisk (its home page); ziltivekimab (Wikipedia, "an investigational
new drug being developed by Novo Nordisk"); the American Heart Association (https://www.heart.org/, which
refuses automated visitors but is the official page); the New England Journal of Medicine (the paper's
DOI); Paul Ridker (Wikipedia, "a cardiovascular epidemiologist ... Brigham and Women's Hospital"); the
American College of Cardiology (its report). The earlier trial of a similar drug (canakinumab, 2017) is
described and not named, so it carries no link.

## Plain reading pass and voice

- No tool, model, file, field or record id named. No project vocabulary ("leaf", "rung", "settler",
  "branch", "headline") in the body; the treatment is "one of the treatments", the step is "wide use"
  explained in plain words in the second paragraph.
- "Antibody" glossed as "an antibody drug that blocks one of the body's inflammation signals";
  "inflammation" glossed in the first paragraph; "placebo" said as "a dummy injection".
- Every date says what happened on it: November 7th, 2026 for the results; November 9th, 2026 for the site's
  move; July for the company announcement; 2027 for the trials still running.
- The title names the site's change, not the trial as news. Rule 4.19: the post opens on the human
  question ("Can calming inflammation protect the heart?"), then the result, then why it matters. The
  closing line on the headline is kept because a reader of an "estimate revised" post would otherwise
  assume the site's main year moved.
- No em dashes, no tables, no headings of the old fixed shape. 622 words.
- `python3 scripts/check_news.py`: OK, 3 posts.

## Cold reader (`calibration-problem/editorial/cold-reader-protocol.md`)

- Ninety seconds: the question, then what inflammation is and why doctors suspect it, then the cheap
  drug that already works, then the failed trial. Attention would break first at "in wide use"; the
  second paragraph says what that means before the trial is told.
- Uninformed reader (John's father): "hardened arteries" and "weak kidneys" for the medical terms; the
  percentages given as people it happened to, so the near-tie is plain. "Antibody" still asks a little;
  glossed rather than replaced.
- Coinage budget: none. Closed loop: the body's links are mostly outside the site (the trial registry,
  the paper, the reports, Wikipedia); the treatment's page is linked for the reasons.
- Genre: a short news story with its sources in the sentences; nothing reads as promotion.

## John's edits (2026-11-09)

- The title and two sentences no longer make the site its own agent ("the site expects", "the site
  already counts", "what it still waits for"). John: it "makes the site its own agent, which is not
  the goal of the project". The title is now in his voice, with the news first: "A heart trial found
  no benefit, so I've moved my estimate for drugs that calm inflammation three years later".
- Dates in the post's prose and source labels are spelled "November 7th, 2026", John's rule for
  public prose (2026-10-21).
