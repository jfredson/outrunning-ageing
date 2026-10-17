// The typed view of the JSON the export script writes (scripts/export.py), plus the wording and
// the small helpers every page shares. Every page reads from here; nothing in the browser touches
// the TOML records. The file src/data/records.json is generated at build time and not committed:
// `npm run export` (or any build or dev run) writes it from ../data.
import data from '../data/records.json';

export interface Counts {
  branches: number;
  branches_expected: number;
  leaves: number;
  leaves_tracked: number;
  claims: number;
  experiments: number;
  publications: number;
  scans: number;
  scans_real: number;
  retired: number;
  verify: number;
  examples: number;
}

export interface Branch {
  key: string;
  order: number;
  name: string;
  meaning: string;
  hallmarks: string[];
  required: boolean;
  handled_when: number;
  what_would_move_this: string;
  leaves: number;
  leaves_tracked: number;
  furthest_stage: string | null;
  path: string;
}

export interface LeafBrief {
  id: string;
  name: string;
  branch: string;
  stage: string;
  stage_label: string;
  stage_reached_on: string | null;
  status: 'tracked' | 'withdrawn';
  horizon: 'near' | 'mid' | 'far' | 'top';
  horizon_words: string;
  sibling: string | null;
  estimate_status: 'first-pass' | 'reviewed' | null;
  example: boolean;
  path: string;
}

export interface ClaimBrief {
  id: string;
  who: string;
  said_on: string;
  commits_to: string;
  due: number | null;
  verdict: string;
  verdict_label: string;
  about_the_headline: boolean;
  leaves: string[];
  branches: string[];
  example: boolean;
  path: string;
}

export interface ExperimentBrief {
  id: string;
  who: string;
  name: string;
  started: string;
  status: 'running' | 'ended';
  leaves: string[];
  branches: string[];
  example: boolean;
  path: string;
}

export interface PublicationBrief {
  id: string;
  title: string;
  date: string;
  added_on: string;
  authors: string[];
  moved_range: boolean;
  settled_stage: boolean;
  leaves: string[];
  branches: string[];
  example: boolean;
  path: string;
}

export interface Reading {
  read_on: string;
  covers_from: string;
  summary: string;
  read: number;
  moved: string[];
  path: string;
}

export type Headline =
  | { available: false; reason: string }
  | {
      available: true;
      median_year: number;
      before_2050: number;
      after_2100: number;
      percentiles?: Record<string, number>;
      histogram?: { from: number; to: number; share: number }[];
      method?: { before_year?: number; century_end?: number; runs?: number; [key: string]: unknown };
      computed_on?: string;
      file?: string;
      [key: string]: unknown;
    };

export interface Records {
  exported_on: string;   // year-month-day
  commit: string;        // short code of the source version, or ""
  counts: Counts;
  headline: Headline;
  fixed_dates: { before: number; century_end: number };
  reading: Reading | null;   // the latest real weekly reading, or null when none has run
  stages: { key: string; label: string; rank: number }[];
  branches: Branch[];
  leaves: LeafBrief[];
  claims: ClaimBrief[];
  experiments: ExperimentBrief[];
  publications: PublicationBrief[];
  examples: { kind: string; id: string }[];
  retired: { id: string; kind: string; date: string; why: string; replaced_by?: string }[];
}

export const records = data as unknown as Records;
export const REPO = 'https://github.com/jfredson/outrunning-ageing';
export const SITE_NAME = 'Outrunning Ageing';

/** "16 October 2026" for the footer and the strip; the design standard writes dates out there. */
export function longDate(iso: string): string {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC',
  });
}

export function plural(n: number, one: string, many: string): string {
  return `${n} ${n === 1 ? one : many}`;
}

/** The footer's "from ..." clause: how much is behind the page, in the reader's terms. */
export function builtFrom(): string {
  const c = records.counts;
  return `${plural(c.branches, 'branch', 'branches')}, ${plural(c.leaves, 'treatment or tool', 'treatments and tools')}, ${plural(c.claims, 'promise', 'promises')}, ${plural(c.experiments, 'public self-experiment', 'public self-experiments')} and ${plural(c.publications, 'publication', 'publications')}`;
}
