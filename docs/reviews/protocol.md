# Outside-model review of the 44 ranges, the lag and the independence assumption: protocol

The roadmap step "After launch: outside-model review of the ranges", and the method document's own flag: parameter 2 (the lag from the clinic to ordinary people) was ruled by John on 2026-10-16 with its figures marked a first guess with no source and sent to this review, and parameter 7 (independent draws) says this review is the place to raise linking between branches. Proposed 2026-10-17, adapted from The Quiet Galaxy's review protocol of the same date (`~/Code/quiet-galaxy/docs/reviews/protocol.md`), which in turn adapted The Belt Equation's of 2026-09-19, and run the same day as proposed at the master session's instruction, so that John's ruling on the protocol can take the first run's results into account. Each design choice is listed at the end with a confidence level and its strongest alternative, per the ground rule of 2026-09-08. **Nothing here is ruled until John says so.**

## Purpose

Every range was proposed by one model (Claude) on 2026-10-16 and accepted by John as a first pass. That is one source of error with no check on it, and the headline rests on it. The review puts each treatment's record in front of a model from another lab, files what it says verbatim, checks every source it names, and has John rule on every item. It is a critique pass, not a vote: the reviewer can move a range only through John's ruling, and a ruling to keep a range over the reviewer's objection is a valid outcome that goes on the record with its reason.

The weekly reading (`docs/weekly-reading.md`) is a different thing and stays separate. It looks for new publications once a week and may move a stage only on a record, and a year only within its cap; the ranges as a whole, the lag and the independence assumption are this review's to argue.

## What is reviewed

The 44 treatments' estimates: for each, the earliest, likely and latest year for the rung the headline draws from (in clinical use; for the six treatments already there, the wide-use rung, which the headline does not draw but the site shows), with the reason the record gives. Everything on each record goes to the reviewer: the description, the test, the stage with its record and earlier rungs, the estimate with its reason, the notes, the revisions, the publications logged against it and the promises filed against it.

Two questions are put specially, because the method document sent them here on 2026-10-16: whether the lag of 3, 8 and 15 years from the clinic to ordinary people has published figures behind it and whether one lag for every branch is defensible or a lag per branch is needed; and whether any pair of branches should be linked in the draw, and on what evidence.

Not reviewed: the stages (what has happened is a matter of record, and a dispute about a stage goes to the weekly reading), the tests, the choice of treatments, the headline numbers, the site, and the rest of the method (the triangle, the two-treatments-per-branch rule, the fixed dates, the seed). The brief tells the reviewer so and allows one line on each at the end.

## The reviewer

Google's Gemini, called through its API with a fixed model id and the version string the API reports recorded at the top of every filed response, with Google Search lookup switched on so the reviewer can check trials and approvals the record may have missed. The first run uses `gemini-3.1-pro-preview`, the model the siblings' reviews used on 2026-10-17. The key is read from the environment and never written anywhere. If a lab ships a new model mid-review, the review finishes on the model it started with.

One reviewer for the first run; a second from a third lab is added if John wants a second opinion on items where Claude's recommended ruling disagrees with the reviewer (decision 1).

## The brief

One fixed text (`docs/reviews/brief.md`), sent unchanged at the top of every packet. For every treatment it asks three things: is the range supported by published evidence the reviewer can name; which way is it wrong, if it is, with a specific earliest, likely and latest; and what is the source for every fact the record does not already cite, with the site's rule stated that an unsourced figure is declined for that reason alone. It puts the lag and independence questions once per packet, says what is not asked, and asks for a table of items first, then the items, then one line per treatment left as it is, then the two method answers. It sets thresholds so that small differences are not argued: three years at the likely or the earliest, ten at the latest.

## Packets

Four packets of two branches each, in the branches' own order, so each call stays within a sensible length and the reviewer sees a treatment's neighbours on its branch:

| Packet | Branches | Treatments |
|---|---|---|
| `cells-and-settings` | worn-out cells; the cell's settings | 10 |
| `dna-and-proteins` | damaged DNA; broken proteins and waste | 9 |
| `fuel-and-parts` | energy and fuel sensing; replacing lost cells and parts | 15 |
| `signals-and-measuring` | inflammation and the body's messaging; measuring ageing | 10 |

Each packet carries the brief, a table of all eight branches (so the independence question can be answered from any packet), the records, and the method extract. `scripts/review_packets.py` generates them from the records; they live under `docs/reviews/packets/`, named by date and packet.

## Running

