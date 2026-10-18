// The typed view of the JSON the export script writes (scripts/export.py), plus the wording and
// the small helpers every page shares. Every page reads from here; nothing in the browser touches
// the TOML records. The file src/data/records.json is generated at build time and not committed:
// `npm run export` (or any build or dev run) writes it from ../data. Widened 2026-10-17 from the
// holding version's short forms to the full records the pages need.
import data from '../data/records.json';

export type StageKey = 'idea-only' | 'shown-in-animals' | 'first-human' | 'in-clinical-use' | 'in-wide-use';
export type Horizon = 'near' | 'mid' | 'far' | 'top';
export type Verdict = 'not-yet-due' | 'delivered' | 'missed' | 'unfalsifiable';
export type ReadingVerdict = 'quiet' | 'noted' | 'moved' | 'flagged';
export type ReadingKind = 'leaf' | 'claim' | 'experiment';
export type StoryKind = 'stage-settled' | 'moved-range' | 'held' | 'revision' | 'reading';

export interface Counts {
  branches: number;
  branches_expected: number;
  leaves: number;
  leaves_tracked: number;
  leaves_by_stage: Record<StageKey, number>;
  leaves_in_clinic: number;
  leaves_first_pass: number;
  long_shots: number;
  siblings: number;
  claims: number;
  experiments: number;
  publications: number;
  scans: number;
  scans_real: number;
  retired: number;
  verify: number;
  examples: number;
}

export interface Stage { key: StageKey; label: string; meaning: string; rank: number }

/** A short pointer at a leaf, resolved by the export so no page looks an id up. */
export interface LeafRef {
  id: string;
  name: string;
  path: string;
  branch: string;
  branch_name: string;
  stage: StageKey;
  stage_label: string;
  stage_rank: number;
  horizon: Horizon;
  status: 'tracked' | 'withdrawn';
  example: boolean;
}
export interface BranchRef { key: string; name: string; path: string }
export interface PublicationRef {
  id: string;
  title: string;
  date: string;           // a world date as text: "2019", "2019-09" or "2019-09-18"
  path: string;
  link: string;
  first_author: string;
  authors_short: string;
  settles_rung?: string | null;  // on a leaf page: the rung this paper is the record of, if any
}
export interface ClaimRef {
  id: string;
  who: string;
  said_on: string;
  commits_to: string;
  due: number | null;
  verdict: Verdict;
  verdict_label: string;
  path: string;
}
export interface ExperimentRef {
  id: string;
  who: string;
  name: string;
  started: string;
  status: 'running' | 'ended';
  path: string;
}

export interface Branch {
  key: string;
  order: number;
  name: string;
  meaning: string;
  hallmarks: { key: string; words: string }[];
  required: boolean;
  handled_when: number;
  what_would_move_this: string;
  notes: string;
  leaves: number;
  leaves_tracked: number;
  counts_by_stage: Record<StageKey, number>;
  in_clinic: number;
  furthest_stage: StageKey | null;
  furthest_label: string | null;
  furthest_rank: number | null;
  median_handled_year: number | null;   // from the computed headline, when it exists
  leaf_refs: LeafRef[];
  claims: ClaimRef[];
  experiments: ExperimentRef[];
  publications: PublicationRef[];
  path: string;
}

export interface Rung {
  key: StageKey;
  label: string;
  reached: boolean;
  current: boolean;
  reached_on: string | null;
  record: string | null;
  publication: PublicationRef | null;
}
export interface EstimateRung {
  rung: StageKey;
  rung_label: string;
  earliest: number;
  likely: number;
  latest: number;
  feeds_headline: boolean;
}
export interface Estimate {
  status: 'first-pass' | 'reviewed';
  set_on: string;
  why: string;
  sources: PublicationRef[];
  rungs: EstimateRung[];
}
export interface Revision {
  date: string;
  field: string;
  old: unknown;
  new: unknown;
  why: string;
  publication: PublicationRef | null;
}
// One record's line in a weekly reading, as a leaf, claim or self-experiment page shows its last three.
export interface LeafReading {
  read_on: string;
  path: string;
  verdict: ReadingVerdict;
  verdict_label: string;
  found: string;
  sources: string[];
  search_short: string;
  for_john: string;
  resolved_on: string | null;
  resolved_by: string;
  moved_from_label: string | null;
  moved_to_label: string | null;
  publications: PublicationRef[];
}

