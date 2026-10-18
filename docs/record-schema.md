# Record schema and data format

Drafted 2026-10-16 (weekend step 2 of `docs/2026-10-16-kickoff.md`) and **PROPOSED, not yet ruled**: Claude proposed the layout below with a confidence level and the strongest alternative for each choice, recorded at the end under "Decisions", per the ground rule John set on 2026-09-08. Until John rules, this document is what `scripts/compute.py validate` enforces, and every choice in it is open to him. Three choices depart from the kickoff document and say why (decisions 2, 4 and 11). A change to the layout is a new proposal, made the same way.

The shape is The Quiet Galaxy's (`quiet-galaxy/docs/record-schema.md`, ruled by John 2026-10-16): one TOML file per record, ids that are also public addresses and are never renamed, world dates as text and project dates as TOML dates, top-level fields before tables, unknown fields refused, a retired-ids list, and a verify list on every record. The stage ladder is The Upgrade Tree's (`upgrade-tree/docs/upgrade-schema.md`), keys and all, so the two records can point at each other.

## What a record is

The data is the project. There are six kinds of record, under `data/`:

| Kind | Where | What one record is | Its id is also |
|---|---|---|---|
| branch | `data/branches.toml`, one `[[branch]]` table each | One of the eight fixed branches: a kind of damage repair would have to address, or the measuring branch | the branch page address (`/branches/worn-out-cells/`) |
| leaf | `data/leaves/<id>.toml` | One specific treatment, result or measuring tool that would have to arrive, with its test, its settler, its stage and the project's estimate of when it reaches the clinic | the leaf page address (`/leaves/drug-clears-aged-cells-from-a-person/`), **never renamed** |
| claim | `data/claims/<id>.toml` | One thing a named person or company said in public about when, with the primary source and a verdict as dates pass | the anchor on the claims page |
| experiment | `data/experiments/<id>.toml` | One public self-experiment someone else runs: what they do, measure and claim, and what the public record shows | the anchor on the self-experiments page |
| publication | `data/papers/<id>.toml` | One scientific paper, trial report or regulator's record that bears on a leaf or a branch, in an append-only log | the citation key other records link with |
| scan | `data/scans/<id>.toml` | One weekly reading of every leaf, claim and self-experiment against the week's news, with the searches made and a verdict per record (widened 2026-10-17; decision 18) | the anchor on "This week's reading" |

A seventh file, `data/retired.toml`, lists ids that once existed and were retired or replaced. It is how an id is taken out of service without ever being renamed.

The links between the six kinds point one way, and nothing is stored in two places. A leaf names its branch and, where one exists, its sibling on The Upgrade Tree. A claim names the leaves or branches it bears on (or says it is about the headline itself). A self-experiment names the leaves or branches it tries. A publication names the leaves or branches it bears on. A reading names, in each of its items, the leaf, claim or self-experiment it read, and the publications it logged. A page for a leaf gathers the claims, self-experiments, publications and readings that point at it; a branch page gathers its leaves and everything that points at the branch.

## File format and layout

TOML, one file per record, read by Python's standard library (`tomllib`, present since Python 3.11; this Mac has 3.14). Plain text, allows comments, one field per line so a change to one number is a one-line diff, multi-line text for the paragraphs. The same choice The Belt Equation made on 2026-09-08 and both siblings followed on 2026-10-16.

    data/
      branches.toml                   the eight branches, in order, each a [[branch]] table
      retired.toml                    ids that once existed and were retired or replaced
      leaves/
        drug-clears-aged-cells-from-a-person.toml     one file per leaf, named for its id
        ...
      claims/
        kurzweil-2029-escape-velocity.toml            one file per claim: who, year, topic
        ...
      experiments/
        bryan-johnson-blueprint.toml                  one file per public self-experiment
        ...
      papers/
        hickson-2019.toml                             one file per paper: first author and year
        ...
      scans/
        2026-10-17.toml                               one file per weekly reading, named for its date (the
                                                      siblings call this folder readings/; the kickoff named
                                                      it scans/ and the scripts and the site followed, so it stays)

**Ids.** Every record has an `id` (a branch has a `key`, which is the same thing): lowercase letters, digits and single dashes, like `drug-clears-aged-cells-from-a-person` or `hickson-2019`. The file is named `<id>.toml`, and the validator refuses a file whose name and id disagree: that is the first guard against renaming. Ids are unique across all six kinds, so a link is never ambiguous. Leaf ids say what happens, in plain words, and carry no branch prefix (decision 3). Claim ids are the speaker, the year the claim is about or was made, and a word for the topic. Publication ids are the first author's surname and the year, with a word added when two collide (`hickson-2019-senolytics`). Scan ids are the reading's date.

**Dates.** A date the project writes (when an estimate was set, when a paper was logged, when a reading ran, when a revision was made, when a verdict was given) is a TOML date, `2026-10-16`. A date the world supplies (when a stage was reached, when a paper appeared, when someone said something, when a self-experiment started) is text, because old records often have only a year or a year and month: `"2004"`, `"2019-09"` or `"2019-09-18"`, nothing else.

**Top-level fields come before the first table.** In TOML, anything written after a `[estimate]` or `[[revision]]` header belongs to that table, so `verify` and `notes` written at the bottom of a file silently become fields of the last table and fail as unknown. Write them before the first table header; the worked examples do.

**Unknown fields are refused.** A field not listed below fails validation, so a misspelt field name is caught instead of silently ignored, and so a field for John's own health cannot arrive by accident (decision 12 of the kickoff).

**Three fields every kind may carry.** `verify`: a list of plain-language claims in the record that were written from memory and not checked against a source at the time; a later session clears each by checking it and either deleting the line or correcting the record; the weekly reading reads the list but may not edit it (the Belt Equation rule of 2026-10-06; a search that settles a listed fact becomes a flagged item, `docs/weekly-reading.md`). `notes`: anything else worth keeping. `example`: `true` on a record that is a worked example of the layout and not yet a record of the world; the site counts examples separately and never shows an example reading as the site's reading (decision 13). An example that becomes real has the field removed; one that is replaced is deleted and its id retired.

## Writing for visitors (ruled by John 2026-10-18)

John ruled on 2026-10-18 that anything on the public site is a public version of the internal record: git keeps the raw text, and the site shows only what has passed through a presentation he has discussed. Most of a record's text is printed on a page as it stands, so the record's prose is written for the visitor from the start.

