# Review: fuel-and-parts packet, gemini-3.1-pro-preview, 2026-10-17

Model: `gemini-3.1-pro-preview`, version string reported by the API `gemini-3.1-pro-preview`, thinking at the highest level the API allows. Date: 2026-10-17. Mode: the packet shown in full; Google Search lookup on, 1 search made: "time to peak sales" "years" pharmaceutical. Called through the Gemini API by `scripts/review_gemini.py` and filed verbatim the same day. Finish reason: STOP. Tokens: 31647 in, 2549 out, 11553 thinking; 89 seconds. Never edited after filing.

Packet sent: `docs/reviews/packets/2026-10-17-fuel-and-parts.md` (the brief in `docs/reviews/brief.md` followed by the eight branches in brief, the treatment records with the publications and promises logged against them, and the method extract).

Rulings: `docs/reviews/2026-10-17-rulings.md`.

---

| Item | Tracked Entry | Concerns | Proposal | Confidence |
|---|---|---|---|---|
| 1 | `a-weight-loss-drug-is-approved-to-prevent-heart-attacks-and-strokes` | Earliest and likely years | Shift earliest to 2030, likely to 2033 | High |
| 2 | `a-persons-own-cells-are-grown-to-rebuild-a-worn-joint-surface` | Earliest and likely years | Shift earliest to 2033, likely to 2040 | High |
| 3 | `cells-grown-from-stem-cells-restore-a-lost-organ-function` | Whole range | Shift to 2030, 2032, and 2046 | High |
| 4 | `heart-muscle-grown-from-stem-cells-is-grafted-onto-a-failing-heart` | Whole range | Shift to 2035, 2043, and 2085 | Medium |
| 5 | lag | Lag | Branch-specific lags (e.g., 8/15/25 for replacing-parts) | High |
| 6 | independence | Link | Link `measuring-age` and `energy-and-fuel` | High |

**Item 1: `a-weight-loss-drug-is-approved-to-prevent-heart-attacks-and-strokes`**
The record currently sets the wide-use earliest year at 2027 and the likely year at 2029, under the assumption that high prescription volumes for weight loss will naturally bleed into the heart-prevention indication. I would move the earliest year to 2030 and the likely year to 2033. The record’s own notes explicitly undercut the 2027 earliest year by citing Scannell et al. (2026), which found that fewer than 1% of eligible Medicare beneficiaries filled a prescription six months after coverage began. Reaching "a substantial share" of eligible people across several countries takes many years to scale due to payer negotiations, high out-of-pocket costs, and clinical inertia. 
*Source:* Scannell et al., 2026, *The American Journal of Managed Care*, https://doi.org/10.37765/ajmc.2026.89983 (cited in the record). 
*What would settle it:* Published prescription data and coverage figures showing a substantial share of eligible people taking it for this specific indication.

**Item 2: `a-persons-own-cells-are-grown-to-rebuild-a-worn-joint-surface`**
The record currently sets the wide-use earliest year at 2028 and the likely year at 2036. I would move the earliest year to 2033 and the likely year to 2040. The test requires the treatment to be used in "worn joints in older people", which strictly means an osteoarthritis indication. As the record notes, no Phase 3 trial in osteoarthritis has been run. A Phase 3 trial takes at least 3 to 5 years to enroll and read out, plus 1 to 2 years for an FDA label expansion, plus several years for commercial rollout to hit the "wide use" mark. Wide use by 2028 is biologically and administratively impossible.
*Source:* ClinicalTrials.gov (a search for "MACI" or "autologous cultured chondrocytes" shows no active or completed Phase 3 trials for general osteoarthritis of the knee).
*What would settle it:* A completed Phase 3 trial readout in osteoarthritis and subsequent FDA label expansion.

**Item 3: `cells-grown-from-stem-cells-restore-a-lost-organ-function`**
The record currently estimates clinical use with an earliest year of 2027, a likely year of 2028, and a latest year of 2036. I would move the earliest to 2030, the likely to 2032, and the latest to 2046. The 2027/2028 estimates assume a 2026 BLA filing. However, the record notes that Vertex paused dosing in 2025 and only resumed in May 2026, with no filing announced as of August 2026. Completing the 1-year primary follow-up for the final patients pushes final data collection to mid-to-late 2027. Filing, FDA review (which can take 6 to 10 months), and intense manufacturing scrutiny shift any realistic approval to 2029 or 2030. The latest year should be extended by a decade to allow for the possibility that the FDA demands a larger Phase 3 trial.
*Source:* Vertex Pharmaceuticals Q2 2026 financial results (August 3, 2026), as cited in the record's own notes.
*What would settle it:* The FDA approval record and Vertex's updated trial timelines.