export interface Leaf {
  id: string;
  name: string;
  path: string;
  branch: string;
  branch_name: string;
  branch_path: string;
  description: string;
  test: string;
  settler: string;
  stage: StageKey;
  stage_rank: number;
  stage_label: string;
  stage_reached_on: string | null;
  stage_record: string | null;
  stage_publication: PublicationRef | null;
  ladder: Rung[];
  status: 'tracked' | 'withdrawn';
  horizon: Horizon;
  horizon_words: string;
  horizon_label: string;
  long_shot: boolean;
  mechanism: string;
  breaking_point: string;
  sibling: string | null;
  sibling_url: string | null;
  estimate: Estimate | null;
  estimate_status: 'first-pass' | 'reviewed' | null;
  clinic_year: number | null;   // known, for a leaf already in the clinic
  headline_draw: { known: boolean; year: number | null; earliest: number | null; likely: number | null; latest: number | null } | null;
  revisions: Revision[];
  verify: string[];
  notes: string;
  example: boolean;
  claims: ClaimRef[];
  experiments: ExperimentRef[];
  publications: PublicationRef[];
  readings: LeafReading[];   // the last three real weekly readings of this leaf
  file: string;
}

export interface Claim {
  id: string;
  who: string;
  who_is: string;
  said_on: string;
  where: string;
  link: string | null;
  quote: string;
  is_paraphrase: boolean;
  paraphrase_seen_in: string;
  commits_to: string;
  due: number | null;
  verdict: Verdict;
  verdict_label: string;
  verdict_on: string | null;
  verdict_why: string;
  about_the_headline: boolean;
  leaves: LeafRef[];
  branches: BranchRef[];
  verify: string[];
  notes: string;
  readings: LeafReading[];   // the last three weekly readings of this claim (not yet shown on the page)
  example: boolean;
  file: string;
  path: string;
}
export interface ClaimsCounts {
  claims: number;
  speakers: number;
  by_verdict: Record<Verdict, number>;
  about_the_headline: number;
  coverage_only: number;
  to_verify: number;
  first_year: string | null;
  last_year: string | null;
}

export interface Experiment {
  id: string;
  who: string;
  who_is: string;
  name: string;
  started: string;
  status: 'running' | 'ended';
  ended: string | null;
  what: string;
  measures: string;
  claims: string;
  public_record: string;
  link: string;
  leaves: LeafRef[];
  branches: BranchRef[];
  verify: string[];
  notes: string;
  readings: LeafReading[];   // the last three weekly readings of this self-experiment (not yet shown on the page)
  example: boolean;
  file: string;
  path: string;
}

export interface SettledRung extends LeafRef { rung: StageKey; rung_label: string }
export interface MovedRange extends LeafRef { date: string; field: string; old: unknown; new: unknown; why: string }
export interface Publication {
  id: string;
  title: string;
  date: string;
  added_on: string;
  authors: string[];
  authors_short: string;
  venue: string;
  link: string;
  finding: string;
  moved_range: boolean;
  settled_stage: boolean;
  kind: StoryKind;
  kind_label: string;
  settles: SettledRung[];
  moved: MovedRange[];
  leaves: LeafRef[];
  branches: BranchRef[];
  verify: string[];
  notes: string;
  example: boolean;
  file: string;
  path: string;
}

export interface StoryEntry {
  kind: StoryKind;
  kind_label: string;
  date: string;              // the project date it was logged
  world_date: string | null; // when the thing itself happened, for a publication
  publication?: string;      // the publication id, for a publication entry
  leaf?: LeafRef;
  revision?: Revision;
  moves_estimate?: boolean;  // for a revision: true when it changed a year of an estimate
  reading?: string;
}
export interface Story {
  entries: StoryEntry[];
  totals: Record<StoryKind, number>;
  moved_estimate: number;
  days: string[];
  changelog: { source: string; intro: string; days: { date: string; items: string[] }[] };
}