**Who it is for.** Every line of prose the site prints is written for a visitor who has never seen the repository, the procedures or the conversations behind them. That covers every record's `notes`; a leaf's revision reasons (`why`) and its estimate's reasoning; a claim's `verdict_why`; a publication's `finding`; and a reading's `summary`, `limits`, later notes, and each item's `found`, `for_john`, `resolved_by`, `search_short` and `reused` lines. Plain words, UK spelling, no em dashes, absolute dates.

**What it may not contain.** No internal names: not "leaf", "node", "trunk", "scan", "ledger", "schema", "settler", "session", "batch", "first pass" or "the master session". No file names or paths (`docs/…`, `data/…`, `CHANGELOG.md`), no field names (`stage_record`, `verify`, `for_john`, `estimate.rung…`), no record ids (`grifols-2026`, `hickson-2019`), no ladder keys (`in-clinical-use`; write "in clinical use"), no commit codes, no numbered references to a document the visitor cannot see ("item 13", "decision 19", "the rulings document"), and no all-capital markers ("FOR JOHN", "RULED").

**How to refer to things, in plain words with a date.**

- A review: "an outside review on 2026-10-17 argued that … ; John ruled on 2026-10-17 that …". Say what the review argued, not where it is filed.
- A ruling: "John ruled on 2026-10-18 that …".
- A reading: "the weekly reading of 2026-10-17 found …"; a question it left open: "the weekly reading of 2026-10-17 left this for John to decide: …".
- Another record: by what it is and who made it. A paper or release as its authors or maker and its date ("the supplier's announcement (Grifols, 2026-03-12)", "the 2019 trial report by Hickson and colleagues"); a treatment by its name; a claim by who said it and when; a self-experiment by its person.
- A fact not yet checked: "not yet checked against a source", not "in the verify list".
- A dated change to the records: "the change to the records on 2026-10-17", not a changelog entry or a commit.

**What stays exactly as it is.** Every fact, date, number, name, quotation and source. A rewrite changes wording and never a fact. The search queries are printed as they were run, because logging every search is the family's transparency rule (tracker pattern, rule 5.4); a `reused` line still quotes its search exactly as written in `queries`, which the validator checks, and names the other record in words. A revision's `old` and `new` are the record of what a field held, and stay as written; the site prints them for a stage, a date, a link or a year, and for a changed paragraph says only that the paragraph changed, beside the reason. A `test` is never edited once published, so a ladder key written into one ("the first-human rung") is shown by the site in words; four tests written before this rule still say "leaf", and only John can rule on rewording a test.

The existing notes, reasons and reading lines were rewritten once in this voice on 2026-10-18, wording only, with git keeping the text as first written. That includes the two readings of 2026-10-17 and 2026-10-18, which are otherwise written once and never edited; the queries, verdicts, sources and counts in them did not change.

## The stage ladder

Five rungs, The Upgrade Tree's, in order. A leaf sits on the highest rung it has reached, and the rung never moves down: a withdrawal is a status and a note.

| key | shown as | what it means |
|---|---|---|
| `idea-only` | Idea only | Proposed or worked on, but not yet shown to work in any living animal. |
| `shown-in-animals` | Shown in animals | Shown to work in a living animal, in a peer-reviewed report. |
| `first-human` | First human | At least one person has had it, with a public record of that result. |
| `in-clinical-use` | In clinical use | A regulator somewhere has approved it, or it is in routine use in a named clinical setting, so a doctor can give it to a patient outside a trial. |
| `in-wide-use` | In wide use | Available to the general public in at least one country without joining a trial, and taken up by many people. |

The rung the headline reads is `in-clinical-use`: the year each leaf reaches it is what the computation draws or reads (see "How a leaf's state feeds the headline").

## The twelve hallmarks and the eight branches

The published science groups ageing into twelve "hallmarks" (López-Otín and colleagues, 2023; nine in their 2013 paper). The branches group them so that a reader can check nothing was dropped. The keys below are the script's; each hallmark belongs to exactly one branch, and the validator refuses a `branches.toml` in which one is missing or doubled.

| hallmark key | the hallmark, in plain words | branch |
|---|---|---|
| `genomic-instability` | mutations accumulating in DNA | `damaged-dna` |
| `telomere-attrition` | the shortening of chromosome ends | `damaged-dna` |
| `epigenetic-alterations` | drift in the marks that say which genes a cell reads | `cell-settings` |
| `loss-of-proteostasis` | misfolded proteins and failed protein quality control | `broken-proteins` |
| `disabled-macroautophagy` | the cell's recycling of its own worn parts failing | `broken-proteins` |
| `deregulated-nutrient-sensing` | the pathways that sense food running wrong | `energy-and-fuel` |
| `mitochondrial-dysfunction` | the cell's power plants failing | `energy-and-fuel` |
| `cellular-senescence` | cells that stop dividing but will not die, and poison their neighbours | `worn-out-cells` |
| `stem-cell-exhaustion` | the reserve of cells that replace lost tissue running out | `replacing-parts` |
| `altered-intercellular-communication` | the signals cells send each other going wrong | `inflammation-and-signalling` |
| `chronic-inflammation` | low-grade inflammation that never switches off | `inflammation-and-signalling` |
| `dysbiosis` | the gut's community of microbes going out of balance | `inflammation-and-signalling` |

The eighth branch, `measuring-age`, groups no hallmark: it is the tools that say whether anything worked. Cross-links between proteins, which the kickoff lists under broken proteins, are not one of the twelve and appear in that branch's `meaning`, not in its hallmark list.

## The branch record (`data/branches.toml`)

Eight `[[branch]]` tables, in order. The eight keys are fixed in the script; a file with a ninth, or without one of the eight, fails.

| Field | Required | Meaning |
|---|---|---|
| `key` | yes | One of `worn-out-cells`, `damaged-dna`, `cell-settings`, `broken-proteins`, `energy-and-fuel`, `replacing-parts`, `inflammation-and-signalling`, `measuring-age`. Also the branch page address. |
| `order` | yes | 1 to 8; must match the key (the script holds the table). |
| `name` | yes | The plain name shown on the site. |
| `meaning` | yes | One or two sentences on what the branch covers, for a reader who has never heard of it. |
| `hallmarks` | yes | List of hallmark keys from the table above; `[]` for the measuring branch. |
| `required` | yes | `true` if the escape year cannot arrive until this branch is handled. The kickoff marks the measuring branch required; the first pass marks all eight (see the file). |
| `handled_when` | yes | A whole number, at least 1: how many of its leaves must be in clinical use for the branch to count as handled in a run. The kickoff's default is 2. |
| `what_would_move_this` | no | One line, hand-written, for the branch page until the computed list exists (tracker pattern, rule 2.3). |
| `verify`, `notes`, `example` | no | As above. |

