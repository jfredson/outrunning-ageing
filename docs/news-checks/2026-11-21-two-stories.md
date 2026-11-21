# Two story posts of 2026-11-21: sources and checks

The posts:
- `site/src/content/news/2026-11-21-mouse-life-drugs-help-heavy-mice-most.md` (the mouse body-weight preprint)
- `site/src/content/news/2026-11-21-lecanemab-five-years-against-past-patients.md` (lecanemab at five years, with the Japan pen)

Both are "a story from the field" posts (`kind: story`, `docs/news.md`). They were drafted 2026-11-21 by Claude
on John's ruling of that day ("Story now, hold estimate"). **Not published.** They sit on their own branch and pull
request. Merging the pull request to `main` deploys them, and John approves them first (tracker pattern, rule 4.18).

## Which posts the rulings call for

- **The mouse preprint:** a story, with the estimate for a drug giving people extra healthy years held. The
  weekly reading of 2026-11-15 flagged the preprint as pointing that estimate later. On 2026-11-21 John ruled to
  tell the story now and hold the estimate until a version checked by other scientists is published. The post
  says the estimate has not moved, and says why. Moving that estimate would not move the headline year in any
  case. The energy-and-fuel branch is counted once two of its treatments are in the clinic, and the weight-loss
  drug for heart attacks is already there, with the dog drug estimated for 2028.
- **Lecanemab:** a story. The antibody entry's estimate for wide use turns on how many people are treated, and
  neither release gives a count. The Japan pen remains a flagged item from the reading of 2026-11-15 that bears
  on the wide-use estimate, towards earlier, and it is still open for John's ruling. The post mentions the pen as
  news and says the estimate is unchanged.

## Promotion gate (rule 3.3, part 4)

`python3 scripts/compute.py validate` on 2026-11-21: "0 claim(s) marked to verify", and a search of every
record for a `verify` field found none. No record carries an open check.

## Facts, each against its source (opened 2026-11-21)

**Mouse post.** The full text of the preprint was read on bioRxiv in the browser
(https://www.biorxiv.org/content/10.64898/2026.11.10.765234v1.full; bioRxiv refused the automated reader
with "too many requests", and Europe PMC gave the abstract and the date, 2026-11-11):
- 33,780 mice in the Interventions Testing Program; a preprint that has not been peer reviewed.
- Males, weight-lowering experiments: median gain 6.2 per cent in the lightest pre-dosing quarter, 20.2 per cent
  in the heaviest (the abstract says "among those experiments"; the post says "male mice given a drug that also
  lowered their weight"). Medians: lightest 890 to 945 days; heaviest 673 to 809 days. Heavy treated mice still
  died earlier than light untreated mice (809 against 890 days).
- 13 of 14 compounds showed the same ordering, "including ... rapamycin". In the lightest quarter, acarbose,
  rapamycin, canagliflozin and 17α-estradiol still raised median life by 6–8 per cent, against 21–25 per cent in
  the heaviest (the post says "rapamycin and three other drugs").
- Females weak, "possibly because" the programme's untreated females outlived every non-programme female
  control group sampled. The effects "may" be less apparent in metabolically healthier mice or humans: the
  authors' hedge, kept as a hedge in the post.
- Mice fed freely: the title says "ad libitum-fed", and the programme's own page describes the testing.
- The 2009 rapamycin paper (https://doi.org/10.1038/nature08221) opened: title and journal as in the sources line.

**Lecanemab post.** The joint Eisai and Biogen release of 2026-11-17 was read on Eisai's site
(https://www.eisai.com/news/2026/news202663.html). Biogen's copy (https://investors.biogen.com/node/31156)
refused the automated reader with 403, so the post links Eisai's copy.
- CTAD, the 19th, Boston and online; Clarity AD 1,795 people (898 and 897), 18 months; 95 per cent continued;
  351 received five years of continuous treatment.
- Against ADNI: −2.05 points on CDR-SB at five years; against BioFINDER −2.54. Progression 61.9 against 77.5 per
  cent (ADNI). CDR-SB stages run to 18.0 (the release's footnote), so "a scale from 0 to 18".
- Brain swelling (ARIA-E): 13.5 per cent in the first 12 months, then 3.6, 1.1, 1.3 and 0.6 per cent.
- Low tau: 62 per cent improved on CDR-SB; the release gives no count of people.
- The release's own limit: "assessments were conducted at relatively long intervals and control-group data
  were used to impute missing values". BioFINDER subjects are all at the MCI stage, with a lower starting score.
- The point that people who stay five years may not be typical is the post's own general caution, not the
  release's, and it is worded as a "may".
- The Japan pen release of 2026-11-13 (https://www.eisai.com/news/2026/news202662.html): on sale that day; Japan
  is the second country after the United States; self-injection at home; MRI before and during treatment.

## Link what you name (rule 4.17)

Every first mention is linked, and each address was opened on 2026-11-21. Linda Partridge, rapamycin
(Sirolimus) and lecanemab go to Wikipedia. The Interventions Testing Program goes to the National Institute on
Aging's page, which refuses scripts and was opened in the browser. Eisai and Biogen go to their home pages, and
the CTAD conference to its home page. Clarity AD goes to its registry entry, NCT03887455, read through the data
interface: "Clarity AD", active, not recruiting. ADNI goes to its home page, and BioFINDER to its home page,
which refuses scripts and was opened in the browser. Paul-Edouard Bouvet has no public page beyond the preprint,
so his name sits inside the preprint's link. The three other drugs in the lightest-quarter figure are not named,
so they carry no link.

## Plain reading pass

Done by hand. The following were checked:
- Median, preprint, amyloid and tau each get their plain meaning at first use.
- CDR-SB, ADNI and ARIA are not used as bare terms.
- No tool is named.
- World dates and site dates are kept apart.
- Neither post says a claim was checked.

`scripts/check_news.py`, `scripts/check_site.py`, the tests and the build all pass.