export interface ReadingItem {
  kind: ReadingKind;
  kind_label: string;
  id: string;
  name: string;
  record: LeafRef | ClaimRef | ExperimentRef;
  group: string;                 // a branch key, or 'the-whole-question' for a claim about the headline
  verdict: ReadingVerdict;
  verdict_label: string;
  queries: string[];
  reused: string[];
  search_short: string;
  found: string;
  sources: string[];
  publications: PublicationRef[];
  moved_from: StageKey | null;
  moved_to: StageKey | null;
  moved_from_label: string | null;
  moved_to_label: string | null;
  for_john: string;
  resolved_on: string | null;   // a flagged item the records have since dealt with (decision 19)
  resolved_by: string;
  sibling_stage: StageKey | null;
  sibling_stage_label: string | null;
  sibling_agrees: boolean | null;
}
export interface ReadingGroup {
  key: string;
  name: string;
  path: string;
  items: ReadingItem[];
}
export interface Reading {
  id: string;
  read_on: string;
  covers_from: string;
  ran_at: string;
  run_by: 'hand' | 'scheduled';
  commit_before: string;
  summary: string;
  read: number;
  leaves_read: number;
  claims_read: number;
  experiments_read: number;
  searches: number;
  short_of_two: number;
  counts: Record<ReadingVerdict, number>;
  moved: LeafRef[];
  logged: string[];
  items: ReadingItem[];
  groups: ReadingGroup[];
  waiting: number;               // flagged items of this reading still waiting on the author
  resolved: number;              // flagged items of this reading since marked resolved
  notes: string;
  verify: string[];
  file: string;
  path: string;
}
export interface WaitingItem extends ReadingItem {
  reading: string;
  read_on: string;
  path: string;
}
export interface LatestReading {
  read_on: string;
  covers_from: string;
  summary: string;
  read: number;
  leaves_read: number;
  claims_read: number;
  experiments_read: number;
  searches: number;
  moved: string[];
  movers: LeafRef[];
  logged: number;
  flagged: number;
  waiting: number;
  path: string;
}

export interface HeadlineLeafDraw {
  id: string;
  name: string;
  stage: StageKey;
  known: boolean;
  estimate_status?: 'first-pass' | 'reviewed' | null;   // of the estimate the leaf carries, drawn or not
  year?: number;
  earliest?: number;
  likely?: number;
  latest?: number;
  estimate_status?: string;
}
export interface HeadlineBranch {
  key: string;
  name: string;
  required: boolean;
  handled_when: number;
  median_handled_year: number;
  leaves: HeadlineLeafDraw[];
}
export interface WorkedRunRow {
  key: string;
  name: string;
  required: boolean;
  handled_when: number;
  years: { id: string; name: string; year: number | null; known: boolean }[];
  handled_year: number | null;
  handled_by: { id: string; name: string } | null;
}
export interface WorkedRun {
  rows: WorkedRunRow[];
  latest_handled_year: number | null;
  latest_branch: string | null;
  lag: number;
  escape_year: number | null;
  note: string;
}
export type Headline =
  | { available: false; reason: string }
  | {
      available: true;
      computed_on: string;
      method: {
        document: string;
        status: string;
        runs: number;
        seed: number;
        lag_years: { earliest: number; likely: number; latest: number };
        before_year: number;
        century_end: number;
        draw: string;
        combination: string;
      };
      median_year: number;
      before_2050: number;
      after_2100: number;
      percentiles: { p5: number; p25: number; p50: number; p75: number; p95: number };
      histogram: { from: number; to: number | null; share: number }[];
      branches: HeadlineBranch[];
      counts: { leaves_counted: number; leaves_in_clinic_already: number; estimates_first_pass: number; estimates_first_pass_drawn: number; verify_entries: number };
      file: string;          // the file in the repository, data/headline.json
      served_at: string;     // the same file served from this site, /data/headline.json (2026-10-17)
      worked_run: WorkedRun;
    };

export interface Records {
  exported_on: string;   // year-month-day
  commit: string;        // short code of the source version, or ""
  counts: Counts;
  headline: Headline;
  fixed_dates: { before: number; century_end: number };
  reading: LatestReading | null;   // the latest real weekly reading, or null when none has run
  readings: Reading[];             // every real weekly reading, newest first
  waiting: WaitingItem[];          // flagged items still waiting on the author, newest reading first
  reading_verdicts: { key: ReadingVerdict; label: string; meaning: string }[];
  stages: Stage[];
  verdicts: { key: Verdict; label: string; meaning: string }[];
  story_kinds: { key: StoryKind; label: string }[];
  branches: Branch[];
  leaves: Leaf[];
  claims: Claim[];
  claims_counts: ClaimsCounts;
  experiments: Experiment[];
  publications: Publication[];
  story: Story;
  examples: { kind: string; id: string }[];
  retired: { id: string; kind: string; date: string; why: string; replaced_by?: string }[];
}