- `python3 scripts/review_packets.py` writes the four packets dated today.
- `python3 scripts/review_gemini.py docs/reviews/packets/<date>-<packet>.md` sends one packet, in the foreground, streaming the answer to the terminal and to a partial file as it arrives (the sibling's lesson: a background call once lost a whole answer to a dropped connection), and files the answer verbatim as `docs/reviews/<date>-<packet>-<model>.md` with the model's version string, the date, the mode, the finish reason and the token counts at the top. A filed review is never edited. If a call drops, the packet is run again.
- The rulings list, `docs/reviews/<date>-rulings.md`, is written by Claude after all four packets are filed: every item the reviewer raised, numbered, with the treatment or parameter, what the reviewer said, whether its source checks out (the source opened; if it cannot be opened or does not say what the reviewer claims, the list says so, because a reviewer's recollection is not a source either), the recommended ruling (accept, decline, or accept if a named source checks out) with a one-line reason, and the headline the change would give if accepted, computed by running `scripts/compute.py run` on a scratch copy of the records, never on the records themselves. The lag and independence items come first, and the list ends with the short list of items that matter most for the headline. The review itself changes no range, no stage and no parameter.
- When John has ruled, every accepted item lands as a dated revision on the treatment, a dated line in `CHANGELOG.md`, and a re-run of the headline; a range whose items are all ruled has its estimate status set to `reviewed`. A declined item keeps its reason on the record so the next review can see it was considered.

## Done

Every treatment reviewed, every item ruled, the changes landed, the headline re-run and the new numbers in the changelog, and no range left at "first pass". Then the rest of the method (the two-per-branch rule, the triangle, the fixed dates) gets its own single pass with a different brief.

## Decisions (proposed 2026-10-17, not ruled; each with confidence, whether it is standard practice, and the alternative)

1. **One reviewer from another lab for the first run, a second only on request.** Confidence moderate. The siblings' lesson: The Quiet Galaxy's first run with one reviewer gave John a usable rulings list, and the second lab's model is reachable only through its app, which John would have to run by hand. Alternative: two reviewers from the start (GPT through the ChatGPT app, as The Belt Equation did), at the cost of John's time on four app sessions before the first rulings list exists.
2. **The reviewer is called through the API, with a fixed model id, the reported version string filed, and Google Search lookup on.** Confidence high that the version must be filed and the key never written; moderate on the API over the app. The API gives a reproducible, pinned call that a later review can repeat on the same model, and lookup lets the reviewer check trials and approvals the record may have missed. Alternative: John in the Gemini app, at the cost of four sessions of his time and a model version the app does not state exactly.
3. **Four packets of two branches each rather than one per treatment, one per branch or one for all 44.** Confidence moderate; a judgment about depth against length. Two branches a packet keep each prompt under about 25,000 words so the reviewer can answer every treatment with care, and the reviewer sees a treatment's siblings on its branch, whose ranges should be consistent with it. Alternative: eight packets, one per branch, sharper answers and twice the calls; or 44 calls, one per treatment, the sharpest answers and no view of a branch's consistency. Take the eight-packet form if any treatment gets a shallow answer.
4. **Thresholds: three years at the likely or the earliest, ten at the latest.** Confidence low to moderate; a judgment about signal against noise, with no standard to follow. Moving one treatment's likely year by two moves the headline by less than its run-to-run noise, because a branch is handled at its second treatment and the headline is the latest of eight; ten years at a latest moves the tail only. Alternative: no threshold, file every difference, which buries the real disagreements under quibbles about a year.
5. **The stages are not reopened.** Confidence high. A stage is a matter of record (a paper, an approval, a registry entry), the weekly reading checks it, and the 2026-10-17 verification cleared every open statement; asking a reviewer to relitigate records would spend its attention where the site has already done the work. The ranges are the judgment, and the review is of the judgment. Alternative: ask anyway and file the answer as information; cheap, but it invites the reviewer to argue a fact instead of a range.
6. **The lag and independence questions are put in every packet, not in a packet of their own.** Confidence moderate. The lag differs by kind of treatment (a pill, a gene therapy, a transplant), so four answers, each from a reviewer looking at two branches' treatments, give the per-branch evidence that a lag per branch would need; and the independence question can be answered from any packet because every packet carries the table of all eight branches. Alternative: one fifth packet for the method alone, one answer with no treatments in view, cheaper to read and thinner.
7. **Packets generated from the records by a script.** Confidence high; standard practice, and what both siblings do. Alternative: hand-written packets, which drift from the records between the writing and the sending.
8. **The review changes nothing itself; the rulings list carries recommended rulings and the headline they would give, from a scratch copy.** Confidence high. It is the kickoff's rule (nothing promoted before John rules), the CLAUDE.md rule (every range changes only by John's ruling with a dated reason and a source) and the verification rule (nothing public rests on a model's recollection, so a reviewer's unsourced figure cannot enter the record either). Alternative: land the recommended rulings on a branch for John to merge, which puts the changes one click away but mixes the reviewer's items, Claude's view and John's ruling in one diff.
9. **Filed documents named by date, packet and model; the rulings list by date.** Confidence high; it is the siblings' naming and sorts by date in a listing. No real alternative.
