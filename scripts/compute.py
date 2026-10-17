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

"run" will play the tree out many thousands of times (docs/method.md) and write the headline.
For now it is a stub: it validates, then refuses until every branch has at least as many tracked
leaves as its handled_when, naming the branches short of it. The leaf session (weekend step 3 of
docs/2026-10-16-kickoff.md) fills it in.

Written 2026-10-16 (weekend step 2 of docs/2026-10-16-kickoff.md).
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
READING_VERDICTS = {"quiet", "noted", "moved", "met", "waiting"}
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

COMMON = {"verify", "notes", "example"}

# Fields each kind may carry (docs/record-schema.md). Required ones are listed separately.
ALLOWED: dict[str, set[str]] = {
    "branch": {"key", "order", "name", "meaning", "hallmarks", "required", "handled_when",
               "what_would_move_this"} | COMMON,
    "leaf": {"id", "name", "branch", "description", "test", "settler", "stage", "stage_reached_on",
             "stage_record", "stage_publication", "earlier_stage", "status", "horizon", "long_shot",
             "mechanism", "breaking_point", "sibling", "estimate", "revision"} | COMMON,
    "claim": {"id", "who", "who_is", "said_on", "where", "link", "quote", "is_paraphrase",
              "paraphrase_seen_in", "commits_to", "due", "leaves", "branches", "about_the_headline",
              "verdict", "verdict_on", "verdict_why"} | COMMON,
    "experiment": {"id", "who", "who_is", "name", "started", "status", "ended", "what", "measures",
                   "claims", "public_record", "link", "leaves", "branches"} | COMMON,
    "publication": {"id", "date", "added_on", "authors", "title", "venue", "link", "finding",
                    "leaves", "branches", "moved_range", "settled_stage"} | COMMON,
    "scan": {"id", "read_on", "covers_from", "summary", "reading"} | COMMON,
}
REQUIRED: dict[str, list[str]] = {
    "branch": ["key", "order", "name", "meaning", "hallmarks", "required", "handled_when"],
    "leaf": ["id", "name", "branch", "description", "test", "settler", "stage", "status", "horizon"],
    "claim": ["id", "who", "who_is", "said_on", "where", "quote", "commits_to", "verdict"],
    "experiment": ["id", "who", "who_is", "started", "status", "what", "measures", "claims",
                   "public_record", "link"],
    "publication": ["id", "date", "added_on", "authors", "title", "venue", "link", "finding",
                    "moved_range", "settled_stage"],
    "scan": ["id", "read_on", "covers_from", "summary", "reading"],
}
# "hallmarks" may be an empty list (the measuring branch), so it is not checked for emptiness.
MAY_BE_EMPTY = {"hallmarks"}

EARLIER_STAGE_ALLOWED = {"stage", "reached_on", "record", "publication"}
ESTIMATE_ALLOWED = {"status", "set_on", "why", "sources", "rung"}
RUNG_ALLOWED = {"rung", "earliest", "likely", "latest"}
REVISION_ALLOWED = {"date", "field", "old", "new", "why", "publication"}
READING_ALLOWED = {"leaf", "verdict", "line", "source", "sibling_stage", "sibling_agrees"}
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
            _check_scan(r, tag, leaves, problems)

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
                   "date", "title", "venue", "finding", "summary", "notes"}
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


def _check_scan(r: dict, tag: str, leaves: dict, problems: list[str]) -> None:
    read_on = r.get("read_on")
    if isinstance(read_on, dt.date) and isinstance(r.get("id"), str) and r["id"] != read_on.isoformat():
        problems.append(f"{tag}: id {r['id']!r} must equal the read_on date {read_on.isoformat()}")
    covers = r.get("covers_from")
    if isinstance(read_on, dt.date) and isinstance(covers, dt.date) and covers > read_on:
        problems.append(f"{tag}: covers_from ({covers}) is after read_on ({read_on})")
    readings = r.get("reading", [])
    if not isinstance(readings, list):
        problems.append(f"{tag}: 'reading' must be a list of [[reading]] tables")
        readings = []
    seen: set[str] = set()
    for i, g in enumerate(readings, 1):
        gtag = f"{tag}, reading {i}"
        if not isinstance(g, dict):
            problems.append(f"{gtag}: must be a table")
            continue
        for key in sorted(set(g) - READING_ALLOWED):
            problems.append(f"{gtag}: unknown field {key!r}")
        leaf_id = g.get("leaf")
        leaf = leaves.get(leaf_id) if isinstance(leaf_id, str) else None
        if leaf is None:
            problems.append(f"{gtag}: leaf {leaf_id!r} is not a leaf that exists")
        elif leaf_id in seen:
            problems.append(f"{gtag}: leaf {leaf_id!r} is read twice")
        else:
            seen.add(leaf_id)
        verdict = g.get("verdict")
        if verdict not in READING_VERDICTS:
            problems.append(f"{gtag}: verdict must be one of {sorted(READING_VERDICTS)}")
        if _empty(g.get("line")) or not isinstance(g.get("line"), str):
            problems.append(f"{gtag}: needs a 'line' (the sentence written on opening)")
        if verdict in ("moved", "met") and leaf is not None and isinstance(read_on, dt.date):
            matched = any(isinstance(rev, dict) and rev.get("date") == read_on for rev in (leaf.get("revision") or []))
            if not matched:
                problems.append(f"{gtag}: says {leaf_id!r} {verdict}, but the leaf has no revision dated {read_on}; "
                                "the reading proposes and the leaf records")
        if "sibling_stage" in g:
            if leaf is not None and "sibling" not in leaf:
                problems.append(f"{gtag}: 'sibling_stage' is only for a leaf that has a sibling on The Upgrade Tree")
            if g["sibling_stage"] not in STAGE_RANK:
                problems.append(f"{gtag}: sibling_stage must be one of {STAGES}")
        if "sibling_agrees" in g and not isinstance(g["sibling_agrees"], bool):
            problems.append(f"{gtag}: 'sibling_agrees' must be true or false")


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


# ---------------------------------------------------------------- the headline (stub)
#
# docs/method.md: every tracked leaf supplies the year it reaches the clinic (known if it is
# there, drawn from a triangle over earliest, likely and latest if not); a branch is handled in
# the year its handled_when-th leaf arrives; the run's escape year is the latest handled year
# across the required branches plus a drawn lag; many thousands of runs give the spread. The
# leaf session fills this in. Until then, `run` refuses with the readiness rule (method item 8).


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


def cmd_run(args: argparse.Namespace) -> int:
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
    print("The leaves are in place, but the headline computation is not written yet (weekend step 3 of "
          "docs/2026-10-16-kickoff.md fills in scripts/compute.py run). Nothing computed.")
    return 3


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Outrunning Ageing: validate the records, compute the headline.")
    parser.add_argument("--data", default=str(ROOT / "data"), help="data folder (default: the repository's data/)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="check every record against docs/record-schema.md")
    sub.add_parser("run", help="compute the headline and write data/headline.json (a stub until the leaves exist)")
    args = parser.parse_args(argv)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "run":
        return cmd_run(args)
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
