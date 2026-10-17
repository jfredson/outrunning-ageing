#!/usr/bin/env python3
"""Outrunning Ageing: turn the records in data/ into JSON for the website.

Plain Python, standard library only. Run from anywhere:

    python3 scripts/export.py                  write site/src/data/records.json
    python3 scripts/export.py --check          validate and print the counts, write nothing
    python3 scripts/export.py --out DIR        write the JSON somewhere else
    python3 scripts/export.py --data DIR       read a different data folder (for tests)
    python3 scripts/export.py --headline FILE  read the headline numbers from another file

The records are read with the same loader and validator as scripts/compute.py, so the site can
never show a record that fails the schema: if validation fails, nothing is written and the
build stops. The site (site/) reads the JSON at build time. Nothing in the browser touches TOML.
This is the only reader of the data, so the site can never show two numbers that disagree
(tracker pattern, rule 1.5).

What the JSON holds for the holding version of the site (2026-10-16): the date and source
version it was built from, the counts of each kind of record (worked examples counted
separately), the eight branches with how many leaves each has, a short form of every record
for the lists, the latest weekly reading that is not a worked example (or null, so the strip can
say no reading has run), and the headline read from data/headline.json when `compute.py run`
has written it, otherwise a plain reason that it is not computed yet. The site session widens
it to the full records as the pages that need them are built.

Written 2026-10-16.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))

import compute  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("America/Los_Angeles")

STAGE_LABELS: dict[str, str] = {
    "idea-only": "Idea only",
    "shown-in-animals": "Shown in animals",
    "first-human": "First human",
    "in-clinical-use": "In clinical use",
    "in-wide-use": "In wide use",
}
HORIZON_WORDS: dict[str, str] = {
    "near": "could reach its next rung within 1 to 5 years",
    "mid": "could reach its next rung within 5 to 20 years",
    "far": "longer than 20 years away, if ever",
    "top": "already in wide use",
}
VERDICT_WORDS: dict[str, str] = {
    "not-yet-due": "Not yet due",
    "delivered": "Delivered",
    "missed": "Missed",
    "unfalsifiable": "Cannot be settled",
}


def short_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def clean(value):
    """Make a record JSON-safe: dates become year-month-day text, private keys are dropped."""
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items() if not str(k).startswith("_")}
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    return value


def text(value) -> str:
    return value.strip() if isinstance(value, str) else ""


def load_headline(path: Path | None) -> dict | None:
    """The output of `compute.py run`, if it exists and carries the three numbers; else None."""
    if path is None or not path.exists():
        return None
    try:
        h = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not all(k in h for k in ("median_year", "before_2050", "after_2100")):
        return None
    return h


def build_export(loaded: dict, headline_file: Path | None) -> dict:
    records = loaded["records"]
    by_kind: dict[str, list[dict]] = {k: [] for k in compute.RECORD_KINDS}
    for r in records:
        by_kind[r["_kind"]].append(r)

    leaves = sorted(by_kind["leaf"], key=lambda r: (compute.BRANCHES.get(r["branch"], 99), r["name"]))
    tracked = [l for l in leaves if l.get("status") == "tracked"]

    branches = []
    for b in sorted(by_kind["branch"], key=lambda r: r["order"]):
        mine = [l for l in leaves if l["branch"] == b["key"]]
        branches.append({
            "key": b["key"], "order": b["order"], "name": b["name"], "meaning": text(b["meaning"]),
            "hallmarks": b.get("hallmarks", []), "required": b["required"], "handled_when": b["handled_when"],
            "what_would_move_this": text(b.get("what_would_move_this")),
            "leaves": len(mine), "leaves_tracked": sum(1 for l in mine if l.get("status") == "tracked"),
            "furthest_stage": max((l["stage"] for l in mine), key=compute.STAGE_RANK.get, default=None),
            "path": f"/branches/{b['key']}/",
        })

    leaf_briefs = [{
        "id": l["id"], "name": l["name"], "branch": l["branch"], "stage": l["stage"],
        "stage_label": STAGE_LABELS[l["stage"]], "stage_reached_on": l.get("stage_reached_on"),
        "status": l["status"], "horizon": l["horizon"], "horizon_words": HORIZON_WORDS[l["horizon"]],
        "sibling": l.get("sibling"), "estimate_status": (l.get("estimate") or {}).get("status"),
        "example": l.get("example") is True, "path": f"/leaves/{l['id']}/",
    } for l in leaves]

    claims = [{
        "id": c["id"], "who": c["who"], "said_on": c["said_on"], "commits_to": text(c["commits_to"]),
        "due": c.get("due"), "verdict": c["verdict"], "verdict_label": VERDICT_WORDS[c["verdict"]],
        "about_the_headline": c.get("about_the_headline") is True,
        "leaves": c.get("leaves", []), "branches": c.get("branches", []),
        "example": c.get("example") is True, "path": f"/claims/#{c['id']}",
    } for c in sorted(by_kind["claim"], key=lambda r: r["said_on"])]

    experiments = [{
        "id": e["id"], "who": e["who"], "name": e.get("name", ""), "started": e["started"], "status": e["status"],
        "leaves": e.get("leaves", []), "branches": e.get("branches", []),
        "example": e.get("example") is True, "path": f"/self-experiments/#{e['id']}",
    } for e in sorted(by_kind["experiment"], key=lambda r: r["started"])]

    publications = [{
        "id": p["id"], "title": p["title"], "date": p["date"], "added_on": p["added_on"].isoformat(),
        "authors": p["authors"], "moved_range": p["moved_range"], "settled_stage": p["settled_stage"],
        "leaves": p.get("leaves", []), "branches": p.get("branches", []),
        "example": p.get("example") is True, "path": f"/story/#{p['id']}",
    } for p in sorted(by_kind["publication"], key=lambda r: (r["added_on"], r["id"]), reverse=True)]

    # The latest weekly reading that is a real reading, not a worked example of the layout.
    real_scans = sorted((s for s in by_kind["scan"] if s.get("example") is not True), key=lambda r: r["read_on"])
    reading = None
    if real_scans:
        s = real_scans[-1]
        verdicts = [g["verdict"] for g in s["reading"]]
        reading = {
            "read_on": s["read_on"].isoformat(), "covers_from": s["covers_from"].isoformat(),
            "summary": text(s["summary"]), "read": len(verdicts),
            "moved": [g["leaf"] for g in s["reading"] if g["verdict"] in ("moved", "met")],
            "path": f"/reading/#{s['id']}",
        }

    examples = [{"kind": r["_kind"], "id": r.get("id") or r.get("key")} for r in records if r.get("example") is True]

    # The headline: read from compute.py run's output when it exists; else say why not, in words.
    h = load_headline(headline_file)
    if h is None:
        short = compute.branches_short(loaded)
        if short:
            n = len(tracked)
            reason = (f"The year is not computed yet: {n} of the treatments and tools the tree needs "
                      f"{'is' if n == 1 else 'are'} written up so far, and the calculation needs every branch "
                      f"to have at least {min(b['handled_when'] for b in by_kind['branch']) if by_kind['branch'] else 2}.")
        else:
            reason = "The year is not computed yet: the leaves are in place and the calculation is being written."
        headline = {"available": False, "reason": reason}
    else:
        headline = {"available": True, **{k: v for k, v in h.items()}, "file": str(headline_file)}

    counts = {
        "branches": len(branches), "branches_expected": len(compute.BRANCHES),
        "leaves": len(leaves), "leaves_tracked": len(tracked),
        "claims": len(claims), "experiments": len(experiments), "publications": len(publications),
        "scans": len(by_kind["scan"]), "scans_real": len(real_scans),
        "retired": len(loaded["retired"]),
        "verify": sum(len(r.get("verify") or []) for r in records),
        "examples": len(examples),
    }

    return {
        "exported_on": dt.datetime.now(TZ).date().isoformat(),
        "commit": short_commit(),
        "counts": counts,
        "headline": headline,
        "fixed_dates": {"before": 2050, "century_end": 2100},
        "reading": reading,
        "stages": [{"key": k, "label": STAGE_LABELS[k], "rank": i} for i, k in enumerate(compute.STAGES)],
        "branches": branches,
        "leaves": leaf_briefs,
        "claims": claims,
        "experiments": experiments,
        "publications": publications,
        "examples": examples,
        "retired": clean(loaded["retired"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the site's JSON from the records in data/.")
    parser.add_argument("--data", default=str(ROOT / "data"))
    parser.add_argument("--out", default=str(ROOT / "site" / "src" / "data"))
    parser.add_argument("--headline", default=None, help="the headline JSON (default: DATA/headline.json)")
    parser.add_argument("--check", action="store_true", help="validate and print counts, write nothing")
    args = parser.parse_args(argv)

    data_dir = Path(args.data).resolve()
    try:
        loaded = compute.load_and_validate(data_dir)
    except compute.RecordError as e:
        print("The records do not pass validation; nothing written:", file=sys.stderr)
        for line in str(e).splitlines():
            print(f"  - {line}", file=sys.stderr)
        return 1

    headline_file = Path(args.headline).resolve() if args.headline else data_dir / "headline.json"
    export = build_export(loaded, headline_file)
    c = export["counts"]
    print(f"{c['branches']} of {c['branches_expected']} branches, {c['leaves']} leaves ({c['leaves_tracked']} tracked), "
          f"{c['claims']} claims, {c['experiments']} self-experiments, {c['publications']} publications, "
          f"{c['scans']} weekly readings ({c['scans_real']} real); {c['verify']} claim(s) to verify; "
          f"{c['examples']} worked example(s); headline {'computed' if export['headline']['available'] else 'not computed'}; "
          f"version {export['commit'] or 'unknown'}")
    if args.check:
        return 0
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "records.json").write_text(json.dumps(export, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out / 'records.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
