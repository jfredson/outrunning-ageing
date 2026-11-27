# Rung-reached post of 2026-11-27: heart muscle sheets in use with patients in Japan

The post: `site/src/content/news/2026-11-27-heart-muscle-sheets-in-use-in-japan.md`

A "rung reached" post (`kind: rung-reached`). On 2026-11-27 John ruled on the four stage questions from the weekly
readings ("Yes, as recommended"), and the heart entry moved to in clinical use from 2026-03-06 (pull request 57).
He then asked for this post ("Yes, draft it"). **Not published.** It sits on its own branch and pull request, and
merging to `main` deploys it, so John approves it first (tracker pattern, rule 4.18).

## Promotion gate (rule 3.3, part 4)

`python3 scripts/compute.py validate` on 2026-11-27: "0 claim(s) marked to verify". No record carries an open
check. The record the post names changed on 2026-11-27, so it passes the fourteen-day rule.

## The before-and-after line

- Before: 6 of 45 tracked treatments in clinical use or beyond (counted from the records at main before pull
  request 57).
- After: 7 of 45, counted from the records after it.
- The headline before and after: the headline file before pull request 57 (computed 2026-11-09) gives median 2058
  and before-2050 0.0427. The rerun of 2026-11-27 gives median 2058 and before-2050 0.0431. The replacing-parts
  branch's median year went from 2032 to 2026; worn-out cells is at 2043 and damaged DNA at 2044.

## Facts, each against its source (opened 2026-11-27)

**The regulator's review report** (https://www.pmda.go.jp/files/000281693.pdf, English):
- Indication: severe heart failure associated with ischaemic cardiomyopathy with an inadequate response to standard
  treatment, including drugs and invasive procedures. The post says "severe heart failure after heart attacks whom
  drugs and other standard treatment have not helped enough".
- "Duration of Approval 7 years". The conditions include surveillance of every treated patient.
- Study CVSC0005: a multi-centre, open-label, uncontrolled study, with a target of 8 patients, at 5 sites, December
  2019 to March 2024.

**The regulator's list** (https://www.pmda.go.jp/files/000283257.pdf, checksum matched to a second download):
"Mar. 6, 2026 RiHEART (Cuorips Inc.) Conditional/Time-limited Approval"; the same for AMCHEPRY (Sumitomo Pharma).

**Cuorips, 2026-03-06** (https://cuorips.co.jp/news-en/20260306): the conditional and time-limited approval, for
"patients with severe ischemic heart failure who have exhausted conventional treatment options".

**Cuorips, 2026-10-01** (https://cuorips.co.jp/news-en/200261001, read on the page): eligible for public health
insurance coverage on September 1, 2026; the first transplantation after coverage on September 29, 2026, at Osaka
Police Hospital.

**HeartSheet** (https://www.pmda.go.jp/files/000272880.pdf): the expert committee and the council concluded in July
2024 that the product should not be approved, because efficacy was not shown by the use-results survey and clinical
study run after the conditional, time-limited approval of 2015 (the regulator's list gives that approval as
2015-09-18). Sales ended (MONOist, 2024-08-08); the post does not state a sales date.

**AMCHEPRY**: supplied for the time being only to institutions cooperating in the post-marketing clinical study
(Sumitomo Pharma's notice of 2026-06-26 and its presentation of 2026-10-30), as recorded on its entry on
2026-11-27.

**Göttingen**: the trial report (Zimmermann and others, New England Journal of Medicine, online 2026-05-27,
https://doi.org/10.1056/NEJMoa2513525, opened in the browser), 20 patients, three deaths, a higher ejection
fraction at three months at the highest dose, no comparison group, as the entry records.

## Link what you name (rule 4.17)

Each address was opened on 2026-11-27:
- Cuorips (its English home page), Osaka Police Hospital (its home page, in Japanese) and the Pharmaceuticals and
  Medical Devices Agency (its English home page) go to their own sites.
- Terumo's home page refused the plain fetch and was opened in the browser.
- The University Medical Center Göttingen goes to its English home page.
- Heart failure and induced pluripotent stem cells go to Wikipedia.
- RiHEART, HeartSheet and AMCHEPRY are named inside links to the records that describe them.

## Plain reading pass

Done by hand:
- Heart failure, induced pluripotent stem cells and a conditional approval are each explained at first use.
- No IND, iPSC or cardiomyocyte appears in the prose; the title of one source keeps the company's wording.
- No tool is named.
- The post speaks as "I" and never says "the site counts".
- Dates are spelt out in the prose.