export const records = data as unknown as Records;
export const REPO = 'https://github.com/jfredson/outrunning-ageing';
export const SITE_NAME = 'Outrunning Ageing';
export const SIBLING_SITE = 'https://theupgradetree.com';

export const branchByKey = (key: string) => records.branches.find((b) => b.key === key);
export const leafById = (id: string) => records.leaves.find((l) => l.id === id);
export const publicationById = (id: string) => records.publications.find((p) => p.id === id);

/** "16 October 2026" for the footer and the strip; the design standard writes dates out there. */
export function longDate(iso: string): string {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC',
  });
}

/** A world date as the record gives it: "2004" stays "2004", "2019-09" becomes "September 2019",
 *  "2019-09-18" becomes "18 September 2019". */
export function worldDate(text: string | null | undefined): string {
  if (!text) return '';
  const parts = text.split('-').map(Number);
  if (parts.length === 1) return text;
  if (parts.length === 2) {
    return new Date(Date.UTC(parts[0], parts[1] - 1, 1)).toLocaleDateString('en-GB', { month: 'long', year: 'numeric', timeZone: 'UTC' });
  }
  return longDate(text);
}

/** "damaged DNA" from "Damaged DNA": only the first letter drops, so initials keep their capitals. */
export function lowerFirst(name: string): string {
  return name.charAt(0).toLowerCase() + name.slice(1);
}

export function plural(n: number, one: string, many: string): string {
  return `${n} ${n === 1 ? one : many}`;
}

/** "2.7%" from 0.0266; whole numbers above ten per cent, one decimal below. */
export function percent(share: number): string {
  const p = share * 100;
  if (p === 0) return '0%';
  if (p >= 10) return `${Math.round(p)}%`;
  return `${p.toFixed(1)}%`;
}

/** "2.7 per cent" for prose. */
export function percentWords(share: number): string {
  const p = share * 100;
  if (p === 0) return 'none';
  if (p >= 10) return `${Math.round(p)} per cent`;
  return `${p.toFixed(1)} per cent`;
}

/** "200,000" for a run count. */
export function plainNumber(n: number): string {
  return n.toLocaleString('en-GB');
}

/** A year past the century's end is said as "not this century" (docs/method.md, parameter 10). */
export function yearWords(year: number): string {
  return year > records.fixed_dates.century_end ? 'not this century' : String(year);
}

/** The spread under the headline: "anywhere from 2051 to 2068", or "... to not this century". */
export function spreadWords(): string {
  const h = records.headline;
  if (!h.available) return '';
  return `anywhere from ${yearWords(h.percentiles.p5)} to ${yearWords(h.percentiles.p95)}`;
}

export function hostOf(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
}

/** A link that opens a new issue in the public repository from one of the three templates
 *  (.github/ISSUE_TEMPLATE/), with the title and, where given, the body filled in. Copied from
 *  The Quiet Galaxy's records.ts on 2026-10-17. */
export function issueUrl(template: string, title: string, body = ''): string {
  const q = new URLSearchParams({ template, title });
  if (body) q.set('body', body);
  return `${REPO}/issues/new?${q.toString()}`;
}

/** Where a record lives in the public repository. */
export function recordUrl(file: string): string {
  return `${REPO}/blob/main/${file}`;
}

/** The footer's "from ..." clause: how much is behind the page, in the reader's terms. */
export function builtFrom(): string {
  const c = records.counts;
  return `${plural(c.branches, 'branch', 'branches')}, ${plural(c.leaves, 'treatment or tool', 'treatments and tools')}, ${plural(c.claims, 'promise', 'promises')}, ${plural(c.experiments, 'public self-experiment', 'public self-experiments')} and ${plural(c.publications, 'publication', 'publications')}`;
}

/** The one line the site repeats about self-experiments (ruled in the kickoff, 2026-10-16). */
export const ONE_PERSON_LINE = 'A claim about one person is a story, not a record, and it moves nothing on the tree.';
