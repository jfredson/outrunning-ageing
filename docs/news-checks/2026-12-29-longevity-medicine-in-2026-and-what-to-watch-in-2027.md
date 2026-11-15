# The year-end post for 2026: sources and checks

The post: `site/src/content/news/2026-12-29-longevity-medicine-in-2026-and-what-to-watch-in-2027.md`,
a "year in review" post (the kind John ruled on 2026-11-15, `docs/news.md`), drafted
2026-11-15 and dated for the publishing week John set (2026-12-28 to 2026-12-31). **Not published.**
It sits on its own branch and pull request, and John approves it first (tracker pattern, rule
4.18). Merging it deploys the site, but the post, dated 2026-12-29, stays off every page until a
build on or after that day. Every entry it names shows a dated change in 2026, as the kind requires.

## Promotion gate

`python3 scripts/compute.py validate` on 2026-11-15: "0 claim(s) marked to verify", every record valid.
But the weekly reading of 2026-11-15 carries 34 items left for John's decision, among them the two
Japanese approvals of 2026-03-06 that the post's first section is about. The post says plainly that
the decision is not yet made. If John rules before publishing, the third paragraph of that section
must be rewritten to say what was decided, and the post may then be about a change to the records as
well as a story.

## Facts, each against its source (all opened 2026-11-15)

- **Sumitomo Pharma, 2026-03-06** (https://www.sumitomo-pharma.com/news/20260306.html): conditional and
  time-limited approval in Japan "as of March 6, 2026"; dopamine-making nerve cell precursors grown from
  donor iPS cells; for Parkinson's disease with an inadequate response to existing drugs; "the world's
  first iPS cell-derived regenerative medicine".
- **Cuorips, 2026-03-06** (https://cuorips.co.jp/news-en/20260306): conditional and time-limited
  approval from Japan's health ministry; heart-muscle cell sheets from donor iPS cells; "patients with
  severe ischemic heart failure who have exhausted conventional treatment options"; "the world's first
  approved therapy using cardiomyocytes derived from iPS cells for the treatment of heart failure".
- **Cuorips, 2026-10-01** (https://www.cuorips.co.jp/news-en/200261001): insurance cover from
  2026-09-01; first insured operation 2026-09-29 at Osaka Police Hospital. The English news list
  redirects to plain http; the notice itself answers on https.
- **Sumitomo Pharma's results presentation, 2026-10-30**
  (https://www.sumitomo-pharma.com/news/assets/pdf/eir20261030.pdf, read as text): first transplant in
  the post-marketing (phase 4) study at Kyoto University Hospital in October 2026; about 1 to 2 patients
  in its financial year 2026, about 10 in 2027, 10 to 20 in 2028; priority to study patients, wider use
  after the study. The post says "its next financial year" rather than giving months, because the
  document does not say when the year starts.
- **Ace Alzheimer Center Barcelona, 2026-04-27**: 71 patients completed the 15-month programme; "under
  routine clinical practice conditions".
- **Life Biosciences, 2026-06-09 and 2026-10-08**: first patient dosed in a phase 1 trial in glaucoma
  and NAION; three glaucoma patients, no dose-limiting toxicity or serious adverse events through day 56;
  visual-field improvement in 2 of 3, which the company calls "preliminary signals"; escalation to the
  second dose level. The register (NCT07290244, through its data interface): 18 planned, primary
  completion 2027-05, completion 2032-03.
- **COSMOS clock paper** (https://doi.org/10.1038/s41591-026-04239-3): the journal's page asks for a
  sign-in; the abstract was read through Europe PMC's data interface (PMID 41803341): prespecified,
  958 participants, PCGrimAge −0.113 and PCPhenoAge −0.214 years a year, cocoa no effect, "small
  effects". The points about five clocks without correction and likely false positives are from the
  full-text reading of 2026-10-19 recorded on the entry. "Older adults" rests on that entry's
  description (about 70 on average). COSMOS register entry NCT02422745 confirmed by data interface.
- **Koning and others** (https://doi.org/10.1038/s42255-026-01643-4): abstract through Europe PMC (PMID
  42823536): phase 2, 31 people, 47 against 7 per cent, "proof-of-principle". The dropouts and the
  least-favourable count (P = 0.068) are from the full-text reading of 2026-10-20 recorded on the
  paper's record.
- **ZEUS**: the journal's page refuses automated visitors; figures from the American College of
  Cardiology's report and Mass General Brigham's release, as in the ZEUS post. HERMES closed: Novo
  Nordisk's report of 2026-11-04 on the securities regulator's site ("ZEUS and HERMES did not meet the
  primary endpoint"; the closure is in the record's reading of the same document).
- **Metformin frailty trial** (https://www.medrxiv.org/content/10.64898/2026.07.27.26359055v1, a
  preprint; abstract read through Europe PMC): 145 people, about 72; no difference on the Fried score
  without the weight-loss item; frailty index and two clocks slightly slower.
- **TAME**: the archived sponsor page of 2026-07-04 reads "Raising Funds to Launch".
- **Reagan-Udall Foundation meeting summary** (read as text): meeting held 2026-05-27; "no FDA-approved
  pathway currently exists for an aging indication"; "no validated aging biomarker".
- **The site's numbers**: `data/headline.json` (computed 2026-11-09): 2058; 4.27 per cent before 2050;
  first run 2026-10-16 at 2.66 per cent; the October 17th runs at 3.35 and 4.09; ends at 2035 (lag 3)
  and 2095 (lag 15); the two slowest groups at 2044. Most-likely years changed since launch: six, five
  later (chromosome-end drug, joint surface, weight-loss drugs' wide use, insulin cells, anti-inflammatory
  wide use) and one earlier (cataract drops).
- **2027 items**: ARTEMIS register entry (NCT06118281: about 10,000, active and not recruiting, primary
  completion 2027-01-29) and Novo Nordisk's release of 2026-07-31 (first half of 2027); Scribe
  Therapeutics' report of 2026-11-12 on the securities regulator's site ("initial clinical data expected
  in the first half of 2027" for STX-1150); Loyal's release of 2026-01-13 as carried by Yahoo Finance
  ("apply for XCA next year") and its page for vets (manufacturing section and conditional approval "In
  progress"); the Loyal claim of 2025-02-26 in the claims log; the San Antonio trial (NCT07923630: phase
  2, 1,200, "Aging", start 2027-01, primary completion 2030-12, collaborator the Department of Health and
  Human Services).

## Link what you name (rule 4.17)

Opened 2026-11-15 and answering: Sumitomo Pharma and Cuorips home pages; Wikipedia on induced
pluripotent stem cells, dasatinib and metformin; Ace Alzheimer Center Barcelona; Life Biosciences; the
COSMOS register entry; Novo Nordisk; the Reagan-Udall Foundation; Scribe Therapeutics; Loyal; UT Health
San Antonio. Kyoto University Hospital is linked to its Wikipedia article; the Osaka hospital is not named in the post. ER-100, STX-1150, ARTEMIS and TAME are linked through their own source in the same
sentence. Intellia's home page refuses automated visitors (it was dropped from the post with its item).

## Plain reading pass

No internal words (node, leaf, rung, scan, ledger, schema, settler); "hallmark", "senolytic" and
"epigenetic" not used. Dates in prose month-first with ordinals, as in John's edits to the ZEUS post. No
tool named. No line on who decided or what waits for whom; the open decision is said in the first
person. `scripts/check_site.py` on a full build: no note addressed to John.

## Not done

The cold-reader check (the lay read) is for John. The share kit is not written.
