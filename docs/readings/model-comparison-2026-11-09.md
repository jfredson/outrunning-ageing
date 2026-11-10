# Which model should read the news: a measured comparison, 2026-11-09

John asked on 2026-11-09 how the model arrangements for the weekly reading could be tested for "a measurable difference worth capturing", and said go the same evening. This is the test and its result. Nothing was published and no record was edited. The ruling on which model reads what (step 1a part E of `docs/weekly-reading.md`) is John's.

## The result in one table

The four runs between them reported 21 real stories from the week that a blind checker graded as mattering most (a result in people, a regulator's decision, a company dropping or advancing a treatment, a new trial plainly about ageing).

| Arrangement | Top-graded stories found, of 21 | Stories of interest found, of 35 | Usage, in tokens |
|---|---|---|---|
| All Sonnet 5.5 (two runs) | 12 and 9 | 9 and 14 | about 0.98 million each |
| Sonnet 5.5 record readers with a Fable 5.2 sweep (four pairings) | 13 to 17 | 15 to 19 | about 1.1 to 1.2 million |
| All Fable 5.2 (two runs) | 21 and 16 | 28 and 24 | about 1.65 to 1.7 million |
| For scale: the reading the scheduled routine published for the same week (Sonnet 5.5, in the cloud) | 3 | not scored | not measured |

In plain words: all Sonnet found about half of the stories that matter most, the mixed arrangement about three quarters, and all Fable about nine tenths, for about 70 per cent more usage than all Sonnet.

## What else the numbers show

- **Nothing was invented.** Of 188 reported items, 186 were confirmed at a source and 2 could not be opened. No item was contradicted. The checkers did find wrong details inside true stories (a patient count off by one, a date a day out, a figure attached to the wrong measure) from readers on both models, and did not count them by model.
- **Two runs of Sonnet 5.5 agree with each other less than two runs of Fable 5.2 do.** Counting top-graded stories and stories of interest together, the two Sonnet runs shared 13 and differed on 18 (8 only in the first, 10 only in the second). The two Fable runs shared 36 and differed on 17 (13 and 4). A single Sonnet reading is partly luck: one run found the week's biggest result for a tracked treatment (the full results of the anti-inflammatory heart drug trial) through its sweep only, and its record reader missed it.
- **Running Sonnet twice does not close the gap.** The two Sonnet runs pooled found 13 of the 21 top-graded stories. The weaker of the two single Fable runs found 16.
- **Most of the difference is the field-wide sweep.** Alone, the Fable sweeps found 16 and 11 of the 21; the Sonnet sweeps found 7 and 5. The Fable sweeps read every paper title in the week (about 1,000) and every title in 22 main journals; the Sonnet sweeps ran one or two queries. This is why the mixed arrangement captures much of the gain.
- **The record readers differ too.** Fable readers opened 228 and 187 pages across the 45 treatments; Sonnet readers 44 and 58. Fable readers found 14 and 10 of the top-graded stories by themselves; Sonnet readers 5 and 5. Fable readers also turned up the older facts the entries lack (Japan's conditional approvals, a trial date that slipped), which this scoring does not count because they are outside the week.
- **Fable 5.2 is not complete either.** Its first run missed the failed Alzheimer's antibody announced on 2026-10-30, which both Sonnet runs found through a news report. Three stories of interest were found only by a Sonnet run.
- **Eight top-graded stories were found by no Sonnet run:** the healthspan trial first posted on 2026-11-06, a new trial in age-related muscle loss, first results in people for a gene editor against blood fats, the company's write-down on the failed heart antibody, five-year results for a heart-protein drug, a trial of stopping statins in people over 70, and two small company-reported results. The first four were found by both Fable runs.
- **No Fable 5.2 reader was stopped by the safety filter** in these 14 runs. One was in the trial of the same morning.
- **Sonnet readers mostly did not save as they went.** At least ten of the fourteen Sonnet readers said they wrote their file once at the end, against the instruction to save after every record; one said it saved as it went. The Fable readers saved as they went, with small lapses (one wrote its last three records together). In an unattended run, a reader stopped before the end would lose its whole group.

## The larger surprise: the routine in the cloud did far worse than the same model here

The scheduled routine ran the same week on Sonnet 5.5 under the procedure now in force and published 3 of these 21 stories. The same model, run here from the comparison's brief, found 12 and 9. The difference is not the model. Likely causes, none tested: the routine's helpers are briefed by the main reader in its own words and not from a fixed brief; its sweep read the first 25 of 493 paper titles; the press-release and filings sites refused the cloud machine; and the whole reading took about eight minutes. So fixing how the routine briefs its helpers may be worth as much as changing its model, and whichever model is chosen should be tested in the cloud and not assumed from this.

## How it was done

- **The week:** 2026-11-02 to 2026-11-09.
- **Four sets of runs:** the six groups of record readers and one field-wide sweep, on Sonnet 5.5 twice and on Fable 5.2 twice. 28 readers in all. The 45 treatments were read; the 31 claims and 9 self-experiments were left out, because they were almost all quiet in every earlier run.
- **Three arrangements from four sets:** all Sonnet is a Sonnet run's readers with its own sweep; all Fable likewise; the mixed arrangement is a Sonnet run's readers with a Fable run's sweep, which gives four pairings. The main reader's weighing and assembly were not run, so the mixed figures measure what would be found, not what a Fable main reader would then do with it.
- **Clean records:** every reader worked from a copy of the records as they stood before 2026-11-09 (commit 3219363), with no earlier readings, no changelog and none of the day's write-ups. Each was told to read nothing else on the machine. The other runs' files sat in neighbouring folders; one reader reported seeing their names in a listing and opening none.
- **One brief for both models** (`brief-reader.md` and `brief-sweep.md` in the folder beside this file), written from step 1a of the procedure, with no fixed number of queries or stories.
- **The blind check:** the 464 findings dated in the week were grouped by registry number, paper identifier or address into 188 items. Seven checkers on Fable 5.2 each had about 27, with no sign of which run reported what. Each opened the source and said whether the item was real, what its true date was, and how much it mattered, on three grades (`check/brief-check.md`). Items the checkers marked as the same story were joined, and the session joined nine more pairs it saw across packets, leaving 156 stories: 147 real and in the week (21 top-graded, 35 of interest, 91 routine) and 9 others.

## What this does not show

- **One week.** A week with a large heart meeting in it, which favours a reader that follows meeting coverage. A quiet week might show a smaller gap.
- **No outside reference.** Stories that all four runs missed are invisible here. The monthly check by a non-Claude model (`scripts/miss_check_gemini.py`) is built for that and has not been run. No run reached the press-release sites directly.
- **The grades are one checker's judgement,** and the checkers were Fable 5.2, though blind. Four of the 21 top grades are small or company-reported results that the checker said a cautious reader could mark one step down. Two of them were found only by the first Fable run, one by that run and a Sonnet run, and one by all four runs. Leaving those four out, the figures are 11 and 7 of 17 for Sonnet and 17 and 15 of 17 for Fable, so the gap does not rest on them.
- **Usage is the readers' own token counts as the tool reported them,** useful for comparing arrangements with each other and not as a bill. All of it ran on the plan.
- **Duplicates may remain** among the routine items, where the same registry edit reached two checkers. That would not change the top-graded count, which was checked by hand.

## The 21 top-graded stories and who found them

| Date | Story, in the checker's words | Sonnet 1 | Sonnet 2 | Fable 1 | Fable 2 |
|---|---|---|---|---|---|
| 2026-11-02 | Vertex third-quarter 2026 results, 2026-11-02: company puts its newer islet-cell therapy VX-017 ahead of zimislecel, expects late-stage development of VX-017 in 2027 | yes | yes | yes | yes |
| 2026-11-03 | Circulation, online 2026-11-03 (Garcia-Pavia and colleagues): HELIOS-B open-label extension of vutrisiran to month 48, 37 per cent lower risk of death in those on the drug throughout | yes | yes | yes | yes |
| 2026-11-03 | Registry first posts NCT07912164 on 2026-11-03: Human Biome placebo-controlled trial of gut-microbe capsules to slow the pace of ageing in 68 adults aged 45 to 80 | yes | yes | yes | yes |
| 2026-11-04 | European Heart Journal Open: randomised trial of a multi-ingredient ageing supplement (NOVOS) improved artery measures in 61 healthy adults (Piercy et al.), 2026-11-04 | yes | yes | yes | yes |
| 2026-11-05 | Registry NCT07920133 first posted 2026-11-05: TARGET-CHD, Sir Run Run Shaw Hospital, 1,768 people, colchicine guided by an inflammation blood marker after stenting | yes | yes | yes | yes |
| 2026-11-07 | ZEUS trial: ziltivekimab (Novo Nordisk, interleukin-6 antibody) did not cut heart events in 6,376 people; presented at the American Heart Association meeting and published in NEJM, 2026-11-07 | yes | yes | yes | yes |
| 2026-11-07 | Full Lp(a)HORIZON results: pelacarsen lowered lipoprotein(a) but not heart events; AHA meeting and NEJM, 2026-11-07 | yes | yes | yes | yes |
| 2026-11-09 | FDA approves Bayer's asundexian (Sunharbo), first factor XIa blocker, to prevent a repeat stroke, 2026-11-09 | yes | yes | yes | yes |
| 2026-11-05 | Registry posts results 2026-11-05 for Janssen's phase 2 trial of the anti-tau antibody posdinemab in early Alzheimer's (NCT04619420): no difference from placebo | yes | - | yes | yes |
| 2026-11-09 | FDA, 2026-11-09: all twelve approved GLP-1 drugs must add a label warning about a rare eye condition (non-arteritic anterior ischaemic optic neuropathy) | yes | - | yes | yes |
| 2026-11-09 | SYNCHRONIZE-CVOT: survodutide (Boehringer Ingelheim / Zealand) did not raise major heart events against placebo, no proven reduction; American Heart Association meeting and The Lancet, 2026-11-09 | yes | - | yes | yes |
| 2026-11-09 | ATTAIN-OSA: orforglipron (Foundayo, Lilly) reduced sleep apnoea severity in two phase 3 trials; AHA meeting, 2026-11-09 | yes | - | yes | yes |
| 2026-11-03 | Muna Therapeutics phase 1 results for MNA-001, an oral TREM2 activator; spinal-fluid ageing markers shifted in elderly volunteers, 2026-11-03 | - | yes | yes | - |
| 2026-11-04 | Novo Nordisk nine-month report, 2026-11-04: 4.6 billion kroner write-down on ziltivekimab; ZEUS and HERMES missed their main goals; ziltivekimab work closed | - | - | yes | yes |
| 2026-11-06 | VITAL-H (NCT07923630), University of Texas Health Science Center at San Antonio, first posted 2026-11-06: phase 2 trial of oral semaglutide, dapagliflozin or placebo in 1,200 people aged 60 to 75 against the decline of ageing | - | - | yes | yes |
| 2026-11-06 | Epirium Bio, registry entry NCT07921420 first posted 2026-11-06: phase 2b placebo-controlled trial of MF-300 in 225 adults aged 65 and over with age-related muscle loss | - | - | yes | yes |
| 2026-11-09 | CRISPR Therapeutics, 2026-11-09: phase 1b data for CTX310 (one-time in-body editor of ANGPTL3) in 10 people with severe high triglycerides, presented at the American Heart Association meeting; 65% fall in the target protein, 63% in triglycerides at day 30 | - | - | yes | yes |
| 2026-11-02 | Enlivex 12-month headline results for Allocetra injections in age-related knee osteoarthritis, phase 1/2a, 2026-11-02 | - | - | yes | - |
| 2026-11-05 | Resolution Therapeutics interim six-month results for RTX001 engineered macrophage therapy in end-stage liver disease (EMERALD trial), 2026-11-05 | - | - | yes | - |
| 2026-11-08 | STREAM trial: stopping statins in people 70 and over without cardiovascular disease was no worse at two years; AHA meeting and NEJM, 2026-11-08 | - | - | yes | - |
| 2026-11-09 | Alnylam release, 2026-11-09: five-year HELIOS-B data for vutrisiran at the American Heart Association meeting, 41 per cent lower combined risk of death and repeat heart events overall, 48 per cent in those on the drug alone | - | - | yes | - |

## The 35 stories of interest

| Date | Story, in the checker's words | Sonnet 1 | Sonnet 2 | Fable 1 | Fable 2 |
|---|---|---|---|---|---|
| 2026-11-05 | Intellia third-quarter 2026 release, 2026-11-05: enrolment complete in MAGNITUDE-2 (nex-z, nerve form, past target of 60); MAGNITUDE heart trial still enrolling; registry entries for both trials updated 2026-11-04 and 2026-11-05 | yes | yes | yes | yes |
| 2026-11-05 | Ye and colleagues, Cell Stem Cell, 2026-11-05: lasting, partly reversible silencing of a platelet gene by editing DNA marks in human blood-forming stem cells, stable four months after transplant into mice | yes | yes | yes | yes |
| 2026-11-05 | Registry entry NCT07918261 first posted 2026-11-05: Steadman Philippon Research Institute's completed fisetin trial in 82 healthy volunteers, two dosing schedules, no placebo, no results posted | yes | yes | yes | yes |
| 2026-11-06 | Mizoguchi and colleagues (Verve Therapeutics, part of Eli Lilly), Nature, 2026-11-06: laboratory and monkey work for a one-dose base editor that switches off ANGPTL3; first trial in people under way | yes | yes | yes | yes |
| 2026-11-06 | Nature Aging, 2026-11-06 (Wu and colleagues): vanadyl sulfate, a mineral supplement, kills aged cells and by mouth extends lifespan in male mice | yes | yes | yes | yes |
| 2026-11-02 | BioArctic announced 2026-11-02 that Novartis ended their 2025 brain-delivery technology agreement (up to 802 million dollars; BioArctic keeps the 30 million upfront) | - | yes | yes | yes |
| 2026-11-02 | Immorta Bio release, 2026-11-02: first person given SenoMune-0257, a peptide meant to train the immune system against aged cells, on 2026-10-29 in Mexico, in a doctor-run study of advanced cancer | - | yes | yes | yes |
| 2026-11-03 | Registry: NCT07911670 first posted 2026-11-03, early trial of UX-DA003 (stem-cell-derived cells) in 12 people with Parkinson's disease, First Affiliated Hospital of Anhui Medical University | yes | - | yes | yes |
| 2026-11-04 | Nature Metabolism, 2026-11-04, Romenskaja-Avgul and colleagues: whole-blood NAD (1,340 measurements, 1,068 adults) does not fall with age in healthy people; lower in cardiovascular disease and high blood pressure | - | yes | yes | yes |
| 2026-11-05 | Blood, 2026-11-05, Romero-Mulero and colleagues: in mice, most blood stem and early blood cells change markedly with age, but one lymphoid-leaning group (MPP6) changes little | - | yes | yes | yes |
| 2026-11-05 | Stewart and Fitzsimmons, GeroScience, 2026-11-05: kidney transplant recipients prescribed rapamycin died at the same age as those not (64.6 against 64.3 years) | - | yes | yes | yes |
| 2026-11-07 | Baldwin and colleagues, Cardiovascular Research, 2026-11-07: colchicine vs placebo in 111 people with coronary disease, no fall in artery inflammation on scans | yes | - | yes | yes |
| 2026-11-02 | Journal of Clinical Investigation, 2026-11-02: dapagliflozin linked to lower odds of pre-frail older people with high blood pressure and kidney disease becoming frail over one year (odds ratio 0.13), matched comparison, not randomised | - | - | yes | yes |
| 2026-11-02 | CRISPR Therapeutics third-quarter 2026 release, 2026-11-02: CTX310 (in-body editor of ANGPTL3) holds the regulator's regenerative-medicine designation for severe high triglycerides and for raised LDL cholesterol; phase 1b data due at the heart meeting 2026-11-09 | - | - | yes | yes |
| 2026-11-02 | Research Square preprint, 2026-11-02, Jin and colleagues: quieting over-active hypothalamus nerve cells in aged mice restored lymph-cell precursors and B-cell production and improved the H1N1 vaccine response | yes | - | yes | - |
| 2026-11-02 | Cell, 2026-11-02 (Kuehnemann and colleagues): the fatty acid DGLA pushes aged cells into a form of cell death; by mouth it lowered markers of aged cells in old mice | - | - | yes | yes |
| 2026-11-02 | Registry entry NCT07906041: Atria institute's 22-person trial of tirzepatide with a blood-protein brain age as main measure; first posted 2026-10-30, updated 2026-11-02 | - | - | yes | yes |
| 2026-11-02 | FDA final guidance on potency assurance for cell and gene therapies, replacing 2011 guidance, 2026-11-02 | - | yes | - | yes |
| 2026-11-04 | Registry: NCT07917403 first posted 2026-11-04, University of California San Diego, 30-person feasibility study of a nicotinamide riboside combination supplement (NRPT) in knee osteoarthritis | - | - | yes | yes |
| 2026-11-05 | Sana Biotechnology third-quarter 2026 update, 2026-11-05: expects to ask permission and start a first trial of SC451 (stem cell-derived islet cells) as early as this year; restates 14-month donor-islet result in one person | - | - | yes | yes |
| 2026-11-06 | FDA investigates tumours after Novartis gene therapy Zolgensma; nine reported cases since 2019, 2026-11-06 | yes | - | yes | - |
| 2026-11-09 | Editas Medicine third-quarter 2026 release, 2026-11-09: Australian ethics approval and regulator notification complete for the first trial in people of EDIT-401, an in-body editor for inherited high cholesterol; first dosing expected in 2026 | - | - | yes | yes |
| 2026-11-09 | Humacyte release on its first study in people of an engineered blood vessel for heart bypass surgery, tied to the AHA meeting, 2026-11-09 | - | - | yes | yes |
| 2026-11-02 | American Heart Association release, 2026-11-02, on meeting abstract MDP1524: in records of 256,492 adults with prediabetes and obesity, GLP-1 drug users had fewer heart attacks, strokes and deaths than metformin users | - | - | - | yes |
| 2026-11-02 | Research Square preprint, 2026-11-02: gene-edited pig livers supported six monkeys in liver failure for 74 to 144 hours, with platelets falling sharply | - | yes | - | - |
| 2026-11-02 | Nature Biomedical Engineering paper on RetiME, a mortality-risk measure read from retinal photographs (Xu et al.), 2026-11-02 | - | - | yes | - |
| 2026-11-04 | Scribe Therapeutics release, 2026-11-04: to present updated monkey data on its PCSK9 epigenetic silencer STX-1150 (LDL cholesterol held down at least two years after one dose) at the American Heart Association meeting on 2026-11-07 | - | - | - | yes |
| 2026-11-04 | Blood, 2026-11-04, Igarashi and colleagues (Wilkinson group): old mouse blood stem cells expand poorly outside the body with low Lin28b; forcing Lin28b on improved their transplant performance | - | - | yes | - |
| 2026-11-04 | Pharmazeutische Zeitung (dpa), 2026-11-04: a year of lecanemab and donanemab in Germany; neurologist Özgür Onur estimates 1,000 to 2,000 people treated; no proven added benefit; price talks continuing | - | yes | - | - |
| 2026-11-04 | Cell Reports mouse study: clearing light-chain amyloid around liver vessels with anselamimab restored aged liver regrowth (Zhang et al.), 2026-11-04 | - | - | yes | - |
| 2026-11-05 | GEN article 'Beyond Conventional CRISPR', 2026-11-05: eGenesis expects its RESTORE pig kidney trial to start in the first quarter of 2027 and a first pig heart transplant in 2027 | - | yes | - | - |
| 2026-11-05 | JCI paper: senescent cells drive facioscapulohumeral muscular dystrophy; lamivudine reduced them in mice (Jung et al.), 2026-11-05 | - | - | yes | - |
| 2026-11-06 | Vericel third-quarter 2026 results call (reported 2026-11-06): the United Kingdom's cost-effectiveness body NICE accepted MACI for appraisal; United Kingdom launch targeted for the second half of 2027 | - | - | - | yes |
| 2026-11-06 | Lilly registers phase 2 trial of bimagrumab in heart failure with preserved ejection fraction (NCT07920887, ACTIVATE-HFpEF), first posted 2026-11-06 | - | - | yes | - |
| 2026-11-09 | Longevity.Technology 2026-11-09: 'Younger', a six-month contest by NeuroAge Therapeutics and Longevity Global for about 500 people to lower biological age, tested by TruDiagnostic | - | - | yes | - |

## Reported as this week's, but outside the week or not confirmed

- Check for the metformin trial TAME on 2026-11-09: no registry entry posted or updated 2026-11-02 to 2026-11-09, and afar.org/research/TAME/ answers 'not found' Real: yes; true date None; reported by: f1.
- Loyal's page for veterinarians, read 2026-11-09: effectiveness and safety sections complete, manufacturing section and conditional approval 'In progress', STAY study ongoing; no dated news in the window Real: yes; true date None; reported by: f1, f2, s1.
- Zhavoronkov and colleagues, Nature Biotechnology, 2026-09-07: six blood-protein age clocks read lower biological age in the rentosertib arms of a 12-week phase 2a lung-scarring trial (discussed by Fight Aging! 2026-11-09) Real: yes; true date 2026-09-07; reported by: f1, s1, s2.
- Intellia quarterly report (Form 10-Q for the quarter to 2026-09-30), filed 2026-11-05: restates the 2025 trial stop, the patient death and the immune-gene finding; no new safety event Real: unverified; true date 2026-11-05; reported by: f1.
- Heikkinen and colleagues, Aging Cell, 2026-08-01: nicotinamide riboside for five months linked to lower epigenetic age acceleration in muscle (mentioned in Niagen Bioscience's results release of 2026-11-04) Real: yes; true date 2026-08-01; reported by: f2.
- Acumen announced 2026-10-30 that sabirnetug missed the main 18-month measure in the 542-person ALTITUDE-AD phase 2 trial in early Alzheimer's and that it is ending development; NeurologyLive report 2026-11-03 Real: yes; true date 2026-10-30; reported by: f2, s1, s2.
- Novo Nordisk stopped two ziltivekimab heart-failure trials, HERMES and ATHENA, for low chance of success; reported 2026-09-07 Real: yes; true date 2026-09-07; reported by: f2.
- Null checks of the trial registry made on 2026-11-09: no entry for the TAME metformin trial by its full title; no entry for SenoVax, SenoMune or Immorta Real: yes; true date None; reported by: f1, f2.
- Null check on 2026-11-09 of three mitochondrial transplant registry entries (NCT04998357, NCT02851758, NCT04976140): none changed in the week Real: yes; true date 2026-01-05; reported by: f1.

## Files

Beside this file: the four runs' raw output (`run-s1`, `run-s2` for Sonnet 5.5; `run-f1`, `run-f2` for Fable 5.2), the three briefs, the seven checkers' output and the joined list (`check/stories-final.json`).