## The leaf record

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | The page address, never renamed once committed. Retire it in `data/retired.toml` instead. |
| `name` | yes | Plain-language name that says what happens, not what it is called: "A drug clears aged cells from a person", not "senolytic therapy". |
| `branch` | yes | One of the eight branch keys. |
| `description` | yes | Two to four sentences: what this is and why it is on the tree, for a reader who has never heard of it. |
| `test` | yes | What would count as this having happened, written so that two readers agree. Swallowing the pill is not the leaf; the result is. The site calls this "what would count". Never edited once a stage or an estimate has been published against it; a leaf that needs a different test is retired and replaced (tracker pattern, rule 3.1). |
| `settler` | yes | Who or what settles the test: the peer-reviewed report, the regulator's approval record, the trial registry. "Common knowledge" and a press release are not settlers. |
| `stage` | yes | One of the five ladder keys. |
| `stage_reached_on` | unless idea-only | When the current stage was reached, as text: a year, year-month or full date. |
| `stage_record` | unless idea-only | A link to the public record that settles the current stage. |
| `stage_publication` | no | The id of the publication record that is that record, which must exist. |
| `[[earlier_stage]]` | no | One per rung below the current one whose date and record are known. Fields: `stage` (a rung below the current one), `reached_on` (text date), `record` (link), `publication` (no; an id that must exist). |
| `status` | yes | `"tracked"` (live) or `"withdrawn"` (the treatment left the market or the clinic; the stage stays, and `notes` says what happened). |
| `horizon` | yes | How soon the next rung could be reached: `"near"` (within 1 to 5 years), `"mid"` (5 to 20), `"far"` (longer, if ever) or `"top"` (already in wide use, so there is no next rung; allowed only at that stage). The Upgrade Tree uses `leaf`, `mid`, `root` and `top` for the same four; decision 6 says why the words differ. |
| `long_shot` | no | `true` for a leaf that current biology, engineering or physics does not yet allow. |
| `mechanism` | long shots | The believable sequence of steps from here to there, each named in order. |
| `breaking_point` | long shots | Where current biology, engineering or physics would have to give way, stated plainly. |
| `sibling` | no | The id of the matching entry on The Upgrade Tree (its `data/lifespan.toml`), for the five shared leaves. A slug; the weekly reading compares the two stages and files a reading on both sites when they disagree. |
| `[estimate]` | unless in clinical use or beyond | The project's estimate of when the remaining rungs are reached; the one thing on the leaf that is a judgment rather than a record. Fields: `status` (`"first-pass"` until the outside review has run, then `"reviewed"`), `set_on` (a TOML date), `why` (the reasoning in plain words, naming the evidence it rests on), `sources` (no; publication ids that must exist), and one or more `[[estimate.rung]]` tables, each with `rung` (a ladder key above the current stage), `earliest`, `likely` and `latest` (whole years, `earliest <= likely <= latest`, `earliest` no earlier than the year of `set_on`, `latest` no later than 2300; a `latest` beyond 2100 means "perhaps not this century"). A leaf below `in-clinical-use` must carry a rung for `in-clinical-use`, because that is the rung the headline reads. A leaf already in clinical use may carry an estimate for `in-wide-use` and need not. |
| `[[revision]]` | no | One per change to any field after the file's first commit, newest last. Fields: `date` (TOML date), `field`, `old`, `new`, `why` (all yes), `publication` (no; an id that must exist). A stage change and an estimate change always get one. |
| `verify`, `notes`, `example` | no | As above. |

### How a leaf's state feeds the headline (proposed)

The computation needs one thing from every tracked leaf: the year it reaches `in-clinical-use`. The state supplies it two ways:

- **A leaf at `in-clinical-use` or `in-wide-use` has a known year**: the year in `stage_reached_on` when the stage is `in-clinical-use`, or the year in the `earlier_stage` entry for `in-clinical-use` when the stage is `in-wide-use` (if that entry is missing, the year the current stage was reached is used as the latest it could have been, and the validator does not insist on the entry). What has happened is not drawn.
- **A leaf below `in-clinical-use` has a drawn year**: each run draws from the triangle over the `in-clinical-use` rung's `earliest`, `likely` and `latest`, so the likely year is the most probable draw and the two ends are possible but rare. The current stage does not change the draw beyond what the estimate already says: a leaf at idea only should have a wider, later range than one in a first human, and the `why` says so.

Withdrawn leaves still count if they reached the clinic (the stage is what happened); a leaf retired to `data/retired.toml` does not count at all. The rest of the method (how branch years combine, the lag, the fixed dates) is in `docs/method.md`.

Confidence: moderate; a judgment call. The strongest alternative is for every leaf, reached or not, to carry a probability per year as The Belt Equation's events do, with the stage as a floor; that is more expressive and harder to argue about in public, and the kickoff chose ranges for that reason. Second alternative: draw from a bell curve centred on `likely` with the ends as two standard deviations; smoother, but a bell curve never says "no earlier than", and the earliest year on a treatment with no human result is a real floor.

### Worked example: `data/leaves/drug-clears-aged-cells-from-a-person.toml`

Abridged; the file in `data/` has the full text. One of the five leaves shared with The Upgrade Tree, so it carries a `sibling`.

    id = "drug-clears-aged-cells-from-a-person"
    name = "A drug clears aged cells from a person"
    branch = "worn-out-cells"
    description = """
    Some cells stop dividing but do not die ... """
    test = """
    A person given a drug meant to kill senescent (aged, non-dividing) cells afterwards has
    measurably fewer of them in a tissue sample or a validated blood marker, compared with before
    treatment, in a peer-reviewed report. For the clinic rung: a regulator approves such a drug
    for an age-related condition, or it is in routine use in a named clinical setting."""
    settler = "Peer-reviewed trial reports; a regulator's approval record for the clinic rung"
    stage = "first-human"
    stage_reached_on = "2019-09-18"
    stage_record = "https://doi.org/10.1016/j.ebiom.2019.08.069"
    stage_publication = "hickson-2019"
    status = "tracked"
    horizon = "mid"
    sibling = "lifespan-a-drug-clears-aged-cells-from-a-persons-body"

    verify = [
      "The 2011 mouse result's date (2 November 2011) and the 2019 trial report's date are copied from The Upgrade Tree's record and not re-checked here.",
    ]

    [[earlier_stage]]
    stage = "shown-in-animals"
    reached_on = "2011-11-02"
    record = "https://doi.org/10.1038/nature10600"

    [estimate]
    status = "first-pass"
    set_on = 2026-10-16
    why = """
    A first human result on a measurement exists since 2019, but the one company drug to reach a
    controlled trial on a clinical outcome failed in 2020, and no senolytic is approved anywhere ... """

    [[estimate.rung]]
    rung = "in-clinical-use"
    earliest = 2031
    likely = 2038
    latest = 2060

