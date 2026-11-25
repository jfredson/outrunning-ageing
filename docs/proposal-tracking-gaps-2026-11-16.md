# Proposal: five additions to how Outrunning Ageing tracks progress

Written 2026-11-16 (Pacific) and **PROPOSED, not yet ruled**. Nothing here has been built or changed. Each of the five items ends in a ruling to make.

## Where this came from

A conversation on 2026-11-16 asked three questions: which medical interventions for longevity look most promising, what still limits healthy adults who already eat, train and sleep well, and which drugs aimed at ageing itself could reach the market within ten years. The answers were then checked against the tree as it stands (45 treatments and tools in `data/leaves/`, read from the newest worktree on 2026-11-16).

Most of what came up is already on the tree. Two things said in that conversation were wrong about the tree and are corrected here:

- The regulatory bottleneck is already tracked. Two entries on the measuring branch cover it: "A regulator recognises ageing itself as a condition a drug can be approved to treat" and "A regulator accepts a marker of ageing as proof a treatment worked". No new entry is needed.
- Whether the branches move together is already a recorded open question (`docs/method.md`, parameter 7), raised by all four packets of the outside review of 2026-10-17.

What the tree does not have is below, in the order I would do them.

## 1. A watch list: dated events ahead, with the consequence written first

**The gap.** The weekly reading reacts to news after it lands. Nothing in the record schema holds an event that is expected on a known date (a search of `docs/record-schema.md` for "watch", "readout" and "expected" finds nothing). So when a trial reads out, the size of the change to an estimate is decided after the result is known.

**The proposal.** A new record kind, `data/watch/<id>.toml`, one per expected event:

| Field | Meaning |
|---|---|
| `event` | What is expected, in plain words |
| `expected` | When, as text (a year, a year and month, or a date) |
| `source` | Where the date comes from (registry entry or the company's own statement) |
| `leaves` | The entries it bears on |
| `if_yes`, `if_no` | Which rung or estimate moves, which way and by how many years, written before the result |
| `written_on` | The date the two consequences were written |
| `settled_on`, `outcome` | Filled when it happens |

The weekly reading checks the list for anything due and, when an event settles, compares what was done with what was written beforehand. A site page, "What to watch", lists them by date.

**First entries to write** (dates as reported in sources read on 2026-11-16; the session that builds this confirms each against the trial registry):

| Event | Expected | Bears on |
|---|---|---|
| ER-100, the first trial of cell-resetting genes in people (in the eye), reaches the end of its first phase | May 2027 | A person receives cell-resetting genes in a trial |
| NewLimit starts its first human trial, in liver disease | 2027 | The cell's settings branch |
| The United States regulator reviews the last major section of the dog drug LOY-002 | 2027 | A drug is approved to make dogs live longer |
| The second-phase trial of an antibody against interleukin-11 (an inflammatory messenger protein) in scarring reports | not found yet | Blocking one inflammatory messenger protein |
| VITAL-H, a 38 million dollar United States trial of semaglutide, dapagliflozin and rapamycin for healthy ageing in people in their sixties, starts and later reports | not found yet | A drug makes people live longer in good health |
| The TAME metformin trial is funded and registered | open | Metformin delays age-related disease; a regulator recognises ageing |

**Ruling 1:** add the watch record and page, yes or no. If yes, is the consequence binding (the reading must apply it) or advisory (the reading may differ and must say why)? I recommend advisory with a required explanation.

## 2. Entries the tree is missing

Checked by name against the 45 files. The session that writes these re-checks the notes of neighbouring entries first, since a treatment can sit inside another entry's notes.

- **VITAL-H is nowhere in the repository** (no match for "VITAL", "dapagliflozin" or "SGLT" in `data/` or `docs/`). It is the first government-funded trial aimed at healthy ageing with already-approved drugs. Proposed: a new entry on the energy and fuel branch for the drug class dapagliflozin belongs to (SGLT2 inhibitors, a diabetes and heart-failure medicine with mouse lifespan results), with a test matching the rapamycin entry: a controlled trial in older people without the disease the drug treats, improving an age-related measure more than placebo.
- **The interleukin-11 entry** says antibodies were in early trials for lung scarring. A second-phase trial in skin scarring (Mabwell's 9MW3811) was reported as dosing its first patient on 2026-01-02. That is a notes update, not a new entry.
- **Semaglutide in old mice.** A Nature paper reported in September 2026 found late-life semaglutide lengthened life in female mice. Check whether the weekly reading logged it and whether it belongs on the weight-loss drug entry or the healthy-years entry.
- **Rebuilding the ageing immune system in a person.** The tree has "An old animal's blood stem cells are rejuvenated" and nothing at the human rungs for regrowing the thymus (the gland that trains new immune cells). `fahy-2019` is in the publications, so this may sit inside a clock entry. Decide whether it earns its own entry.

**Ruling 2:** which of these four to write. I recommend the first three now and the fourth at the yearly review.

## 3. A coverage table: what still kills the healthy, and which entries answer it

**The gap.** The branches follow kinds of damage. A reader asks a different question: what will get me, and is anything on this tree aimed at it? The home page already admits the tree cannot count healthy-life gains, and `data/branches.toml` records the alternative of weighting branches by the deaths behind them.

**The proposal.** One page, display only, with no effect on the headline. Rows are the main things that end healthy life in people who already live well. Columns are the entries aimed at each, with their stage. A first pass from entry names:

| What ends healthy life | Entries aimed at it | Gap |
|---|---|---|
| Heart and blood vessels | weight-loss drug approved for heart attacks; anti-inflammatory drug; misfolded heart protein; stem-cell heart graft; gene edited inside the body | Inherited risk from lipoprotein(a), a cholesterol particle set by genes, has no entry |
| Cancer | none directly | Early-detection blood tests and cancer vaccines have no entry |
| Dementia | amyloid antibody; plasma replacement | Prevention before symptoms has no entry |
| Infection and immune decline | old animal's blood stem cells (animals only) | Nothing at a human rung |
| Frailty, falls and fractures | drug renews the cell's power plants and improves muscle; joint surface regrown; aged-cell clearing for knee arthritis | Bone has no entry |
| Ovarian ageing | none | No entry |

The value is the right-hand column: it shows where the tree is blind, in public.

**Ruling 3:** build the page, yes or no. If yes, do the gaps become new entries (which changes the headline through their branches) or stay listed as "not on the tree, and why"? I recommend listing them first and deciding entry by entry at the yearly review.

## 4. A translation scorecard: how often animal results hold up in people

**The gap.** Every estimate is a judgment about how long a treatment takes to climb from animals to a first human result to the clinic. The tree already holds the dates to measure that (`stage_reached_on` and `earlier_stage` on each entry) and nothing computes it.

**The proposal.** A script that reads the entries and reports: of the treatments shown in animals, how many reached a controlled human result, how many reached the clinic, how long each step took, and which failed in people (rapamycin's year-long trial missing its main measure, the 2026 exercise trial). Shown on the method page as the base rate behind the ranges.

**The catch.** The tree holds treatments chosen because they looked promising, so the rate would flatter the field. It needs the failures counted, which means a rule for including treatments that died before anyone would have added them.

**Ruling 4:** this is a method change. I recommend sending the design to the outside review first, not building it now.

## 5. Evidence on whether the branches move together

**The gap.** With independent draws the chance before 2050 is 4.3%. With linked draws it is about 19%. This one assumption moves the headline more than any single entry, and nothing collects dated evidence for or against it.

**The proposal.** Keep the headline on independent draws. Add one verdict to the weekly reading, "bears on linkage", for stories where progress in one branch demonstrably sped another: a regulator accepting a marker, one delivery method serving several treatments, a drug designed by machine reaching a trial. The yearly review reads the pile and decides whether parameter 7 changes.

**Ruling 5:** add the verdict, yes or no. Small change to `docs/weekly-reading.md` and the scan record.

## Order and size

| Item | Size | Needs outside review |
|---|---|---|
| 2. Missing entries | small, existing format | no |
| 1. Watch list | medium: new record kind, validator rule, one page | no |
| 5. Linkage verdict | small | no |
| 3. Coverage table | medium: one page and a mapping file | no |
| 4. Translation scorecard | large | yes |

After the rulings, the work goes to one new Claude Agents session on the `outrunning-ageing` repository. The prompt is written once the rulings are in.

## Sources read on 2026-11-16

- VITAL-H: https://www.mdlinx.com/article/3-fda-approved-drugs-tested-in-new-longevity-trial-inside-the-clinical-debate/6vQTv88VE9h2ReqTkeHV1H
- Regulatory meeting of 2026-05-27 (no approved pathway for an ageing indication): https://reaganudall.org/sites/default/files/2026-07/073126_Affecting%20the%20Aging%20Trajectory%20Public%20Meeting%20Summary.pdf
- ER-100 timing and NewLimit's 2027 trial: https://wewillcure.com/insights/news/longevity-and-healthspan/longevity-biotech-readouts-to-watch-through-2027 and https://wewillcure.com/insights/longevity-and-healthspan/funding-and-models/cures-longevity-biotech-funding-tracker-2026
- LOY-002: https://loyal.com/posts/loy-002-tas-announcement and https://www.dvm360.com/view/lifespan-extension-drug-in-development-for-senior-dogs-reaches-a-new-milestone
- Interleukin-11 antibody, second phase: https://www.dermatologytimes.com/view/first-patient-dosed-in-phase-2-trial-of-anti-il-11-antibody-for-pathological-scarring
- Semaglutide in old mice: https://nih.gov/news-events/news-releases/glp-1-treatment-late-life-extends-lifespan-animal-model
- Rapamycin and exercise in older adults: https://www.longevitywiz.com/blog/lw-rapamycin-65-85-exercise

These are news and trade sources. Under the project's own rules none of them settles a stage; each needs its registry entry or paper before it goes into a record.
