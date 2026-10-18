# Review: signals-and-measuring packet, gemini-3.1-pro-preview, 2026-10-17

Model: `gemini-3.1-pro-preview`, version string reported by the API `gemini-3.1-pro-preview`, thinking at the highest level the API allows. Date: 2026-10-17. Mode: the packet shown in full; Google Search lookup on, 2 searches made: "Ace Alzheimer Center" AMBAR "routine care" OR "clinical practice" OR "real-world" plasma exchange; "adoption of new" drugs OR "medical technology" years after approval. Called through the Gemini API by `scripts/review_gemini.py` and filed verbatim the same day. Finish reason: STOP. Tokens: 24700 in, 1432 out, 9243 thinking; 91 seconds. Never edited after filing.

Packet sent: `docs/reviews/packets/2026-10-17-signals-and-measuring.md` (the brief in `docs/reviews/brief.md` followed by the eight branches in brief, the treatment records with the publications and promises logged against them, and the method extract).

Rulings: `docs/reviews/2026-10-17-rulings.md`.

---

| Item | Record / Concept | Concerns | Proposal | Confidence |
|---|---|---|---|---|
| 1 | `replacing-a-persons-plasma-slows-an-age-related-disease` | earliest | Move earliest year to 2026 | High |
| 2 | lag | lag | Use branch-specific lags (e.g., 1-3-5 for Measuring, 5-10-15 for Inflammation) | Medium |
| 3 | independence | link | Link "Measuring ageing" to all other branches | High |

**1. replacing-a-persons-plasma-slows-an-age-related-disease**
The record currently sets the earliest year for clinical use at 2030, assuming a named service or regulator adopts plasma exchange for ageing later this decade. I would change the earliest year to 2026. The test for clinical use allows a named clinical setting to give the treatment for that purpose in routine care and publish its practice. The Ace Alzheimer Center in Barcelona has already done exactly this: in April 2026, they presented real-world evidence at the American Society for Apheresis (ASFA) showing the results of 71 patients treated with the AMBAR plasma exchange protocol under "routine clinical practice conditions". Because this routine care is already happening and being publicly reported this year, the earliest possible year for this rung to be recognized is 2026, not 2030. The source is the April 27, 2026 announcement, "Ace Alzheimer Center presents pioneering evidence on plasma exchange to slow Alzheimer's". A review of the ASFA 2026 abstract or the center's published real-world evidence confirming it reflects routine clinical practice would settle it.

**Treatments left as they are:**
- `an-anti-inflammatory-drug-is-approved-to-prevent-heart-attacks`: Leave as is; the likely year of 2032 for wide use is defensible given the slow clinical uptake of colchicine and recent mixed results from trials like CLEAR SYNERGY.
- `blocking-one-messenger-protein-makes-old-animals-live-longer`: Leave as is; the clinical timeline is defensible given that anti-IL-11 antibodies are still in early stages for fibrosis and would need years of trials to be repurposed and approved for an age-related condition.
- `young-blood-rejuvenates-an-old-animal`: Leave as is; the 2035-2048-2110 range is defensible because human results for young plasma fractions have so far been weak, requiring decades to identify, test, and approve specific active factors.
- `young-gut-microbes-rejuvenate-an-old-animal`: Leave as is; while microbial transfers are approved for infections, demonstrating a proven anti-ageing benefit in a controlled human trial will require years of research, making 2050 a reasonable likely year.
- `a-blood-test-predicts-a-persons-death-and-disease-better-than-their-age`: Leave as is; the 2034 likely year for clinical use is defensible, as electronic health record integration of epigenetic clocks is currently limited to research biobanks, not routine patient care.
- `a-regulator-accepts-a-marker-of-ageing-as-proof-a-treatment-worked`: Leave as is; regulatory biomarker qualification is notoriously slow, and 2040 is a defensible likely year given no such marker is currently advancing in the FDA's pipeline.
- `a-regulator-recognises-ageing-as-a-condition-a-drug-can-treat`: Leave as is; the mid-2040s likely estimate is realistic because the TAME trial has not yet started, pushing any regulatory decision for a broad ageing label decades into the future.
- `a-treatment-slows-a-biological-age-clock-in-a-controlled-trial`: Leave as is; because all current clock results in trials are post hoc, waiting for a pre-planned controlled trial to read out makes 2037 a defensible likely year.
- `an-age-for-each-organ-is-read-from-blood-proteins`: Leave as is; the likely year of 2036 is appropriate, as these proteomic panels are complex, expensive, and will require years of refinement and cost reduction before routine health system adoption.

**The lag from the clinic to ordinary people:**
The shared 3, 8, 15-year lag from the clinic to wide use is broadly consistent with historical averages for drug adoption; for example, a 2025 review in the journal Brain notes that it took nearly four years for a newly approved epilepsy treatment to reach just 10 percent of eligible patients. However, one shared lag for every branch is not defensible because the logistics of these treatments differ drastically. The "Measuring ageing" branch relies on diagnostic tests (blood protein panels and epigenetic clocks) which, once cleared by a regulator, can scale almost immediately via centralized commercial labs, warranting a shorter lag like 1, 3, and 5 years. By contrast, "Inflammation and the body's messaging" includes therapeutic plasma exchange and faecal microbiota transplants, which require physical clinic space, donor material, and extensive patient chair time. Rolling out this physical infrastructure will be much slower, making a lag of 5, 10, and 15 years more appropriate. 

**Independence:**
The draws should not stay independent. The "Measuring ageing" branch must be linked to the other treatment branches, particularly "Energy and fuel sensing" and "Inflammation and the body's messaging". The strongest published basis for this is the Moqri et al. (Cell, 2023) paper logged in the site's own records, which states that validated biomarkers of biological age are necessary to properly evaluate longevity interventions. As the site's own record for regulatory acceptance explicitly notes, if a regulator accepts a marker of ageing as a trial endpoint, it directly removes the requirement to wait for patients to sicken or die, cutting a decade off the trials for every other drug on the tree. Therefore, an early draw on the regulatory acceptance of a clock in the Measuring ageing branch should mathematically make an early year for every other branch more likely.

**Not asked:** I would leave the triangle shape, the two-treatments-per-branch rule, the fixed dates, and the seed as they are.