When the estimate moves, the file gains a revision such as:

    [[revision]]
    date = 2027-03-14
    field = "estimate.rung.in-clinical-use.likely"
    old = 2038
    new = 2035
    why = "A phase 3 trial of a senolytic in knee osteoarthritis read out positive on its primary endpoint."
    publication = "example-2027"

## The claim record

The claims log is talk, set against delivery (tracker pattern, section 6). It sits beside the headline and moves no number.

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | The speaker, the year, a word for the topic: `kurzweil-2029-escape-velocity`. |
| `who` | yes | The person or organisation, as named. |
| `who_is` | yes | One line introducing them, for a reader who has never heard of them ("the inventor and futurist Ray Kurzweil"). |
| `said_on` | yes | When it was said, as text: year, year-month or full date. Talk is dated by when it was said. |
| `where` | yes | The primary source in words: the book and page, the recording and its timestamp, the company's own release. News coverage is coverage, named in `notes` if at all, never the source. |
| `link` | no | Where to find the source. |
| `quote` | yes | The words, as they appear in the source. |
| `is_paraphrase` | no | `true` when the exact words are not in hand and `quote` is the version that circulates. A paraphrase is never promoted because many outlets carry it (tracker pattern, rule 6.3). |
| `paraphrase_seen_in` | if paraphrase | Where the circulating version was seen. |
| `commits_to` | yes | In plain words, the date or result the claim commits to, so the verdict can be given. |
| `due` | if not yet due | The year by which the claim can be judged. |
| `leaves` | one of these three | List of leaf ids the claim bears on. |
| `branches` | one of these three | List of branch keys it bears on. |
| `about_the_headline` | one of these three | `true` for a claim about escape velocity itself rather than any one leaf or branch. At least one of the three. |
| `verdict` | yes | `"not-yet-due"`, `"delivered"`, `"missed"` or `"unfalsifiable"` (no date or result that could ever settle it). A result claim its maker later withdrew is recorded as `missed` (ruled by John, 2026-10-17). |
| `verdict_on`, `verdict_why` | if delivered or missed | The TOML date the verdict was given and the reason, naming the record it rests on. |
| `verify`, `notes`, `example` | no | As above. |

### Five rulings on judging and sourcing a claim (John, 2026-10-17)

Raised by the session that wrote the first thirty claims, put to John by the master session, and ruled in his words: "withdrawn claim stays missed, far-future claims keep their honest due year as not yet due, undated claims score at 2050, coverage-only entries shown and marked, a printed question-and-answer interview counts as primary."

1. **A result claim its maker later withdrew keeps the verdict `missed`.** The claim as made was not delivered; the withdrawal is the record of that.
2. **A claim no reader can live to check keeps its honest `due` year and the verdict `not-yet-due`**, not `unfalsifiable`. It can be settled, just not by us.
3. **A standing claim with no date is scored against the project's fixed 2050 date**, and the entry says so in `commits_to`.
4. **An entry held on coverage only is shown on the public page, marked plainly as such.** Hiding it would hide the repeated versions the project exists to check.
5. **A written interview is a primary source when the answers are printed as the speaker's own words in question-and-answer form**; where the writer has rephrased them, it is coverage and the paraphrase rule applies.

### Worked example: `data/claims/kurzweil-2029-escape-velocity.toml`

Abridged; the file in `data/` has the full text. The id keeps the famous year, 2029, because ids are never renamed; the book itself says "by around 2030", and the record is dated and worded from the book. The quotation is exact, so it is not marked as a paraphrase.

    id = "kurzweil-2029-escape-velocity"
    who = "Ray Kurzweil"
    who_is = "the inventor and futurist Ray Kurzweil, a director of engineering at Google and the author of The Singularity Is Near (2005) and The Singularity Is Nearer (2024)"
    said_on = "2024-06-25"
    where = "The Singularity Is Nearer (Viking, 2024), page 192, in the chapter on health and longevity; read in Google Books' search-inside snippets on 2026-10-16, which show the sentence but not the whole page"
    link = "https://books.google.com/books?id=V-e8EQAAQBAJ&q=%22by+around+2030%22"
    quote = "by around 2030, the most diligent and informed people will reach \"longevity escape velocity\""
    is_paraphrase = false
    commits_to = "Longevity escape velocity, defined on the same page as adding more than a year of remaining life expectancy per calendar year, reached by around 2030 for the most diligent and informed people; and disease and the ageing process largely overcome by the end of the 2030s."
    due = 2030
    about_the_headline = true
    verdict = "not-yet-due"

    verify = [
      "The sentence was read in snippet view, so the words immediately before it on page 192 were not seen; check against a copy of the book.",
      "The publication date, 2024-06-25, is the publisher's e-book date; the hardcover date was confirmed only from a bookseller's listing.",
    ]
    notes = """
    The famous version is 2029. The book's longevity pages do not use that year; the 2029 figure
    comes from interviews around the book's launch, which are coverage ... """

A claim whose exact words are not in hand would instead carry `is_paraphrase = true` and a `paraphrase_seen_in` line saying where the circulating version was seen.

## The self-experiment record

Other people's public self-experiments. The one line the site repeats everywhere: a claim about one person is a story, not a record, and it moves no leaf. The schema makes that structural: there is no stage, estimate or range field here, and the validator says so plainly if one appears. John's own track is not in this record in version one, by his ruling of 2026-10-16.

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | The person and the programme: `bryan-johnson-blueprint`. |
| `who` | yes | The person, as named. |
| `who_is` | yes | One line introducing them. |
| `name` | no | What the programme is called, if it has a name. |
| `started` | yes | When it began, as text: year, year-month or full date. |
| `status` | yes | `"running"` or `"ended"`. |
| `ended` | if ended | When, as text. |
| `what` | yes | What they do, in a paragraph. |
| `measures` | yes | What they measure and publish, in a paragraph. |
| `claims` | yes | What they claim it has done, in their terms. |
| `public_record` | yes | What the public record actually shows, in a paragraph: what is published, by whom, and what it does and does not establish. |
| `link` | yes | Their own publication of it: the site, the paper, the data. |
| `leaves` | one of these two | Leaf ids the experiment tries or bears on. |
| `branches` | one of these two | Branch keys it tries or bears on. At least one across the two. |
| `verify`, `notes`, `example` | no | As above. |

