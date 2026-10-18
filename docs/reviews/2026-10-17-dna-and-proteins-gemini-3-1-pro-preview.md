# Review: dna-and-proteins packet, gemini-3.1-pro-preview, 2026-10-17

Model: `gemini-3.1-pro-preview`, version string reported by the API `gemini-3.1-pro-preview`, thinking at the highest level the API allows. Date: 2026-10-17. Mode: the packet shown in full; Google Search lookup on, 1 search made: "time to peak sales" new drugs years. Called through the Gemini API by `scripts/review_gemini.py` and filed verbatim the same day. Finish reason: STOP. Tokens: 21139 in, 1783 out, 8816 thinking; 87 seconds. Never edited after filing.

Packet sent: `docs/reviews/packets/2026-10-17-dna-and-proteins.md` (the brief in `docs/reviews/brief.md` followed by the eight branches in brief, the treatment records with the publications and promises logged against them, and the method extract).

Rulings: `docs/reviews/2026-10-17-rulings.md`.

---

| Item | Treatment / Parameter | Concerns | Proposal | Confidence |
|---|---|---|---|---|
| 1 | `a-drug-lengthens-chromosome-ends-in-a-person` | earliest, likely, latest | Move all years later: 2038, 2048, 2085 | High |
| 2 | `premature-ageing-mutation-corrected-in-a-living-animal` | earliest, likely | Move to 2036 and 2042 | Medium |
| 3 | `eye-drops-dissolve-the-clouded-protein-of-a-cataract` | earliest, likely | Move to 2031 and 2040 | High |
| 4 | lag | shared lag | Use a per-branch lag based on modality | Medium |
| 5 | independence | link | Link `measuring-age` to all therapeutic branches | High |

**1. `a-drug-lengthens-chromosome-ends-in-a-person`**
The current range (2030 earliest, 2036 likely) is no longer defensible. The record states that these dates assume a sponsor files danazol on existing data. However, the record also notes that the 2026 *Blood Advances* long-term follow-up found "no significant TL elongation was observed." Because the test explicitly requires approval of a drug "for a telomere disease on the basis of lengthening them," danazol cannot meet this standard if the data shows no lengthening. A sponsor cannot file for a lengthening claim on data that shows stable but unlengthened telomeres. This means a completely new drug will need to clear preclinical, Phase 1, Phase 2, and Phase 3 trials. I would move the earliest year to 2038, the likely year to 2048, and the latest to 2085. The source for this is the 2026 *Blood Advances* paper (Lee and colleagues, doi:10.1182/bloodadvances.2025017860) already cited in the record. This is settled by whether a sponsor actually files for danazol on this indication, which the recent data makes highly improbable.

**2. `premature-ageing-mutation-corrected-in-a-living-animal`**
The current estimate assumes a remarkably narrow three-year gap between the first human result (assumed 2029) and the earliest clinical use (2032). This is far too early for a completely novel modality (in-vivo base editing) given systemically. The FDA requires a 15-year long-term follow-up for gene therapies to monitor for delayed adverse events. While an approval can happen before 15 years based on pivotal efficacy data, the standard historical timeline from first-in-human to approval for breakthrough systemic gene therapies (such as Zolgensma, which entered trials in 2014 and was approved in 2019) is five to seven years at the absolute minimum. I would move the earliest year to 2036 and the likely year to 2042. The source for this is the FDA's guidance document, "Long Term Follow-Up After Administration of Human Gene Therapy Products" (January 2020). The field will settle this when the first human trials for progeria base editing actually register their Phase 1 to Phase 3 timelines.

**3. `eye-drops-dissolve-the-clouded-protein-of-a-cataract`**
The reasoning for the current earliest year of 2035 is explicitly based on the premise that no human trial is registered and that one might "start within three years." As the record's own notes point out, this premise is obsolete: a Phase 2 trial (NCT07395986) is already running and is scheduled to complete its primary endpoint in February 2027. If this trial reads out positively, a Phase 3 trial could realistically run from 2028 to 2030, allowing for a regulatory approval shortly after. Leaving the earliest year at 2035 ignores the active clinical pipeline. I would move the earliest year to 2031 and the likely year to 2040. The source is the ClinicalTrials.gov registry entry NCT07395986. This will be settled when the Phase 2 trial results are published.

**Treatments left as is:**
- `a-gene-is-edited-inside-a-persons-body`: Leave as is; the 2028–2030 clinical use timeline aligns perfectly with standard Phase 3 to approval timelines for NTLA-2001 following the trial's recent restart.
- `gene-therapy-lengthens-chromosome-ends-in-an-old-animal`: Leave as is; the distant timelines appropriately account for the immense safety data required to rule out the inherent cancer risks of telomerase.
- `antibody-clears-amyloid-from-the-brain-and-slows-decline`: Leave as is; the 2035 wide-use year accurately reflects the slow clinical uptake hindered by MRI/PET infrastructure and intensive safety monitoring requirements.
- `drug-boosts-the-cells-recycling-of-worn-parts`: Leave as is; the 2045 likely year properly reflects the lengthy time needed for supplement-like compounds to clear large clinical trials for specific, age-related medical conditions.
- `drug-breaks-the-sugar-cross-links-that-stiffen-old-tissue`: Leave as is; with current candidates still in the laboratory, 2036 is a standard and defensible earliest possible timeline for a new drug class.
- `drug-stops-a-misfolded-protein-piling-up-in-the-heart`: Leave as is; wide use by 2030 is reasonable given the 2019 approval of tafamidis and the rapid current entry of competitive gene silencers driving down prices.

**The lag from the clinic to ordinary people**
Published analyses of post-approval drug uptake show that the time from FDA approval to peak sales (a proxy for wide clinical use) averages roughly 6 to 10 years. A 2022 analysis of FDA-approved drugs found the median time to peak sales is 9 to 10 years. Another review found a median time to peak sales of around 6 years, noting that biologics take slightly longer (7 years) due to development complexity and market education. Therefore, the 3, 8, and 15-year triangle is a defensible shape for small molecules, but a single shared lag across all branches is not defensible. A standard daily pill or eye drop scales much faster than a complex in-vivo gene therapy, a lab-grown organ, or a PET-dependent biologic, which face severe specialized infrastructure bottlenecks. The project should abandon the single shared lag and use a per-branch lag tailored to the specific modality expected to clear that branch.

**Independence**
The strongest case for linking branches is `measuring-age` with all other therapeutic branches. An early clinical use year for `measuring-age`—meaning a regulator formally accepts a biomarker of ageing as a trial endpoint—would drastically shorten the clinical trials for every other branch. Instead of waiting decades for mortality or disease incidence data to prove a drug slowed ageing, sponsors could run much shorter trials relying on the accepted biomarker. This dependency is the foundational rationale behind initiatives like the TAME (Targeting Aging with Metformin) trial, which sought to establish composite endpoints to compress the timeline of anti-ageing drug approvals (Barzilai et al., *Aging Cell*, 2016, doi:10.1111/acel.12451). Furthermore, the FDA's Accelerated Approval pathway explicitly relies on the principle that surrogate endpoints shorten clinical development times. Thus, an early draw on `measuring-age` should mathematically shift the earliest and likely years of the other branches forward.
