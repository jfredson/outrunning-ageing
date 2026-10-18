#!/usr/bin/env python3
"""Outrunning Ageing: check the records in data/ and, once the leaves exist, compute the headline.

Plain Python, standard library only. Run from anywhere:

    python3 scripts/compute.py validate            check every record against docs/record-schema.md
    python3 scripts/compute.py run                 compute the headline and write data/headline.json
                                                   (refuses, with a plain message, until the leaves exist)
    python3 scripts/compute.py --data DIR ...      use a different data folder (for tests)

"validate" reads data/branches.toml, every TOML file under data/leaves, data/claims,
data/experiments, data/papers and data/scans, plus data/retired.toml, and lists everything that
breaks a rule in plain language: a leaf with no test or no settler, a claim with no source, a
self-experiment that tries to move a leaf, a link to a record that does not exist, a file whose
name and id disagree, an id that was committed before and has disappeared without an entry in
data/retired.toml. It exits non-zero on any failure, and nothing downstream runs until it passes.

"run" validates, refuses until every branch has at least as many tracked leaves as its
handled_when (naming the branches short of it), and otherwise plays the tree out 200,000 times
with a fixed seed (docs/method.md) and writes the headline to data/headline.json: the median
escape year, the share of runs before 2050, the share after 2100, the spread, a histogram, and
each branch's median handled year.

The weekly reading's record (data/scans/, docs/weekly-reading.md) is checked with the rest: every
item names a leaf, claim or self-experiment that exists, lists its searches, and carries one of
four verdicts; a moved item is matched by a stage revision on the leaf dated the reading's day; the
header counts match the items.

Written 2026-10-16 (weekend step 2 of docs/2026-10-16-kickoff.md); the computation filled in the
same day by the leaf session (weekend step 3); the reading record widened 2026-10-17.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The eight branches: key -> order. Fixed; changed only at a yearly review (tracker pattern 2.1).
BRANCHES: dict[str, int] = {
    "worn-out-cells": 1,
    "damaged-dna": 2,
    "cell-settings": 3,
    "broken-proteins": 4,
    "energy-and-fuel": 5,
    "replacing-parts": 6,
    "inflammation-and-signalling": 7,
    "measuring-age": 8,
}
BRANCH_ORDER = sorted(BRANCHES, key=BRANCHES.get)

# The twelve hallmarks of ageing (López-Otín and colleagues, 2023). Each belongs to exactly one
# branch; the validator checks branches.toml covers all twelve once.
HALLMARKS: set[str] = {
    "genomic-instability", "telomere-attrition", "epigenetic-alterations", "loss-of-proteostasis",
    "disabled-macroautophagy", "deregulated-nutrient-sensing", "mitochondrial-dysfunction",
    "cellular-senescence", "stem-cell-exhaustion", "altered-intercellular-communication",
    "chronic-inflammation", "dysbiosis",
}

# The stage ladder, The Upgrade Tree's, in order; the rung the headline reads is in-clinical-use.
STAGES: list[str] = ["idea-only", "shown-in-animals", "first-human", "in-clinical-use", "in-wide-use"]
STAGE_RANK = {s: i for i, s in enumerate(STAGES)}
CLINIC = "in-clinical-use"

LEAF_STATUSES = {"tracked", "withdrawn"}
HORIZONS = {"near", "mid", "far", "top"}
ESTIMATE_STATUSES = {"first-pass", "reviewed"}
VERDICTS = {"not-yet-due", "delivered", "missed", "unfalsifiable"}
EXPERIMENT_STATUSES = {"running", "ended"}
# The weekly reading's four verdicts (docs/record-schema.md, "The scan record"; widened from the
# five leaf-only verdicts of 2026-10-16 on 2026-10-17 with the weekly reading, docs/weekly-reading.md).
READING_VERDICTS = {"quiet", "noted", "moved", "flagged"}
RUN_BY = {"hand", "scheduled"}
LATEST_YEAR = 2300

RECORD_KINDS = {"branch", "leaf", "claim", "experiment", "publication", "scan"}

# Folder under data/ -> record kind (branches live in one file, handled separately).
FOLDERS: dict[str, str] = {
    "leaves": "leaf",
    "claims": "claim",
    "experiments": "experiment",
    "papers": "publication",
    "scans": "scan",
}

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
WORLD_DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
RAN_AT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
LINK_RE = re.compile(r"^https?://\S+$")

COMMON = {"verify", "notes", "example"}

# Fields each kind may carry (docs/record-schema.md). Required ones are listed separately.
ALLOWED: dict[str, set[str]] = {
    "branch": {"key", "order", "name", "meaning", "hallmarks", "required", "handled_when",
               "what_would_move_this"} | COMMON,
    "leaf": {"id", "name", "branch", "description", "test", "settler", "stage", "stage_reached_on",
             "stage_record", "stage_publication", "earlier_stage", "status", "horizon", "long_shot",
             "mechanism", "breaking_point", "sibling", "estimate", "revision", "added_on"} | COMMON,
    "claim": {"id", "who", "who_is", "said_on", "where", "link", "quote", "is_paraphrase",
              "paraphrase_seen_in", "commits_to", "due", "leaves", "branches", "about_the_headline",
              "verdict", "verdict_on", "verdict_why", "added_on"} | COMMON,
    "experiment": {"id", "who", "who_is", "name", "started", "status", "ended", "what", "measures",
                   "claims", "public_record", "link", "leaves", "branches", "added_on"} | COMMON,
    "publication": {"id", "date", "added_on", "authors", "title", "venue", "link", "finding",
                    "leaves", "branches", "moved_range", "settled_stage"} | COMMON,
    "scan": {"id", "read_on", "covers_from", "ran_at", "run_by", "commit_before", "leaves_read",
             "claims_read", "experiments_read", "searches", "summary", "item", "limits",
             "later_note"} | COMMON,
}
REQUIRED: dict[str, list[str]] = {
    "branch": ["key", "order", "name", "meaning", "hallmarks", "required", "handled_when"],
    # added_on, the date a record was first committed, on treatments, claims and self-experiments
    # (ruled by John 2026-10-18; back-filled that day from the repository's history).
    "leaf": ["id", "added_on", "name", "branch", "description", "test", "settler", "stage", "status", "horizon"],
    "claim": ["id", "added_on", "who", "who_is", "said_on", "where", "quote", "commits_to", "verdict"],
    "experiment": ["id", "added_on", "who", "who_is", "started", "status", "what", "measures", "claims",
                   "public_record", "link"],
    "publication": ["id", "date", "added_on", "authors", "title", "venue", "link", "finding",
                    "moved_range", "settled_stage"],
    "scan": ["id", "read_on", "covers_from", "ran_at", "run_by", "commit_before", "leaves_read",
             "claims_read", "experiments_read", "searches", "summary", "item"],
}
# "hallmarks" may be an empty list (the measuring branch), so it is not checked for emptiness.
MAY_BE_EMPTY = {"hallmarks"}

EARLIER_STAGE_ALLOWED = {"stage", "reached_on", "record", "publication"}
ESTIMATE_ALLOWED = {"status", "set_on", "why", "sources", "rung"}
RUNG_ALLOWED = {"rung", "earliest", "likely", "latest"}
REVISION_ALLOWED = {"date", "field", "old", "new", "why", "publication"}
ITEM_ALLOWED = {"leaf", "claim", "experiment", "verdict", "queries", "reused", "search_short", "found",
                "sources", "publications", "moved_from", "moved_to", "for_john", "resolved_on", "resolved_by",
                "sibling_stage", "sibling_agrees"}
ITEM_TARGETS = ("leaf", "claim", "experiment")
LATER_NOTE_ALLOWED = {"date", "text"}
RETIRED_ALLOWED = {"id", "kind", "date", "replaced_by", "why"}

# Fields a self-experiment must never carry: a self-experiment moves no leaf. Unknown fields are
# refused anyway; these get a plainer message.
EXPERIMENT_FORBIDDEN = {"stage", "stage_reached_on", "stage_record", "estimate", "range", "earliest",
                        "likely", "latest", "revision"}


class RecordError(Exception):
    """Raised with a plain-language list of everything wrong with the records."""


# ---------------------------------------------------------------- loading


def load_records(data_dir: Path) -> dict:
    """Read every record file, the branches file and the retired list.

    Returns {"records": [...], "retired": [...]}. Each record is the TOML table with two extra
    keys: "_kind" and "_path". A branch's "_path" is branches.toml and it also gets "_index"
    (its position in the file). Files that cannot be read as TOML are reported through
    RecordError; nothing else is checked here.
    """
    problems: list[str] = []
    records: list[dict] = []

    def read(path: Path) -> dict | None:
        try:
            return tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as e:
            problems.append(f"{rel(path, data_dir)}: cannot be read as TOML: {e}")
            return None
        except OSError as e:
            problems.append(f"{rel(path, data_dir)}: cannot be read: {e}")
            return None

    if not data_dir.is_dir():
        raise RecordError(f"{data_dir} is not a folder")

    branches_path = data_dir / "branches.toml"
    if branches_path.exists():
        table = read(branches_path)
        if table is not None:
            entries = table.get("branch")
            extra = sorted(set(table) - {"branch"})
            if extra:
                problems.append(f"branches.toml: unknown top-level field(s) {extra}; the file holds [[branch]] tables only")
            if not isinstance(entries, list) or not entries:
                problems.append("branches.toml: must hold a list of [[branch]] tables")
            else:
                for i, b in enumerate(entries, 1):
                    if not isinstance(b, dict):
                        problems.append(f"branches.toml, branch {i}: must be a table")
                        continue
                    b["_kind"] = "branch"
                    b["_path"] = branches_path
                    b["_index"] = i
                    records.append(b)
    else:
        problems.append("branches.toml is missing (the eight branches live there)")

    for folder, kind in FOLDERS.items():
        sub = data_dir / folder
        if not sub.is_dir():
            problems.append(f"{folder}/ is missing from {data_dir}")
            continue
        for path in sorted(sub.glob("*.toml")):
            table = read(path)
            if table is None:
                continue
            table["_kind"] = kind
            table["_path"] = path
            records.append(table)

    # Any other folder holding TOML is a mistake: a record in the wrong place is never read.
    for sub in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        if sub.name not in FOLDERS and any(sub.rglob("*.toml")):
            problems.append(f"{sub.name}/ is not one of the five record folders "
                            f"({', '.join(FOLDERS)}) but holds TOML files")

    retired: list[dict] = []
    retired_path = data_dir / "retired.toml"
    if retired_path.exists():
        table = read(retired_path)
        if table is not None:
            retired = table.get("retired", [])
            if not isinstance(retired, list):
                problems.append("retired.toml: 'retired' must be a list")
                retired = []
    else:
        problems.append("retired.toml is missing (it may be empty, but it must exist)")

    if problems:
        raise RecordError("\n".join(problems))
    return {"records": records, "retired": retired}


def rel(path: Path, data_dir: Path) -> str:
    try:
        return str(path.relative_to(data_dir))
    except ValueError:
        return str(path)


def ids_in_history(data_dir: Path) -> set[tuple[str, str]] | None:
    """Every (kind, id) whose file was ever committed under data_dir, read from git history.

    Branches live in one file and are not covered (the eight keys are fixed in the script).
    Returns None when the folder is not in a git repository or git is not available, in which
    case the renamed-id check is skipped with a note.
    """
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--no-renames", "--name-only",
             "--pretty=format:", "--relative", "--", "."],
            cwd=data_dir, capture_output=True, text=True, check=True, timeout=30,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    seen: set[tuple[str, str]] = set()
    for line in out.splitlines():
        parts = line.strip().split("/")
        if len(parts) == 2 and parts[0] in FOLDERS and parts[1].endswith(".toml"):
            seen.add((FOLDERS[parts[0]], parts[1][: -len(".toml")]))
    return seen


# ---------------------------------------------------------------- validation


def validate(loaded: dict, previously_seen: set[tuple[str, str]] | None = None) -> list[str]:
    """Check every record against docs/record-schema.md. Returns a list of problems; empty means OK.

    previously_seen is the set of (kind, id) ever committed (ids_in_history); pass None to skip
    the renamed-id history check.
    """
    records: list[dict] = loaded["records"]
    retired: list[dict] = loaded["retired"]
    problems: list[str] = []

    def where(r: dict) -> str:
        if r["_kind"] == "branch":
            return f"branch {r.get('key', '?')!s} (branches.toml, entry {r['_index']})"
        return f"{r['_kind']} {r['_path'].name}"

    def rid_of(r: dict):
        return r.get("key") if r["_kind"] == "branch" else r.get("id")

    # ---- ids: shape, uniqueness, file name
    by_kind: dict[str, dict[str, dict]] = {k: {} for k in RECORD_KINDS}
    all_ids: dict[str, dict] = {}
    for r in records:
        rid = rid_of(r)
        if not isinstance(rid, str) or not rid:
            problems.append(f"{where(r)}: has no {'key' if r['_kind'] == 'branch' else 'id'}")
            continue
        if not ID_RE.match(rid):
            problems.append(f"{where(r)}: id {rid!r} is not a lowercase slug (letters, digits, single dashes)")
        if r["_kind"] != "branch" and r["_path"].stem != rid:
            problems.append(f"{where(r)}: file is named {r['_path'].stem!r} but its id is {rid!r}; "
                            "ids are never renamed, and the file is named for the id")
        if rid in all_ids:
            problems.append(f"{where(r)}: id {rid!r} is also used by {where(all_ids[rid])}; ids are unique across all records")
        else:
            all_ids[rid] = r
            by_kind[r["_kind"]][rid] = r

    leaves = by_kind["leaf"]
    publication_ids = set(by_kind["publication"])
    branch_keys_present = set(by_kind["branch"])

    # ---- the eight branches and the twelve hallmarks
    missing_branches = [k for k in BRANCH_ORDER if k not in branch_keys_present]
    if missing_branches:
        problems.append(f"branches.toml: missing the branch(es) {', '.join(missing_branches)}; the eight are fixed")
    seen_hallmarks: dict[str, str] = {}
    for key, b in by_kind["branch"].items():
        hs = b.get("hallmarks")
        if isinstance(hs, list):
            for h in hs:
                if h in seen_hallmarks and h in HALLMARKS:
                    problems.append(f"branches.toml: hallmark {h!r} is grouped under both {seen_hallmarks[h]!r} and {key!r}; each belongs to one branch")
                seen_hallmarks[h] = key
    uncovered = sorted(HALLMARKS - set(seen_hallmarks))
    if uncovered and not missing_branches:
        problems.append(f"branches.toml: the hallmark(s) {', '.join(uncovered)} belong to no branch; all twelve must be grouped")

    # ---- retired list
    retired_ids: set[str] = set()
    for i, entry in enumerate(retired, 1):
        tag = f"retired.toml entry {i}"
        if not isinstance(entry, dict):
            problems.append(f"{tag}: must be a table")
            continue
        for key in entry:
            if key not in RETIRED_ALLOWED:
                problems.append(f"{tag}: unknown field {key!r}")
        for key in ("id", "kind", "date", "why"):
            if key not in entry or entry[key] in ("", None):
                problems.append(f"{tag}: missing {key!r}")
        rid = entry.get("id")
        if isinstance(rid, str):
            retired_ids.add(rid)
            if rid in all_ids:
                problems.append(f"{tag}: id {rid!r} is retired but {where(all_ids[rid])} still uses it; a retired id is never reused")
        if entry.get("kind") not in RECORD_KINDS:
            problems.append(f"{tag}: kind must be one of {sorted(RECORD_KINDS)}")
        if "date" in entry and not isinstance(entry["date"], dt.date):
            problems.append(f"{tag}: date must be a TOML date like 2026-10-16")
        rep = entry.get("replaced_by")
        if rep is not None and rep not in all_ids:
            problems.append(f"{tag}: replaced_by {rep!r} is not a record that exists")

    # ---- the renamed-id history check
    if previously_seen is not None:
        current = {(r["_kind"], rid_of(r)) for r in records if isinstance(rid_of(r), str)}
        for kind, rid in sorted(previously_seen - current):
            if rid not in retired_ids:
                problems.append(f"{kind} {rid!r} was committed before and is now gone, with no entry in "
                                "data/retired.toml; ids are never renamed or silently deleted")

    # ---- per-record checks
    for r in records:
        kind = r["_kind"]
        tag = where(r)
        fields = {k for k in r if not k.startswith("_")}
        if kind == "experiment":
            for key in sorted(fields & EXPERIMENT_FORBIDDEN):
                problems.append(f"{tag}: carries {key!r}, but a self-experiment moves no leaf: a claim about one "
                                "person is a story, not a record (docs/record-schema.md)")
        for key in sorted(fields - ALLOWED[kind] - (EXPERIMENT_FORBIDDEN if kind == "experiment" else set())):
            problems.append(f"{tag}: unknown field {key!r} (see docs/record-schema.md)")
        for key in REQUIRED[kind]:
            if key not in r or (key not in MAY_BE_EMPTY and _empty(r[key])):
                problems.append(f"{tag}: required field {key!r} is missing or empty")
        _check_text_fields(r, tag, problems)
        _check_common(r, tag, problems)

        if kind == "branch":
            _check_branch(r, tag, problems)
        elif kind == "leaf":
            _check_leaf(r, tag, publication_ids, problems)
        elif kind == "claim":
            _check_claim(r, tag, leaves, problems)
        elif kind == "experiment":
            _check_experiment(r, tag, leaves, problems)
        elif kind == "publication":
            _check_publication(r, tag, leaves, problems)
        elif kind == "scan":
            _check_scan(r, tag, by_kind, problems)

    return problems


def _empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def _is_number(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _is_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def _check_text_fields(r: dict, tag: str, problems: list[str]) -> None:
    """Fields that must be text when present, and fields that must be whole numbers or true/false."""
    text_fields = {"id", "key", "name", "meaning", "what_would_move_this", "branch", "description",
                   "test", "settler", "stage", "stage_reached_on", "stage_record", "stage_publication",
                   "status", "horizon", "mechanism", "breaking_point", "sibling", "who", "who_is",
                   "said_on", "where", "link", "quote", "paraphrase_seen_in", "commits_to", "verdict",
                   "verdict_why", "started", "ended", "what", "measures", "claims", "public_record",
                   "date", "title", "venue", "finding", "summary", "notes", "run_by", "commit_before"}
    for key in text_fields & set(r):
        if not isinstance(r[key], str):
            problems.append(f"{tag}: {key!r} must be text")
    for key in ("order", "handled_when", "due"):
        if key in r and not _is_int(r[key]):
            problems.append(f"{tag}: {key!r} must be a whole number")
    for key in ("required", "long_shot", "is_paraphrase", "about_the_headline", "moved_range",
                "settled_stage", "example"):
        if key in r and not isinstance(r[key], bool):
            problems.append(f"{tag}: {key!r} must be true or false")
    for key in ("said_on", "started", "ended", "stage_reached_on", "date"):
        if isinstance(r.get(key), str) and not WORLD_DATE_RE.match(r[key]):
            problems.append(f"{tag}: {key!r} must be a year, year-month or full date as text, like \"2004\" or \"2019-09-18\"")
    for key in ("added_on", "read_on", "covers_from", "verdict_on"):
        if key in r and not isinstance(r[key], dt.date):
            problems.append(f"{tag}: {key!r} must be a TOML date like 2026-10-16")


def _check_common(r: dict, tag: str, problems: list[str]) -> None:
    v = r.get("verify")
    if v is not None and (not isinstance(v, list) or not all(isinstance(x, str) and x.strip() for x in v)):
        problems.append(f"{tag}: 'verify' must be a list of plain-language claims (non-empty text)")


def _check_id_list(r: dict, key: str, allowed, what: str, tag: str, problems: list[str]) -> list[str]:
    """A list field of ids that must all exist. Returns the list (empty if absent or malformed)."""
    v = r.get(key)
    if v is None:
        return []
    if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
        problems.append(f"{tag}: {key!r} must be a list of ids")
        return []
    for x in v:
        if x not in allowed:
            problems.append(f"{tag}: {key!r} names {x!r}, which is not {what}")
    return v


def _check_branch(r: dict, tag: str, problems: list[str]) -> None:
    key = r.get("key")
    if key not in BRANCHES:
        problems.append(f"{tag}: key {key!r} is not one of the eight branches ({', '.join(BRANCH_ORDER)})")
    elif r.get("order") != BRANCHES[key]:
        problems.append(f"{tag}: order must be {BRANCHES[key]} for {key}")
    hs = r.get("hallmarks")
    if hs is not None:
        if not isinstance(hs, list) or not all(isinstance(h, str) for h in hs):
            problems.append(f"{tag}: 'hallmarks' must be a list of hallmark keys")
        else:
            for h in hs:
                if h not in HALLMARKS:
                    problems.append(f"{tag}: {h!r} is not one of the twelve hallmarks")
    hw = r.get("handled_when")
    if _is_int(hw) and hw < 1:
        problems.append(f"{tag}: handled_when must be at least 1")


def _check_stage_entry(e: dict, etag: str, allowed: set[str], publication_ids: set[str],
                       problems: list[str]) -> None:
    for key in sorted(set(e) - allowed):
        problems.append(f"{etag}: unknown field {key!r}")
    pub = e.get("publication")
    if pub is not None and pub not in publication_ids:
        problems.append(f"{etag}: publication {pub!r} is not a publication record that exists")


def _check_leaf(r: dict, tag: str, publication_ids: set[str], problems: list[str]) -> None:
    if "branch" in r and r["branch"] not in BRANCHES:
        problems.append(f"{tag}: branch {r['branch']!r} is not one of the eight ({', '.join(BRANCH_ORDER)})")
    stage = r.get("stage")
    if stage is not None and stage not in STAGE_RANK:
        problems.append(f"{tag}: stage must be one of {STAGES}")
        stage = None
    if "status" in r and r["status"] not in LEAF_STATUSES:
        problems.append(f"{tag}: status must be one of {sorted(LEAF_STATUSES)}")
    horizon = r.get("horizon")
    if horizon is not None and horizon not in HORIZONS:
        problems.append(f"{tag}: horizon must be one of {sorted(HORIZONS)}")
    if horizon == "top" and stage is not None and stage != "in-wide-use":
        problems.append(f"{tag}: horizon 'top' is only for a leaf already in wide use (this one is at {stage!r})")

    if stage is not None and stage != "idea-only":
        for key in ("stage_reached_on", "stage_record"):
            if _empty(r.get(key)):
                problems.append(f"{tag}: a stage above idea-only needs {key!r} (every stage reached carries a date and a public record)")
    pub = r.get("stage_publication")
    if pub is not None and pub not in publication_ids:
        problems.append(f"{tag}: stage_publication {pub!r} is not a publication record that exists")

    earlier = r.get("earlier_stage", [])
    if not isinstance(earlier, list):
        problems.append(f"{tag}: 'earlier_stage' must be a list of [[earlier_stage]] tables")
        earlier = []
    seen_rungs: set[str] = set()
    for i, e in enumerate(earlier, 1):
        etag = f"{tag}, earlier_stage {i}"
        if not isinstance(e, dict):
            problems.append(f"{etag}: must be a table")
            continue
        _check_stage_entry(e, etag, EARLIER_STAGE_ALLOWED, publication_ids, problems)
        s = e.get("stage")
        if s not in STAGE_RANK:
            problems.append(f"{etag}: stage must be one of {STAGES}")
        elif stage is not None and STAGE_RANK[s] >= STAGE_RANK[stage]:
            problems.append(f"{etag}: {s!r} is not below the current stage {stage!r}")
        elif s in seen_rungs:
            problems.append(f"{etag}: rung {s!r} is listed twice")
        else:
            seen_rungs.add(s)
        if not isinstance(e.get("reached_on"), str) or not WORLD_DATE_RE.match(e["reached_on"]):
            problems.append(f"{etag}: 'reached_on' must be a year, year-month or full date as text")
        if _empty(e.get("record")) or not isinstance(e.get("record"), str):
            problems.append(f"{etag}: needs a 'record' (a link to the public record that reached the rung)")

    if r.get("long_shot") is True:
        for key in ("mechanism", "breaking_point"):
            if _empty(r.get(key)):
                problems.append(f"{tag}: a long shot needs {key!r} (how it could happen, and where it would break)")
    if "sibling" in r and (not isinstance(r["sibling"], str) or not ID_RE.match(r["sibling"])):
        problems.append(f"{tag}: 'sibling' must be the Upgrade Tree id as a lowercase slug")

    est = r.get("estimate")
    below_clinic = stage is not None and STAGE_RANK[stage] < STAGE_RANK[CLINIC]
    if est is None:
        if below_clinic:
            problems.append(f"{tag}: a leaf below {CLINIC!r} needs an [estimate] with a rung for {CLINIC!r} "
                            "(the year the headline reads)")
    elif not isinstance(est, dict):
        problems.append(f"{tag}: 'estimate' must be an [estimate] table")
    else:
        for key in sorted(set(est) - ESTIMATE_ALLOWED):
            problems.append(f"{tag}, estimate: unknown field {key!r}")
        for key in ("status", "set_on", "why", "rung"):
            if key not in est or _empty(est[key]):
                problems.append(f"{tag}, estimate: missing {key!r}")
        if "status" in est and est["status"] not in ESTIMATE_STATUSES:
            problems.append(f"{tag}, estimate: status must be one of {sorted(ESTIMATE_STATUSES)}")
        set_on = est.get("set_on")
        if "set_on" in est and not isinstance(set_on, dt.date):
            problems.append(f"{tag}, estimate: set_on must be a TOML date like 2026-10-16")
            set_on = None
        if "why" in est and not isinstance(est["why"], str):
            problems.append(f"{tag}, estimate: 'why' must be text")
        _check_id_list(est, "sources", publication_ids, "a publication record that exists", f"{tag}, estimate", problems)
        rungs = est.get("rung", [])
        if not isinstance(rungs, list):
            problems.append(f"{tag}, estimate: 'rung' must be a list of [[estimate.rung]] tables")
            rungs = []
        seen: set[str] = set()
        for i, g in enumerate(rungs, 1):
            gtag = f"{tag}, estimate rung {i}"
            if not isinstance(g, dict):
                problems.append(f"{gtag}: must be a table")
                continue
            for key in sorted(set(g) - RUNG_ALLOWED):
                problems.append(f"{gtag}: unknown field {key!r}")
            name = g.get("rung")
            if name not in STAGE_RANK:
                problems.append(f"{gtag}: rung must be one of {STAGES}")
            elif stage is not None and STAGE_RANK[name] <= STAGE_RANK[stage]:
                problems.append(f"{gtag}: {name!r} is not above the current stage {stage!r}; only remaining rungs are estimated")
            elif name in seen:
                problems.append(f"{gtag}: rung {name!r} is listed twice")
            else:
                seen.add(name)
            years = [g.get(k) for k in ("earliest", "likely", "latest")]
            if not all(_is_int(y) for y in years):
                problems.append(f"{gtag}: 'earliest', 'likely' and 'latest' must all be whole years")
                continue
            lo, mid, hi = years
            if not lo <= mid <= hi:
                problems.append(f"{gtag}: years must run earliest <= likely <= latest ({lo}, {mid}, {hi})")
            if isinstance(set_on, dt.date) and lo < set_on.year:
                problems.append(f"{gtag}: earliest ({lo}) is before the year the estimate was set ({set_on.year})")
            if hi > LATEST_YEAR:
                problems.append(f"{gtag}: latest ({hi}) is past {LATEST_YEAR}; a far year is how 'perhaps never' is written, and {LATEST_YEAR} is far enough")
        if below_clinic and CLINIC not in seen:
            problems.append(f"{tag}, estimate: has no rung for {CLINIC!r}, the rung the headline reads")

    revisions = r.get("revision", [])
    if not isinstance(revisions, list):
        problems.append(f"{tag}: 'revision' must be a list of [[revision]] tables")
        revisions = []
    for i, rev in enumerate(revisions, 1):
        rtag = f"{tag}, revision {i}"
        if not isinstance(rev, dict):
            problems.append(f"{rtag}: must be a table")
            continue
        for key in sorted(set(rev) - REVISION_ALLOWED):
            problems.append(f"{rtag}: unknown field {key!r}")
        for key in ("date", "field", "old", "new", "why"):
            if key not in rev or _empty(rev[key]):
                problems.append(f"{rtag}: missing {key!r}")
        if "date" in rev and not isinstance(rev["date"], dt.date):
            problems.append(f"{rtag}: date must be a TOML date like 2026-10-16")
        pub = rev.get("publication")
        if pub is not None and pub not in publication_ids:
            problems.append(f"{rtag}: publication {pub!r} is not a publication record that exists")


def _check_targets(r: dict, tag: str, leaves: dict, problems: list[str], verb: str) -> tuple[list, list]:
    ls = _check_id_list(r, "leaves", set(leaves), "a leaf that exists", tag, problems)
    bs = _check_id_list(r, "branches", set(BRANCHES), "one of the eight branches", tag, problems)
    return ls, bs


def _check_claim(r: dict, tag: str, leaves: dict, problems: list[str]) -> None:
    ls, bs = _check_targets(r, tag, leaves, problems, "bears on")
    if not ls and not bs and r.get("about_the_headline") is not True:
        problems.append(f"{tag}: names no leaf and no branch and is not about the headline; a claim bears on at least one")
    if r.get("is_paraphrase") is True and _empty(r.get("paraphrase_seen_in")):
        problems.append(f"{tag}: a paraphrase says where it was seen ('paraphrase_seen_in'); a repeated version is never promoted to a quote")
    verdict = r.get("verdict")
    if verdict is not None and verdict not in VERDICTS:
        problems.append(f"{tag}: verdict must be one of {sorted(VERDICTS)}")
    if verdict == "not-yet-due" and not _is_int(r.get("due")):
        problems.append(f"{tag}: a claim that is not yet due needs a 'due' year, so the verdict can be given when it passes")
    if verdict in ("delivered", "missed"):
        for key in ("verdict_on", "verdict_why"):
            if _empty(r.get(key)):
                problems.append(f"{tag}: a {verdict!r} verdict needs {key!r} (when it was given, and on what record)")


def _check_experiment(r: dict, tag: str, leaves: dict, problems: list[str]) -> None:
    ls, bs = _check_targets(r, tag, leaves, problems, "tries")
    if not ls and not bs:
        problems.append(f"{tag}: names no leaf and no branch; a self-experiment tries at least one")
    if "status" in r and r["status"] not in EXPERIMENT_STATUSES:
        problems.append(f"{tag}: status must be one of {sorted(EXPERIMENT_STATUSES)}")
    if r.get("status") == "ended" and _empty(r.get("ended")):
        problems.append(f"{tag}: an ended self-experiment says when ('ended')")


def _check_publication(r: dict, tag: str, leaves: dict, problems: list[str]) -> None:
    authors = r.get("authors")
    if authors is not None and (not isinstance(authors, list)
                                or not all(isinstance(a, str) and a.strip() for a in authors)):
        problems.append(f"{tag}: 'authors' must be a list of names")
    ls, bs = _check_targets(r, tag, leaves, problems, "bears on")
    if not ls and not bs:
        problems.append(f"{tag}: names no leaf and no branch; a publication bears on at least one")
    rid = r.get("id")
    if r.get("moved_range") is True:
        named = any(rev.get("publication") == rid
                    for leaf in leaves.values()
                    for rev in (leaf.get("revision") or []) if isinstance(rev, dict))
        if not named:
            problems.append(f"{tag}: says it moved an estimate, but no leaf has a revision naming {rid!r}")
    if r.get("settled_stage") is True:
        named = any(leaf.get("stage_publication") == rid
                    or any(isinstance(e, dict) and e.get("publication") == rid for e in (leaf.get("earlier_stage") or []))
                    for leaf in leaves.values())
        if not named:
            problems.append(f"{tag}: says it settled a stage, but no leaf names {rid!r} as a stage record")


def _text_list(value) -> bool:
    return isinstance(value, list) and all(isinstance(x, str) and x.strip() for x in value)


def _check_scan(r: dict, tag: str, by_kind: dict[str, dict[str, dict]], problems: list[str]) -> None:
    """The weekly reading's record (docs/record-schema.md, "The scan record"; docs/weekly-reading.md).

    The header says when it ran and what it read; one [[item]] per record read, each naming
    exactly one leaf, claim or self-experiment, with the searches, what was found and one of four
    verdicts. A moved item is a leaf whose record carries a stage revision dated the reading's day;
    a noted item names the publication it logged; a flagged item carries a line for John. The
    header counts must match the items.
    """
    leaves = by_kind["leaf"]
    publication_ids = set(by_kind["publication"])
    read_on = r.get("read_on")
    rid = r.get("id")
    if isinstance(read_on, dt.date) and isinstance(rid, str):
        day = read_on.isoformat()
        if not (rid == day or re.fullmatch(re.escape(day) + r"-[2-9]", rid)):
            problems.append(f"{tag}: id {rid!r} must be the read_on date {day} (with -2, -3 on a second or third run that day)")
    covers = r.get("covers_from")
    if isinstance(read_on, dt.date) and isinstance(covers, dt.date) and covers > read_on:
        problems.append(f"{tag}: covers_from ({covers}) is after read_on ({read_on})")
    if isinstance(r.get("ran_at"), str) and not RAN_AT_RE.match(r["ran_at"]):
        problems.append(f"{tag}: ran_at must be universal time as text, like \"2026-10-17T22:15:00Z\"")
    elif "ran_at" in r and not isinstance(r["ran_at"], str):
        problems.append(f"{tag}: ran_at must be text, like \"2026-10-17T22:15:00Z\"")
    if "run_by" in r and r["run_by"] not in RUN_BY:
        problems.append(f"{tag}: run_by must be one of {sorted(RUN_BY)}")
    if "commit_before" in r and (not isinstance(r["commit_before"], str) or not COMMIT_RE.match(r["commit_before"])):
        problems.append(f"{tag}: commit_before must be the short commit the records were read at, like \"23a12a3\"")
    for key in ("leaves_read", "claims_read", "experiments_read", "searches"):
        if key in r and (not _is_int(r[key]) or r[key] < 0):
            problems.append(f"{tag}: {key!r} must be a whole number")

    # `limits`: what the reading could not see (pages opened and refused, no date filter); asked of
    # every reading from 2026-10-25 by the procedure, optional here so earlier readings still pass
    # (decision 20, ruled by John 2026-10-18).
    if "limits" in r and (not isinstance(r["limits"], str) or _empty(r["limits"])):
        problems.append(f"{tag}: 'limits' must say, in plain words, which pages were opened and refused and what the searches could not do")
    # `later_note`: a dated note added after the reading by a later batch, never by the reading
    # itself; the reading's own words stay as written (decision 21, ruled by John 2026-10-18).
    notes_later = r.get("later_note", [])
    if not isinstance(notes_later, list):
        problems.append(f"{tag}: 'later_note' must be a list of [[later_note]] tables")
        notes_later = []
    for n, ln in enumerate(notes_later, 1):
        ntag = f"{tag}, later note {n}"
        if not isinstance(ln, dict):
            problems.append(f"{ntag}: must be a table")
            continue
        for key in sorted(set(ln) - LATER_NOTE_ALLOWED):
            problems.append(f"{ntag}: unknown field {key!r}")
        if not isinstance(ln.get("date"), dt.date):
            problems.append(f"{ntag}: 'date' must be a TOML date")
        elif isinstance(read_on, dt.date) and ln["date"] < read_on:
            problems.append(f"{ntag}: 'date' is before the reading it corrects ({read_on})")
        if not isinstance(ln.get("text"), str) or _empty(ln["text"]):
            problems.append(f"{ntag}: 'text' must say, in plain words, what is corrected or added and why")

    items = r.get("item", [])
    if not isinstance(items, list):
        problems.append(f"{tag}: 'item' must be a list of [[item]] tables")
        items = []
    seen: set[str] = set()
    counts = {k: 0 for k in ITEM_TARGETS}
    distinct_queries: set[str] = set()
    for i, g in enumerate(items, 1):
        gtag = f"{tag}, item {i}"
        if not isinstance(g, dict):
            problems.append(f"{gtag}: must be a table")
            continue
        for key in sorted(set(g) - ITEM_ALLOWED):
            problems.append(f"{gtag}: unknown field {key!r}")

        # ---- exactly one record, which exists, read once
        named = [k for k in ITEM_TARGETS if k in g]
        target = record = None
        if len(named) != 1:
            problems.append(f"{gtag}: names {'no record' if not named else 'more than one record'}; an item names exactly one leaf, claim or experiment")
        else:
            target = named[0]
            tid = g[target]
            record = by_kind[target].get(tid) if isinstance(tid, str) else None
            if record is None:
                problems.append(f"{gtag}: {target} {tid!r} is not a {target} that exists")
            elif tid in seen:
                problems.append(f"{gtag}: {target} {tid!r} is read twice")
            else:
                seen.add(tid)
                counts[target] += 1

        # ---- the verdict
        verdict = g.get("verdict")
        if verdict not in READING_VERDICTS:
            problems.append(f"{gtag}: verdict must be one of {sorted(READING_VERDICTS)}")
            verdict = None

        # ---- the searches: at least two, each a line of text; a reused line quotes one of them
        queries = g.get("queries")
        if not _text_list(queries):
            problems.append(f"{gtag}: 'queries' must be a list of the searches run, each a line of text")
            queries = []
        elif len(queries) < 2 and _empty(g.get("search_short")):
            problems.append(f"{gtag}: lists {len(queries)} search(es); every record gets at least two, unless "
                            "'search_short' says why the search tool could not give them")
        if "search_short" in g and not isinstance(g["search_short"], str):
            problems.append(f"{gtag}: 'search_short' must be one line of text")
        distinct_queries.update(q.strip() for q in queries)
        reused = g.get("reused")
        if reused is not None:
            if not _text_list(reused):
                problems.append(f"{gtag}: 'reused' must be a list of lines, one per search first run for another record")
            else:
                for line in reused:
                    if not any(q.strip() and q.strip() in line for q in queries):
                        problems.append(f"{gtag}: a 'reused' line must quote one of the item's own queries as written")
                if len(reused) >= len(queries) and queries and _empty(g.get("search_short")):
                    problems.append(f"{gtag}: every search is borrowed; at least two must have been run for this record, "
                                    "unless 'search_short' says why they could not be")

        if _empty(g.get("found")) or not isinstance(g.get("found"), str):
            problems.append(f"{gtag}: needs 'found' (one to three plain sentences on what was found and why it got this verdict)")

        # ---- sources, publications, the line for John
        sources = g.get("sources")
        if sources is not None and (not _text_list(sources) or not all(LINK_RE.match(s) for s in sources)):
            problems.append(f"{gtag}: 'sources' must be a list of links to public records")
        if verdict in ("noted", "moved", "flagged") and _empty(sources):
            problems.append(f"{gtag}: a {verdict!r} item cites at least one source")
        pubs = g.get("publications")
        if pubs is not None:
            if not _text_list(pubs):
                problems.append(f"{gtag}: 'publications' must be a list of publication ids")
            else:
                for pid in pubs:
                    if pid not in publication_ids:
                        problems.append(f"{gtag}: publication {pid!r} is not a publication record that exists")
        if verdict == "noted" and _empty(pubs):
            problems.append(f"{gtag}: a 'noted' item names the publication it logged; if nothing was logged, the verdict is 'quiet' or 'flagged'")
        if verdict == "quiet" and pubs:
            problems.append(f"{gtag}: a 'quiet' item logs no publication; if one was logged, the verdict is 'noted'")
        if verdict == "flagged":
            if _empty(g.get("for_john")) or not isinstance(g.get("for_john"), str):
                problems.append(f"{gtag}: a 'flagged' item carries 'for_john' (the change the reading would have made, the record, and why it is John's)")
        elif "for_john" in g:
            problems.append(f"{gtag}: 'for_john' is only for a 'flagged' item")

        # ---- a resolution mark (decision 19): only on a flagged item, both fields or neither, the
        # date not before the reading's own
        if "resolved_on" in g or "resolved_by" in g:
            if verdict != "flagged":
                problems.append(f"{gtag}: 'resolved_on' and 'resolved_by' are only for a 'flagged' item")
            if "resolved_on" not in g or "resolved_by" not in g:
                problems.append(f"{gtag}: a resolution mark carries both 'resolved_on' and 'resolved_by'")
            if "resolved_on" in g:
                if not isinstance(g["resolved_on"], dt.date):
                    problems.append(f"{gtag}: 'resolved_on' must be a TOML date")
                elif isinstance(read_on, dt.date) and g["resolved_on"] < read_on:
                    problems.append(f"{gtag}: 'resolved_on' is before the reading it resolves ({read_on})")
            if "resolved_by" in g and (not isinstance(g["resolved_by"], str) or _empty(g["resolved_by"])):
                problems.append(f"{gtag}: 'resolved_by' must say, in one line, what resolved the item and in which changelog entry")

        # ---- a move: a leaf only, one rung, matched by a stage revision dated the reading's day
        if verdict == "moved":
            if target != "leaf":
                problems.append(f"{gtag}: only a leaf can be 'moved'; a claim or a self-experiment is at most 'flagged'")
            frm, to = g.get("moved_from"), g.get("moved_to")
            if frm not in STAGE_RANK or to not in STAGE_RANK:
                problems.append(f"{gtag}: a 'moved' item names 'moved_from' and 'moved_to', each one of {STAGES}")
            elif STAGE_RANK[to] != STAGE_RANK[frm] + 1:
                problems.append(f"{gtag}: moves from {frm!r} to {to!r}; a reading moves a leaf exactly one rung up")
            elif record is not None and isinstance(read_on, dt.date):
                matched = any(isinstance(rev, dict) and rev.get("date") == read_on and rev.get("field") == "stage"
                              and rev.get("old") == frm and rev.get("new") == to
                              for rev in (record.get("revision") or []))
                if not matched:
                    problems.append(f"{gtag}: says {g.get('leaf')!r} moved from {frm!r} to {to!r}, but the leaf has no stage "
                                    f"revision dated {read_on} saying so; the reading proposes and the leaf records")
        else:
            for key in ("moved_from", "moved_to"):
                if key in g:
                    problems.append(f"{gtag}: {key!r} is only for a 'moved' item")

        # ---- the sibling check, on the five shared leaves
        if "sibling_stage" in g:
            if target != "leaf" or (record is not None and "sibling" not in record):
                problems.append(f"{gtag}: 'sibling_stage' is only for a leaf that has a sibling on The Upgrade Tree")
            if g["sibling_stage"] not in STAGE_RANK:
                problems.append(f"{gtag}: sibling_stage must be one of {STAGES}")
        if "sibling_agrees" in g and not isinstance(g["sibling_agrees"], bool):
            problems.append(f"{gtag}: 'sibling_agrees' must be true or false")

    # ---- the header counts match the items
    for key, target in (("leaves_read", "leaf"), ("claims_read", "claim"), ("experiments_read", "experiment")):
        if _is_int(r.get(key)) and r[key] != counts[target]:
            problems.append(f"{tag}: {key} says {r[key]} but the items name {counts[target]} {target}(s)")
    if _is_int(r.get("searches")) and r["searches"] != len(distinct_queries):
        problems.append(f"{tag}: searches says {r['searches']} but the items list {len(distinct_queries)} distinct search(es)")


# ---------------------------------------------------------------- commands


def summary(loaded: dict) -> str:
    counts = {k: 0 for k in RECORD_KINDS}
    verify = examples = 0
    for r in loaded["records"]:
        counts[r["_kind"]] += 1
        verify += len(r.get("verify") or [])
        examples += 1 if r.get("example") is True else 0
    per_branch = {k: 0 for k in BRANCH_ORDER}
    for r in loaded["records"]:
        if r["_kind"] == "leaf" and r.get("branch") in per_branch and r.get("status") != "withdrawn":
            per_branch[r["branch"]] += 1
    lines = [
        f"{counts['branch']} of {len(BRANCHES)} branches, {counts['leaf']} leaves "
        f"({', '.join(f'{k} {n}' for k, n in per_branch.items() if n) or 'none'}), "
        f"{counts['claim']} claims, {counts['experiment']} self-experiments, "
        f"{counts['publication']} publications, {counts['scan']} weekly readings, "
        f"{len(loaded['retired'])} retired ids",
        f"{verify} claim(s) marked to verify; {examples} record(s) marked as worked examples",
    ]
    return "\n".join(lines)


def load_and_validate(data_dir: Path, history: bool = True) -> dict:
    """Load, validate, and raise RecordError on any problem. Returns the loaded records."""
    loaded = load_records(data_dir)
    seen = ids_in_history(data_dir) if history else None
    problems = validate(loaded, seen)
    if problems:
        raise RecordError("\n".join(problems))
    loaded["_history_checked"] = seen is not None
    return loaded


def cmd_validate(args: argparse.Namespace) -> int:
    data_dir = Path(args.data).resolve()
    try:
        loaded = load_and_validate(data_dir)
    except RecordError as e:
        print(f"The records in {data_dir} do not pass (docs/record-schema.md):", file=sys.stderr)
        for line in str(e).splitlines():
            print(f"  - {line}", file=sys.stderr)
        return 1
    print(summary(loaded))
    if not loaded["_history_checked"]:
        print("note: not in a git repository, so the renamed-id history check was skipped")
    print("OK: every record follows docs/record-schema.md")
    return 0


# ---------------------------------------------------------------- the headline
#
# docs/method.md (parameters ruled by John 2026-10-16): every tracked leaf supplies the year it
# reaches the clinic (known if it is there, drawn from a triangle over earliest, likely and
# latest if not); a branch is handled in the year its handled_when-th leaf arrives; the run's
# escape year is the latest handled year across the required branches plus a drawn lag, shared by
# every branch in that run; many thousands of runs give the spread. Written 2026-10-16 by the
# leaf session (weekend step 3 of docs/2026-10-16-kickoff.md).

RUNS = 200_000              # method parameter 5
SEED = 2004                 # method parameter 6: the year the phrase became known
LAG = (3, 8, 15)            # method parameter 2: earliest, likely, latest years from the clinic to ordinary people
BEFORE_YEAR = 2050          # method parameter 4
CENTURY_END = 2100          # method parameter 4: a year after this is "not this century"
METHOD_STATUS = "ruled by John 2026-10-16; the lag (parameter 2) went to the outside review of 2026-10-17, which produced no published figure for it, and stays a first guess by John's ruling of 2026-10-17"


def branches_short(loaded: dict) -> list[tuple[str, int, int]]:
    """(branch key, tracked leaves, handled_when) for every branch with too few tracked leaves."""
    branches = {r["key"]: r for r in loaded["records"] if r["_kind"] == "branch"}
    counts = {k: 0 for k in BRANCH_ORDER}
    for r in loaded["records"]:
        if r["_kind"] == "leaf" and r.get("status") == "tracked" and r.get("branch") in counts:
            counts[r["branch"]] += 1
    short = []
    for k in BRANCH_ORDER:
        need = branches[k].get("handled_when", 2) if k in branches else 2
        if counts[k] < need:
            short.append((k, counts[k], need))
    return short


def _year_of(text: str) -> int:
    """The year in a world date written as text ("2019", "2019-09" or "2019-09-18")."""
    return int(str(text)[:4])


def leaf_counts(leaf: dict) -> bool:
    """Whether a leaf feeds the headline: tracked, or withdrawn but already past the clinic rung
    (what happened is not undone by a withdrawal; docs/record-schema.md)."""
    if leaf.get("status") == "tracked":
        return True
    return STAGE_RANK.get(leaf.get("stage"), -1) >= STAGE_RANK[CLINIC]


def clinic_year(leaf: dict) -> int | None:
    """The known year a leaf reached the clinic, or None if it is still below that rung.

    At in-clinical-use it is the year of stage_reached_on. At in-wide-use it is the year of the
    earlier_stage entry for in-clinical-use if there is one, else the year the current stage
    was reached (the latest it could have been)."""
    stage = leaf.get("stage")
    if stage == CLINIC:
        return _year_of(leaf["stage_reached_on"])
    if stage == "in-wide-use":
        for e in leaf.get("earlier_stage") or []:
            if isinstance(e, dict) and e.get("stage") == CLINIC and e.get("reached_on"):
                return _year_of(e["reached_on"])
        return _year_of(leaf["stage_reached_on"])
    return None


def clinic_range(leaf: dict) -> tuple[int, int, int]:
    """(earliest, likely, latest) for the in-clinical-use rung of a leaf below the clinic."""
    for g in leaf["estimate"]["rung"]:
        if g.get("rung") == CLINIC:
            return int(g["earliest"]), int(g["likely"]), int(g["latest"])
    raise RecordError(f"leaf {leaf.get('id')!r} has no estimate rung for {CLINIC!r}")


def compute_headline(loaded: dict, runs: int = RUNS, seed: int = SEED,
                     lag: tuple[int, int, int] = LAG) -> dict:
    """Play the tree out `runs` times and return the headline block (docs/method.md).

    Draw order is fixed so the numbers reproduce exactly: for each branch in order, for each of
    its counting leaves sorted by id, `runs` years are drawn (a leaf already in the clinic
    contributes its known year, with no draw); then `runs` lags are drawn. A leaf's drawn year is
    a triangle over its clinic rung's earliest, likely and latest; the lag is a triangle over the
    three lag years. Every draw is independent of every other (method parameter 7). A run's
    escape year is the latest handled year across the required branches plus the run's lag,
    rounded down to a whole year."""
    import random

    records = loaded["records"]
    branches = {r["key"]: r for r in records if r["_kind"] == "branch"}
    leaves_by_branch: dict[str, list[dict]] = {k: [] for k in BRANCH_ORDER}
    for r in records:
        if r["_kind"] == "leaf" and r.get("branch") in leaves_by_branch and leaf_counts(r):
            leaves_by_branch[r["branch"]].append(r)
    for k in BRANCH_ORDER:
        leaves_by_branch[k].sort(key=lambda leaf: leaf["id"])

    rng = random.Random(seed)
    tri = rng.triangular

    # Years per leaf, per run.
    leaf_years: dict[str, list[float]] = {}
    leaf_facts: dict[str, dict] = {}
    for k in BRANCH_ORDER:
        for leaf in leaves_by_branch[k]:
            known = clinic_year(leaf)
            if known is not None:
                leaf_years[leaf["id"]] = [float(known)] * runs
                leaf_facts[leaf["id"]] = {"id": leaf["id"], "name": leaf["name"], "stage": leaf["stage"],
                                          "known": True, "year": known,
                                          "estimate_status": (leaf.get("estimate") or {}).get("status")}
            else:
                lo, mode, hi = clinic_range(leaf)
                if lo == hi:
                    leaf_years[leaf["id"]] = [float(lo)] * runs
                else:
                    leaf_years[leaf["id"]] = [tri(lo, hi, mode) for _ in range(runs)]
                leaf_facts[leaf["id"]] = {"id": leaf["id"], "name": leaf["name"], "stage": leaf["stage"],
                                          "known": False, "earliest": lo, "likely": mode, "latest": hi,
                                          "estimate_status": leaf["estimate"].get("status")}
    lo_l, mode_l, hi_l = lag
    lags = [tri(lo_l, hi_l, mode_l) for _ in range(runs)]

    # Handled year per branch, per run: the handled_when-th smallest of its leaves' years.
    handled: dict[str, list[float]] = {}
    for k in BRANCH_ORDER:
        need = int(branches[k].get("handled_when", 2))
        cols = [leaf_years[leaf["id"]] for leaf in leaves_by_branch[k]]
        if len(cols) < need:
            raise RecordError(f"branch {k!r} has {len(cols)} counting leaves and needs {need}")
        if need == 1:
            handled[k] = [min(vals) for vals in zip(*cols)]
        else:
            handled[k] = [sorted(vals)[need - 1] for vals in zip(*cols)]

    required = [k for k in BRANCH_ORDER if branches[k].get("required") is True]
    if not required:
        raise RecordError("no branch is marked required, so there is nothing to wait for")
    req_cols = [handled[k] for k in required]
    escape = [int(max(vals) + lags[i]) for i, vals in enumerate(zip(*req_cols))]
    escape.sort()

    def pct(p: float) -> int:
        return escape[min(runs - 1, int(p / 100 * (runs - 1)))]

    def median_of(xs: list[float]) -> int:
        s = sorted(xs)
        return int(s[len(s) // 2])

    before = sum(1 for y in escape if y < BEFORE_YEAR) / runs
    after = sum(1 for y in escape if y > CENTURY_END) / runs

    # Histogram by five-year bin up to the century's end, then one bin for the rest.
    first_bin = (escape[0] // 5) * 5
    bins: list[dict] = []
    start = first_bin
    while start <= CENTURY_END:
        end = start + 4
        n = sum(1 for y in escape if start <= y <= end)
        bins.append({"from": start, "to": end, "share": round(n / runs, 4)})
        start += 5
    n_after = sum(1 for y in escape if y > CENTURY_END)
    bins.append({"from": CENTURY_END + 1, "to": None, "share": round(n_after / runs, 4)})

    branch_block = []
    for k in BRANCH_ORDER:
        b = branches[k]
        branch_block.append({
            "key": k, "name": b.get("name"), "required": b.get("required") is True,
            "handled_when": int(b.get("handled_when", 2)),
            "median_handled_year": median_of(handled[k]),
            "leaves": [leaf_facts[leaf["id"]] for leaf in leaves_by_branch[k]],
        })

    # Every estimate the leaves carry that is still a first pass, and the part of those the headline
    # actually draws from: a leaf already in the clinic has a known year, so its estimate (for the
    # wide-use rung) is kept on the page but is not drawn.
    first_pass = sum(1 for f in leaf_facts.values() if f.get("estimate_status") == "first-pass")
    first_pass_drawn = sum(1 for f in leaf_facts.values() if not f["known"] and f.get("estimate_status") == "first-pass")
    verify_count = sum(len(r.get("verify") or []) for r in records)

    return {
        "computed_on": dt.date.today().isoformat(),
        "method": {
            "document": "docs/method.md",
            "status": METHOD_STATUS,
            "runs": runs,
            "seed": seed,
            "lag_years": {"earliest": lo_l, "likely": mode_l, "latest": hi_l},
            "before_year": BEFORE_YEAR,
            "century_end": CENTURY_END,
            "draw": "a triangle over each leaf's earliest, likely and latest clinic year; the lag likewise; all draws independent",
            "combination": "the latest handled year across the required branches, plus the lag; a branch is handled when its handled_when-th leaf is in clinical use",
        },
        "median_year": pct(50),
        "before_2050": round(before, 4),
        "after_2100": round(after, 4),
        "percentiles": {"p5": pct(5), "p25": pct(25), "p50": pct(50), "p75": pct(75), "p95": pct(95)},
        "histogram": bins,
        "branches": branch_block,
        "counts": {
            "leaves_counted": len(leaf_facts),
            "leaves_in_clinic_already": sum(1 for f in leaf_facts.values() if f["known"]),
            "estimates_first_pass": first_pass,
            "estimates_first_pass_drawn": first_pass_drawn,
            "verify_entries": verify_count,
        },
    }


def history_entry(headline: dict) -> dict:
    """One line of the headline's history: the date, the three numbers, the spread's ends and each
    branch's middle year (ruled by John 2026-10-18, so the site can say when the year moved and which
    branch moved it)."""
    return {
        "computed_on": headline["computed_on"],
        "median_year": headline["median_year"],
        "before_2050": headline["before_2050"],
        "after_2100": headline["after_2100"],
        "p5": headline["percentiles"]["p5"],
        "p95": headline["percentiles"]["p95"],
        "branches": {b["key"]: b["median_handled_year"] for b in headline["branches"]},
    }


def with_history(headline: dict, previous: dict | None) -> dict:
    """The headline with its history: the previous file's list, plus this run. A run on the same day
    that gives exactly the same numbers as the last entry is the same result and adds nothing."""
    history = list((previous or {}).get("history") or [])
    entry = history_entry(headline)
    if not history or history[-1] != entry:
        history.append(entry)
    return {**headline, "history": history}


def cmd_run(args: argparse.Namespace) -> int:
    import json

    data_dir = Path(args.data).resolve()
    try:
        loaded = load_and_validate(data_dir)
    except RecordError as e:
        print("Refusing to run: the records do not pass validation.", file=sys.stderr)
        for line in str(e).splitlines():
            print(f"  - {line}", file=sys.stderr)
        return 1
    short = branches_short(loaded)
    if short:
        total = sum(1 for r in loaded["records"] if r["_kind"] == "leaf" and r.get("status") == "tracked")
        print(f"The leaves are not written yet: {total} tracked leaf record(s) exist, and the headline needs "
              f"every branch to have at least as many as its handled_when (docs/method.md, item 8).")
        for k, have, need in short:
            print(f"  {k}: {have} of {need}")
        print("Nothing computed.")
        return 2
    headline = compute_headline(loaded)
    out = data_dir / "headline.json"
    previous = None
    if out.exists():
        try:
            previous = json.loads(out.read_text(encoding="utf-8"))
        except ValueError:
            previous = None
    headline = with_history(headline, previous)
    out.write_text(json.dumps(headline, indent=2) + "\n", encoding="utf-8")
    p = headline["percentiles"]
    print(f"Escape year: {headline['median_year']} (median of {headline['method']['runs']:,} runs, seed {headline['method']['seed']})")
    print(f"Chance before {BEFORE_YEAR}: {headline['before_2050'] * 100:.1f}%")
    print(f"Not this century (after {CENTURY_END}): {headline['after_2100'] * 100:.1f}%")
    print(f"Spread: 5th percentile {p['p5']}, 25th {p['p25']}, 75th {p['p75']}, 95th {p['p95']}")
    for b in headline["branches"]:
        print(f"  {b['key']}: handled around {b['median_handled_year']} "
              f"({len(b['leaves'])} leaves, {sum(1 for f in b['leaves'] if f['known'])} already in the clinic)")
    print(f"Written to {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Outrunning Ageing: validate the records, compute the headline.")
    parser.add_argument("--data", default=str(ROOT / "data"), help="data folder (default: the repository's data/)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="check every record against docs/record-schema.md")
    sub.add_parser("run", help="compute the headline and write data/headline.json")
    args = parser.parse_args(argv)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "run":
        return cmd_run(args)
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