### Worked example: `data/experiments/bryan-johnson-blueprint.toml`

    id = "bryan-johnson-blueprint"
    who = "Bryan Johnson"
    who_is = "the technology entrepreneur Bryan Johnson, who sold a payments company in 2013 and since 2021 has spent a reported two million dollars a year on a published programme to slow his own ageing"
    name = "Blueprint"
    started = "2021"
    status = "running"
    what = """..."""
    measures = """..."""
    claims = """..."""
    public_record = """..."""
    link = "https://protocol.bryanjohnson.com/"
    branches = ["energy-and-fuel", "measuring-age"]

## The publication record

The publications log is append-only: a record is added when a paper is read and never edited afterwards except to fix an error, with a changelog line.

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | First author's surname and year, like `hickson-2019`. |
| `date` | yes | When it appeared, as text: year, year-month or full date. |
| `added_on` | yes | The date it was logged here (a TOML date). The log is read in this order. |
| `authors` | yes | List of names, as they appear on the paper. |
| `title` | yes | The paper's title. |
| `venue` | yes | Journal, preprint server, registry or regulator, with volume and pages where they exist. |
| `link` | yes | Where to read it. |
| `finding` | yes | One or two plain sentences on what it found or claimed, with the numbers that matter. |
| `leaves` | one of these two | List of leaf ids it bears on. |
| `branches` | one of these two | List of branch keys it bears on. At least one across the two. |
| `moved_range` | yes | `true` or `false`: did reading it move a leaf's estimate? If `true`, some leaf's revision log must carry a revision naming this publication. |
| `settled_stage` | yes | `true` or `false`: is it the record that settles a rung on some leaf? If `true`, some leaf's `stage_publication` or an `earlier_stage` entry's `publication` must name it. |
| `verify`, `notes`, `example` | no | As above. |

### Worked example: `data/papers/hickson-2019.toml`

    id = "hickson-2019"
    date = "2019-09-18"
    added_on = 2026-10-16
    authors = ["LaTonya J. Hickson", "Larissa G. P. Langhi Prata", "..." , "James L. Kirkland"]
    title = "Senolytics decrease senescent cells in humans: Preliminary report from a clinical trial of Dasatinib plus Quercetin in individuals with diabetic kidney disease"
    venue = "EBioMedicine 47, 446–456 (2019)"
    link = "https://doi.org/10.1016/j.ebiom.2019.08.069"
    finding = """
    Nine people with diabetic kidney disease took a three-day course of two drugs that kill
    senescent cells; eleven days later, samples of their fat and skin held fewer such cells ... """
    leaves = ["drug-clears-aged-cells-from-a-person"]
    moved_range = false
    settled_stage = true

## The scan record (the weekly reading)