**Item 4: `heart-muscle-grown-from-stem-cells-is-grafted-onto-a-failing-heart`**
The record currently sets the clinical use earliest year at 2031, the likely year at 2038, and the latest year at 2070. I would move the earliest to 2035, the likely to 2043, and the latest to 2085. The record accurately points out that the Zimmermann 2026 Phase 1/2 trial had a 15% mortality rate (3 deaths out of 20) and universal adverse events. These severe safety signals will trigger intense regulatory scrutiny. Any upcoming Phase 3 trial will be substantially delayed, require a redesigned protocol, or demand massive enrollment to prove safety. Therefore, an approval by 2031 is no longer defensible.
*Source:* Zimmermann et al., 2026, *New England Journal of Medicine*, https://doi.org/10.1056/NEJMoa2513525 (cited in the record).
*What would settle it:* The trial registries for upcoming Phase 3 studies in engineered heart muscle and their reported completion dates.

**Treatments left as they are:**
- `a-drug-adds-healthy-years-to-a-life`: Leave as is; the timeline realistically anticipates a long readout period for healthspan trials like TAME, safely pushing approval into the 2030s.
- `a-drug-is-approved-to-make-dogs-live-longer`: Leave as is; the ongoing STAY trial and the FDA conditional approval pathway align well with the 2027–2032 range.
- `a-drug-renews-the-cells-power-plants-and-improves-muscle-in-older-people`: Leave as is; the lack of Phase 3 sarcopenia trials accurately places approval targets in the late 2030s.
- `an-nad-raising-supplement-improves-a-function-in-a-controlled-trial`: Leave as is; the lack of commercial IP realistically delays a proper drug-label arrival to the mid-century.
- `metformin-delays-age-related-disease-in-people-without-diabetes`: Leave as is; the ongoing funding limbo for the TAME trial completely justifies the wide 2036–2100 estimate.
- `mitochondria-are-transplanted-into-a-person`: Leave as is; the need for large, rigorous Phase 3 trials following the recent small Iranian RCT fits the 2033 earliest year.
- `rapamycin-improves-an-age-related-measure-in-older-people`: Leave as is; the PEARL trial failure and the small size of current academic trials accurately support a 2039 likely arrival.
- `a-human-organ-is-grown-inside-an-animal`: Leave as is; the extreme biological and ethical hurdles perfectly justify the long-shot 2040–2160 horizon.
- `an-old-animals-blood-stem-cells-are-rejuvenated`: Leave as is; the early preclinical stage of targeted HSC depletion naturally translates to the distant 2036–2100 range.
- `lab-grown-organ-works-in-a-person-for-a-year`: Leave as is; the severe unsolved vascularization bottleneck aligns with the likely 2045 estimate for solid organs.
- `organ-from-a-gene-edited-pig-keeps-a-person-alive`: Leave as is; xenotransplantation trials starting in 2025 with 24-week endpoints fully support a 2028-2045 clinical use window.

**The lag from the clinic to ordinary people**
Published analyses of pharmaceutical launches show that standard drugs typically reach 50% of their peak sales by year three and hit peak sales around year six to nine; a 2022 study of 243 new FDA-approved drugs found a median time to peak sales of nine years. Therefore, the 3/8/15 triangle is defensible for standard prescription pills like those found in the `energy-and-fuel` branch. However, using one shared lag across all branches is indefensible. The `replacing-parts` branch involves complex surgical interventions, bespoke cell therapies, and xenotransplantation, which require specialized manufacturing facilities, surgical training, and donor-matching networks. Scaling these biologics and infrastructure bottlenecks takes far longer than scaling a pill. The branches in this packet need their own distinct lags; I would maintain 3/8/15 for `energy-and-fuel` but assign a much longer triangle of 8/15/25 for `replacing-parts`. (Source: DiMasi et al., 2022, "Assessing the Financial Value of Decentralized Clinical Trials", *Therapeutic Innovation & Regulatory Science*, PMC9472710).

**Independence**
The branches `measuring-age` and `energy-and-fuel` should be linked, such that an early year on `measuring-age` makes an early year on `energy-and-fuel` significantly more likely. The primary reason `energy-and-fuel` treatments (like metformin or rapamycin) face such long horizons is that proving a drug delays ageing requires thousands of patients and nearly a decade to complete. If the `measuring-age` branch reaches clinical use—meaning a regulator accepts a biological age clock or a surrogate composite as a valid trial endpoint—the time required to test and approve an `energy-and-fuel` drug would collapse from a decade to a year or two. The published basis for this is the Barzilai et al. (2016) design paper for the TAME trial (*Cell Metabolism* 23(6), https://doi.org/10.1016/j.cmet.2016.05.011), which explicitly anchors the feasibility of testing these preventative geroprotectors to the regulatory acceptance of an ageing composite endpoint.

*(Not asked: The strict rule that all required branches must be handled to calculate an escape year may artificially delay the headline year if a single, highly effective therapy reaches the clinic and dramatically slows ageing on its own).*