Widened 2026-10-17 with the weekly reading itself (`docs/weekly-reading.md`; decision 18, ruled by John on 2026-10-17 as proposed) from the leaf-only layout of 2026-10-16. One file per reading, named for its date, written once and never edited. The reading proposes; a move is a dated stage revision on the leaf, and a reading that says a leaf moved must be matched by one. The procedure that writes it, the four verdicts, the caps and the limits on what a reading may do are in `docs/weekly-reading.md`.

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | The Pacific date the reading ran, `2026-10-24`, with `-2`, `-3` on a second or third run the same day. The file is named for it. |
| `read_on` | yes | The same date, as a TOML date. The strip on the home page shows it. |
| `covers_from` | yes | The first day of the news the reading covers (a TOML date, not after `read_on`): seven days before `read_on`, so a reading overlaps the previous one by a week (changed 2026-10-18, decision 22; the first two readings took the time since the last reading, or seven days when there was none). |
| `ran_at` | yes | When the reading finished, universal time, as text: `"2026-10-18T01:12:30Z"`. |
| `run_by` | yes | `"scheduled"` (the weekly cloud task) or `"hand"` (a session a person started). |
| `commit_before` | yes | The short commit the records were read at. |
| `leaves_read`, `claims_read`, `experiments_read` | yes | How many of each were read; each must equal the number of items naming that kind. |
| `searches` | yes | How many distinct searches were run across all items; the validator counts them. |
| `summary` | yes | One paragraph: what the week brought, what moved, what was logged, and what the reading could not do. |
| `limits` | no (asked of every reading from 2026-10-25) | Plain words, one to three sentences: how many pages were opened and of which kinds, which kinds were refused and what was done instead, that the search tool cannot limit results by date, and whether helper agents did the reading. The reading page prints it under the summary (decision 20, ruled by John 2026-10-18). |
| `[[later_note]]` | no | A dated note added after the reading, by a later dated batch and never by the reading itself, so that a statement in the reading's own words that turned out wrong can be corrected without editing the record. Fields: `date` (a TOML date, not before `read_on`) and `text` (plain words). It goes at the end of the file, after the items, and the reading page prints it under the summary (decision 21, ruled by John 2026-10-18). |
| `[[item]]` | at least one | One per record read, in the order read. Fields: exactly one of `leaf`, `claim` or `experiment` (an id that exists; no record twice); `verdict` (`"quiet"`: nothing in the window bears on the test; `"noted"`: something bears on it and was logged as a publication, and the test was not met; `"moved"`: a leaf only, moved one rung up on a record of the kind its settler names; `"flagged"`: something the reading may not decide, left for John); `queries` (at least two searches, each a line of text, including any listed again from another record; fewer only with `search_short`); `reused` (no; one line per search first run for another record, quoting it as written in `queries`, naming that record and saying why it bears on this one); `search_short` (no; one line saying why fewer than two searches of the record's own could be run); `found` (one to three plain sentences on what was found and why it got this verdict); `sources` (required for every verdict but quiet; links to public records); `publications` (required for noted; ids of publication records logged, which must exist; never on a quiet item); `moved_from` and `moved_to` (moved only; adjacent rungs of the ladder, matched by a `[[revision]]` on the leaf dated `read_on` with `field = "stage"`, `old = moved_from` and `new = moved_to`); `for_john` (required for flagged, and only there: the change the reading would have made, the record, and why it was not its to make); `resolved_on` and `resolved_by` (no; flagged items only, both or neither, added by a later dated batch and never by the reading itself: the date the item was dealt with, not before `read_on`, and one line saying what dealt with it and in which changelog entry; proposed 2026-10-17, decision 19); `sibling_stage` and `sibling_agrees` (no; only on a leaf with a `sibling`: the stage The Upgrade Tree shows for it this week, and whether the two agree). |
| `verify`, `notes`, `example` | no | As above. |

A reading need not cover every record: records added after a reading would otherwise make old readings fail, and a reading whose search tool ran out names what it could not read in its summary. The procedure says every tracked leaf, every claim and every self-experiment is read; the validator checks only that what was read exists.

### Worked example: `data/scans/2026-10-17.toml`

Abridged; the file in `data/` is the first reading, with 80 items. The worked example of 2026-10-16, in the earlier layout, was deleted the day the first reading landed and its id retired (`data/retired.toml`).

    id = "2026-10-17"
    read_on = 2026-10-17
    covers_from = 2026-10-10
    ran_at = "2026-10-17T16:08:12Z"
    run_by = "hand"
    commit_before = "23a12a3"
    leaves_read = 44
    claims_read = 27
    experiments_read = 9
    searches = 191
    summary = """
    The first weekly reading, run by hand on 2026-10-17, the day the site went live ... """

    [[item]]
    leaf = "clearing-aged-cells-makes-old-animals-live-longer"
    verdict = "quiet"
    queries = [
      "senolytic lifespan extension mice new study October 2026",
      "senescent cell clearance lifespan Nature Aging 2026 mice senolytic survival",
      "senolytic news this week October 2026",
    ]
    reused = ["senolytic news this week October 2026, first run for aged-cell-clearing-drug-beats-a-sham-in-a-controlled-trial; it asked for any senolytic news in the window and would have surfaced a lifespan result if one had been reported"]
    found = """
    Nothing in the window. Both searches returned only the 2016 engineered-mouse result and the 2018
    dasatinib-plus-quercetin result ... that the record already holds ..."""

    [[item]]
    leaf = "drug-clears-aged-cells-from-a-person"
    verdict = "flagged"
    queries = ["...", "...", "...", "..."]
    found = """
    Nothing dated in the window meets or moves the test; the leaf stays at first-human ... """
    sources = ["https://www.nature.com/articles/s42255-026-01643-4", "..."]
    for_john = """
    The change I would make: the description says the one drug to reach a controlled trial on a
    clinical outcome failed in 2020 ... The stage does not change ..."""
    sibling_stage = "first-human"
    sibling_agrees = true

A moved item would instead carry `moved_from = "shown-in-animals"` and `moved_to = "first-human"`, and the leaf a revision dated the reading's day:

    [[revision]]
    date = 2026-10-24
    field = "stage"
    old = "shown-in-animals"
    new = "first-human"
    why = "[reading 2026-10-24] A peer-reviewed report of the first person treated, with the measured result the test asks for."
    publication = "example-2026"

## The retired list

`data/retired.toml` holds a list `retired`, each entry with `id`, `kind` (`branch`, `leaf`, `claim`, `experiment`, `publication` or `scan`), `date` (a TOML date), `why`, and optionally `replaced_by` (an id that must exist). To retire a record: delete its file (or its table, for a branch), add the entry, and update every record that linked to it. The validator refuses a new record that reuses a retired id.

## Rules the validator enforces

`python3 scripts/compute.py validate` reads every record and refuses to continue on any failure, listing everything wrong in plain language.

1. Every file under the five record folders and `data/branches.toml` is valid TOML; every record has every required field with a non-empty value; every enumerated field has an allowed value; no record carries a field not listed above.
2. Ids are lowercase slugs, unique across all six kinds, and each file is named for its id. A scan's id equals its `read_on` date.
3. `data/branches.toml` holds exactly the eight branches, each once, with `order` matching the key; every one of the twelve hallmarks appears in exactly one branch; `handled_when` is a whole number of at least 1.
4. Every leaf has a `test` and a `settler`, a `branch` that is one of the eight, a `stage` on the ladder, a `status` and a `horizon`. A stage above idea-only has a `stage_reached_on` (a world date as text) and a `stage_record`. Every `earlier_stage` names a rung below the current one, with a date and a record. `horizon = "top"` only at `in-wide-use`. A long shot has a `mechanism` and a `breaking_point`.
5. A leaf below `in-clinical-use` has an estimate with a rung for `in-clinical-use`. Every estimate has a `status`, a `set_on` date and a `why`; every rung is above the current stage and listed once, with `earliest <= likely <= latest`, `earliest` no earlier than the year of `set_on`, and `latest` no later than 2300.
6. Every link between records resolves: a leaf's `branch`, `stage_publication`, `earlier_stage.publication`, `estimate.sources` and `revision.publication`; a claim's, experiment's and publication's `leaves` and `branches`; a reading's `leaf`; a retired entry's `replaced_by`.
7. Every claim has a primary source (`where`), a `quote`, a `commits_to` and a `verdict`; a paraphrase says where it was seen; a `not-yet-due` claim has a `due` year; a `delivered` or `missed` claim has `verdict_on` and `verdict_why`; and it bears on at least one leaf or branch or is about the headline.
8. Every self-experiment names at least one leaf or branch, and carries no stage, estimate or range (the plain message says a self-experiment moves no leaf).
9. Every publication names at least one leaf or branch. One with `moved_range = true` is named by a revision on some leaf; one with `settled_stage = true` is named as a stage record on some leaf.
10. Every reading's id is its `read_on` date (with `-2`, `-3` for a second or third run that day); `ran_at` is universal time as text, `run_by` is `hand` or `scheduled`, `commit_before` is a short commit; every item names exactly one leaf, claim or self-experiment that exists, no record twice; every verdict is one of the four; every item lists at least two searches or carries `search_short`, and a `reused` line quotes one of them; every verdict but quiet cites a source; a noted item names a publication that exists and a quiet item names none; a moved item is a leaf, moves exactly one rung, and is matched by a stage revision on that leaf dated `read_on` from `moved_from` to `moved_to`; a flagged item carries `for_john` and no other item does; `resolved_on` and `resolved_by` appear together, only on a flagged item, with the date not before `read_on` (proposed 2026-10-17, decision 19); `sibling_stage` appears only on a leaf that has a `sibling`; a `limits` line, where present, is not empty, and a `later_note` carries a date not before `read_on` and some text (2026-10-18); and `leaves_read`, `claims_read`, `experiments_read` and `searches` equal what the items hold. (Widened 2026-10-17; the rule of 2026-10-16 checked a leaf-only reading with five verdicts.)
11. No id is renamed: the file name must equal the id, and an id that was committed before and is now gone must have an entry in `data/retired.toml` (the script reads the repository's history for this, and skips the check with a note when the data folder is not in a git repository). A current record may not reuse a retired id.

`python3 scripts/compute.py run` validates first, refuses with a plain message until every branch has at least `handled_when` tracked leaves, and otherwise plays the tree out and writes `data/headline.json`. How it does that, and the parameters proposed for it on 2026-10-16, are in `docs/method.md`.

## Decisions (proposed 2026-10-16, ruled by John the same day)

Proposed by Claude with a confidence level and the strongest alternative for each, per the ground rule of 2026-09-08. Items 2, 4 and 11 depart from the kickoff document and say why. **Ruled by John on 2026-10-16:** "Accept all 17 record-layout choices and all 10 headline parameters for Outrunning Ageing as proposed, with the clinic-to-ordinary-people lag flagged for the outside review." This document is the source of truth for the record layout from that date; a change to it is a new proposal, made the same way.

1. **One TOML file per record, in five folders plus one branches file, named for the id.** High confidence: it is the siblings' format, the standard-library reader exists, a one-line diff per change, and the parallel record sessions can each write a folder without touching the others. Standard practice for a data-as-text project. Alternative: one file per kind, which is fewer files and makes every session edit the same file.
2. **Leaves are one file each under `data/leaves/`, not one file per branch (`data/<branch>.toml`) as the kickoff wrote and The Upgrade Tree does.** Moderate confidence; a judgment call. The brief for this step asked for the Quiet Galaxy shape, one file per record; a leaf is a public address with its own revision log, and the renamed-id check reads file names from git history, which works per file and not per table; and the one session writing forty leaves can still work branch by branch. Alternative: the kickoff's one file per branch, which keeps a branch's leaves together on disk at the cost of the history check and of forty leaves in eight files that every edit touches.
3. **Leaf ids are plain words with no branch prefix** (`drug-clears-aged-cells-from-a-person`, not `worn-out-cells-drug-clears-...` as The Upgrade Tree prefixes its ids). Moderate confidence; a judgment call. A leaf's branch is a field and could in principle move at a yearly review; an id that names the branch would then lie, and ids are never renamed. Alternative: The Upgrade Tree's prefix, which sorts a folder by branch for free and matches the sibling's habit.
4. **The estimate carries a range per remaining rung, and only the `in-clinical-use` rung feeds the headline.** Moderate confidence. The kickoff says the estimate covers "each remaining rung"; the computation reads one. Keeping the per-rung form honours the kickoff and lets the leaf page show when the author expects a first human; requiring only the clinic rung keeps the record honest about what is scored. On reflection Claude would be content with the clinic rung alone and no others, which is the alternative: simpler, and nothing is lost that the headline uses; it costs the leaf page its "first human expected around" line.
5. **A triangle over earliest, likely and latest is the draw** (see "How a leaf's state feeds the headline"). Moderate confidence; a judgment call. Alternative: a probability per year as The Belt Equation carries, or a bell curve. Written up above.
6. **The horizon's values are `near`, `mid`, `far` and `top`, not The Upgrade Tree's `leaf`, `mid`, `root` and `top`.** Moderate confidence; a judgment call about words. On a site whose records are called leaves, a horizon value called `leaf` would mean two things; the meanings are identical and the export can translate for the sibling check. Alternative: the Upgrade Tree's keys verbatim, for one less thing to translate.
7. **A `sibling` field on the five shared leaves, holding the Upgrade Tree's id, checked as a slug only.** High confidence that the field belongs here (the kickoff's item 7, accepted). Moderate on checking only the shape: the validator could read `../upgrade-tree/data/lifespan.toml` when it is on the same machine, but a build on GitHub has no sibling checkout, and a check that passes on one machine and skips on another is confusing. Alternative: a copied list of the five ids in the script, refreshed by hand; cheap, and stale the day the sibling adds a sixth.
8. **A claim carries the exact words, or a marked paraphrase with where it was seen, and a verdict from a fixed set of four.** High confidence; it is the tracker pattern's rule 6.3 and the kickoff's list of verdicts. Alternative: a free-text verdict, which cannot be totalled on the claims page.
9. **A claim may be about the headline itself** (`about_the_headline = true`) rather than any leaf or branch. Moderate confidence. The loudest promises ("escape velocity by 2029") are about the whole; forcing them onto one branch would misstate them. Alternative: require every claim to name a branch and let the headline claims name all eight; clumsy, and it would make the branch pages list promises that are not about them.
10. **The self-experiment record has no field that can move a leaf, and the validator says so in words if one appears.** High confidence; it is the kickoff's rule made structural (item 5 of "How it is built"). Alternative: allow a self-experiment to name a stage it claims to have reached, labelled as a claim; the claims log already does that job.
11. **A publication carries both `moved_range` and `settled_stage`, each cross-checked against the leaves.** High confidence on the cross-check, which is The Quiet Galaxy's rule 9 extended: on this site a paper can move two things, an estimate or a stage, and the log should say which. Alternative: a single `moved` field with three values; the same information with a less obvious check. This is the second departure from the kickoff, which lists only "whether it moved a range".
12. **A reading that says a leaf moved or met a rung must be matched by a revision on that leaf dated the same day.** Moderate confidence; a judgment call. It is the one guard that keeps "the weekly reading proposes, the leaf records" true in the data rather than in a procedure. Alternative: no cross-check and a procedure document; cheaper, and the first time a reading says "moved" without the leaf changing, the two records disagree in public.
13. **An `example` flag on any record, counted separately by the site and never shown as a reading.** Moderate confidence; a judgment call made while building. The brief asked for a worked example of each kind under `data/` and for the holding page's strip to say no reading has run; the one scan record cannot be both a reading and not a reading without a mark. The Upgrade Tree's seeded entries carried "EXAMPLE ENTRY" in their notes and its export counted them; a field is the same idea made checkable. Alternative: keep the scan example in this document only and leave `data/scans/` empty, which costs the validator and the export a test of the real layout.
14. **World dates are text (year, year-month or full date); project dates are TOML dates.** Moderate confidence; the siblings' rule. The Upgrade Tree writes stage dates as TOML dates; here they are text so that a stage known only to the month ("approved in 2015-07") need not invent a day. The sibling check converts. Alternative: TOML dates everywhere, which sorts for free at the cost of made-up days.
15. **Renamed ids are caught two ways: file name must equal id, and an id that was ever committed and is now gone must be in `data/retired.toml`.** High confidence on the rule, moderate on reading git history from the validator; both siblings do it. Alternative: a hand-kept registry.
16. **Unknown fields are refused**, and so no field for John's own health can arrive by accident. High confidence; standard practice for a strict validator, and the kickoff's item 12 made structural.
17. **The `verify` list is carried over from The Belt Equation.** High confidence; it is the mechanism behind the ground rule that facts from memory are marked.

### Proposed 2026-10-17, ruled by John 2026-10-17

18. **The scan record reads three kinds of record, carries the searches, and has four verdicts.** Proposed by the session that built the weekly reading (`docs/weekly-reading.md`), replacing the leaf-only layout of 2026-10-16 before any real reading had used it: each item names exactly one leaf, claim or self-experiment; it lists the searches run (two as a floor, with a `reused` line for a borrowed one and `search_short` when the tool gave out), what was found, the sources, the publications logged, the rungs of a move and the line for John; the header counts what was read and the validator checks the counts against the items; and the five verdicts become four (`quiet`, `noted`, `moved`, `flagged`), because the reading may not touch an estimate, so a move can only be a rung, and the siblings' word for "waiting on the author" is `flagged`. High confidence on the three kinds (the kickoff gives the claims log verdicts "filled in as dates pass" and the self-experiments a public record to hold against, which needs a weekly check) and on the counts and the searches (The Belt Equation's audit of 2026-10-06 made both rules, and the siblings carry them); moderate on folding `met` into `moved`, a judgment about words. Standard practice for this family. **Ruled by John on 2026-10-17, accepted as proposed, together with the weekly reading's schedule and caps (`docs/weekly-reading.md`).** Alternative: keep the layout of 2026-10-16 and read claims and self-experiments in a file outside the record kinds, which would leave the validator blind to two thirds of what the reading does. The folder stays `data/scans/`, as the kickoff named it, although the siblings use `data/readings/`; the cost of the difference is one word in the family's vocabulary, and the cost of changing it a retired id, three scripts and four documents.

### Proposed 2026-10-17, used with John's direction of 2026-10-18

19. **A flagged item may carry a resolution mark: `resolved_on` (a date) and `resolved_by` (one line).** Proposed by the session that fixed the home page's "5 left for the author" on 2026-10-17. The reading record is written once and never edited by the reading, but a flagged item is a request to the author, and the records move on after it: the dated batch of 2026-10-17 applied sixteen of the first reading's nineteen flagged items to the leaves and claims, and the layout had no way to say so. The site had been guessing: a treatment's item counted as cleared if any later revision's reason named the reading's date, and a claim's item only if its verdict had been dated since. So it called the five claim items still open, though the batch had updated all five, and it called three treatment items cleared that still wait on a ruling. With the mark, the site counts an item open until a person or a batch says in the reading's own record that it is not, with the date and the changelog entry that did it. Only the two fields are added; verdicts, searches and sources never change, and the validator refuses the mark on anything but a flagged item, on one half of the pair, or on a date before the reading. The site keeps the other way an item stops being open, a later reading that reads the same record with another verdict. The three items the batch left open, because each asks for a ruling the batch declined to make, are the telomere gene therapy's first-human question (the ZSCAN4 report), the plasma-exchange clinic rung and the young-plasma measure. **Confidence: high** that a mark is needed (the site cannot otherwise tell an applied item from an open one without guessing), **moderate** on putting it on the item. **A judgment call, not checked against the sibling sites' layouts.** **Strongest alternative:** a separate file of resolutions (`data/scans/resolutions.toml`), which keeps every reading file strictly untouched after it is written; the cost is a fourth record kind, a second reader in the export and a cross-check between the files, for a mark that only ever says "dealt with, on this date, by this entry". **Would I change it on reflection?** Possibly the name `resolved_by`, which reads as a person; `resolved_in` would name the changelog entry better. Not ruled by John as a layout; on 2026-10-18 he asked for the audit's thirteen items to be marked resolved this way, and they are.

### Ruled by John 2026-10-18, on the audit of the first scheduled reading

Proposed by the audit session (`docs/readings/audit-2026-10-18.md`, proposals 1 and 7, and the correction of the reading's public summary), ruled by John on 2026-10-18 as recommended.

20. **A reading record may carry a `limits` line.** The choice: one optional text field on the reading, asked of every reading from 2026-10-25, saying which pages were opened and refused and that the searches cannot be limited by date. **Confidence: high** that the record needs somewhere to say it, because the first scheduled reading's public summary said pages "could not be opened" when some had opened, and nothing in the record could show which. **A judgment call**, not checked against the sibling sites (The Quiet Galaxy's audit proposes the same field). **Strongest alternative:** put it in the `summary`, which needs no new field but cannot be checked or printed on its own line; the cost is that a summary written in a hurry leaves it out. **Would I change it on reflection?** Possibly make it required once there are a few readings that carry it.
21. **A reading record may carry dated later notes.** The choice: optional `[[later_note]]` tables (a date and text), added by a later dated batch, printed under the summary, so a wrong statement in the reading's own words is corrected without editing the record. **Confidence: moderate**; the reading stays as written and the correction sits beside it, which is the point, but a second place where a reader must look is a cost. **A judgment call.** **Strongest alternative:** edit the summary and say so in the changelog, which is simpler and loses the record of what the reading said. **Would I change it on reflection?** The name; `correction` would say more than `later_note`, but the field is not only for corrections.
22. **The window is always the seven days up to the reading.** The choice: `covers_from` is seven days before `read_on`, whatever the date of the last reading. **Confidence: moderate** (seven or fourteen days is a judgment); it is what the first scheduled reading did, it leaves no hole if a run is missed, and it costs only that a record the last reading logged is seen again and named. **A judgment call**, not checked against the siblings (The Quiet Galaxy's audit proposes fourteen). **Strongest alternative:** the day after the last reading, which is exact and was the procedure's rule; the cost is a one-day window, or a gap of weeks after a missed run, that makes a quiet reading true by construction.

## Known simplifications

- **The headline's parameters are in `docs/method.md`**, proposed with confidence and alternatives and not yet ruled: the triangle draw, the lag from the clinic to ordinary people, the fixed dates 2050 and 2100, the number of runs, the seed, and the readiness rule for `run`.
- **The estimate is set by hand with a written reason**, not computed from the publications. That is deliberate: the reason is the arguable part.
- **A reading covers what it covers.** The validator does not insist that every tracked leaf, claim or self-experiment was read, for the reason given under the scan record.
- **The sibling check is a weekly-reading procedure**, not a validator rule, for the reason in decision 7; the validator checks only that the sibling's stage, when written, is a rung on the ladder.
