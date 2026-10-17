#!/usr/bin/env python3
"""Outrunning Ageing: turn the records in data/ into JSON for the website.

Plain Python, standard library only. Run from anywhere:

    python3 scripts/export.py                  write site/src/data/records.json
    python3 scripts/export.py --check          validate and print the counts, write nothing
    python3 scripts/export.py --out DIR        write the JSON somewhere else
    python3 scripts/export.py --data DIR       read a different data folder (for tests)
    python3 scripts/export.py --headline FILE  read the headline numbers from another file
    python3 scripts/export.py --changelog FILE read the changelog from another file

The records are read with the same loader and validator as scripts/compute.py, so the site can
never show a record that fails the schema: if validation fails, nothing is written and the
build stops. The site (site/) reads the JSON at build time. Nothing in the browser touches TOML.
This is the only reader of the data, so the site can never show two numbers that disagree
(tracker pattern, rule 1.5).

What the JSON holds (widened 2026-10-17 by the site session from the holding version of
2026-10-16): the date and source version it was built from; the counts of each kind of record;
the headline read from data/headline.json (the whole file, with a worked run at every leaf's
most likely year added for the method page) or a plain reason it is not computed; the eight
branches with their counts, their furthest stage, their leaves, and the claims, self-experiments
and publications that bear on them; every leaf in full, with its stage ladder, its estimate,
its revision log, the last three weekly readings of it, and the claims, self-experiments and
publications that name it; every claim, self-experiment and publication in full, with the
records each points at resolved to names and addresses; the story so far (the publications log
read as dated entries, each saying what it moved, plus the changelog's dated days); the real
weekly readings, newest first, each with its items grouped by branch, the flagged items still
waiting on John, and the latest reading for the home page's strip; and the retired ids. Worked
examples of the layout are counted separately and an example reading is never the site's
reading (record layout, decision 13).

Written 2026-10-16; widened 2026-10-17 by the site session, and again the same day by the
weekly-reading session (items for claims and self-experiments, the four verdicts, the groups and
the waiting list).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))

import compute  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("America/Los_Angeles")
SIBLING_SITE = "https://theupgradetree.com"

STAGE_LABELS: dict[str, str] = {
    "idea-only": "Idea only",
    "shown-in-animals": "Shown in animals",
    "first-human": "First human",
    "in-clinical-use": "In clinical use",
    "in-wide-use": "In wide use",
}
# The ladder's rungs in plain words (docs/record-schema.md, "The stage ladder").
STAGE_MEANINGS: dict[str, str] = {
    "idea-only": "Proposed or worked on, but not yet shown to work in any living animal.",
    "shown-in-animals": "Shown to work in a living animal, in a peer-reviewed report.",
    "first-human": "At least one person has had it, with a public record of that result.",
    "in-clinical-use": "A regulator somewhere has approved it, or it is in routine use in a named clinical setting, so a doctor can give it to a patient outside a trial.",
    "in-wide-use": "Available to the general public in at least one country without joining a trial, and taken up by many people.",
}
HORIZON_WORDS: dict[str, str] = {
    "near": "could reach its next rung within 1 to 5 years",
    "mid": "could reach its next rung within 5 to 20 years",
    "far": "longer than 20 years away, if ever",
    "top": "already in wide use",
}
HORIZON_LABELS: dict[str, str] = {
    "near": "Next rung within 1 to 5 years",
    "mid": "Next rung within 5 to 20 years",
    "far": "Next rung more than 20 years away, if ever",
    "top": "Already in wide use",
}
VERDICT_WORDS: dict[str, str] = {
    "not-yet-due": "Not yet due",
    "delivered": "Delivered",
    "missed": "Missed",
    "unfalsifiable": "Cannot be settled",
}
VERDICT_MEANINGS: dict[str, str] = {
    "not-yet-due": "The date or result it commits to has not arrived yet. It is judged when it does.",
    "delivered": "What it committed to happened by the date it named, on a public record.",
    "missed": "The date passed and what it committed to had not happened. A claim its maker later withdrew stays missed.",
    "unfalsifiable": "It names no date and no result that could ever settle it, so it can never be judged delivered or missed.",
}
# The weekly reading's four verdicts (docs/record-schema.md, "The scan record"; docs/weekly-reading.md).
READING_VERDICTS: dict[str, tuple[str, str]] = {
    "quiet": ("Quiet", "Nothing in the week bore on what would count for this record."),
    "noted": ("Noted", "Something in the week bore on it and was logged in the publications log, and what would count was not met: a paper short of the test, a regulator's step, a first dose with no measured result."),
    "moved": ("Moved a rung", "A public record of the kind the treatment itself names showed its next rung reached, so the reading moved it one rung, with a dated revision on the treatment's page saying so."),
    "flagged": ("Left for the author", "Something the reading may not decide on its own: a record older than the week that the entry did not know, a press-only report, a claim whose date has passed, a test that no longer fits. The line says what the author is asked to rule on."),
}
READING_KINDS: dict[str, str] = {"leaf": "Treatment", "claim": "Claim", "experiment": "Self-experiment"}
WHOLE_QUESTION = {"key": "the-whole-question", "name": "The whole question", "path": "/claims/"}
# The twelve hallmarks in plain words (docs/record-schema.md, "The twelve hallmarks and the eight branches").
HALLMARK_WORDS: dict[str, str] = {
    "genomic-instability": "mutations accumulating in DNA",
    "telomere-attrition": "the shortening of chromosome ends",
    "epigenetic-alterations": "drift in the marks that say which genes a cell reads",
    "loss-of-proteostasis": "misfolded proteins and failed protein quality control",
    "disabled-macroautophagy": "the cell's recycling of its own worn parts failing",
    "deregulated-nutrient-sensing": "the pathways that sense food running wrong",
    "mitochondrial-dysfunction": "the cell's power plants failing",
    "cellular-senescence": "cells that stop dividing but will not die, and poison their neighbours",
    "stem-cell-exhaustion": "the reserve of cells that replace lost tissue running out",
    "altered-intercellular-communication": "the signals cells send each other going wrong",
    "chronic-inflammation": "low-grade inflammation that never switches off",
    "dysbiosis": "the gut's community of microbes going out of balance",
}
# The story so far's kinds of entry (tracker pattern, rule 4.2), as this site's records supply them.
STORY_KINDS: dict[str, str] = {
    "stage-settled": "Settled a stage",
    "moved-range": "Moved an estimate",
    "held": "Read; moved nothing",
    "revision": "A record was revised",
    "reading": "The weekly reading moved a rung",
}
DATE_HEADER = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$")


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


def iso(value) -> str | None:
    """A TOML date as year-month-day text; None when absent."""
    if value is None:
        return None
    return value.isoformat() if isinstance(value, (dt.date, dt.datetime)) else str(value)


def record_file(r: dict, data_dir: Path) -> str:
    """The record's path inside the repository, for the 'this entry is ...' line."""
    p = r.get("_path")
    if p is None:
        return ""
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except ValueError:
        return f"data/{Path(p).name}"


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


def read_changelog(path: Path | None) -> dict:
    """Split CHANGELOG.md into its dated days, each a list of plain lines (newest first).
    Copied from The Upgrade Tree's scripts/export.py (export_changelog) on 2026-10-17."""
    if path is None or not path.exists():
        return {"source": "", "intro": "", "days": []}
    days: list[dict] = []
    intro: list[str] = []
    current: dict | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        m = DATE_HEADER.match(line)
        if m:
            current = {"date": m.group(1), "items": []}
            days.append(current)
            continue
        if current is None:
            if line and not line.startswith("# "):
                intro.append(line)
            continue
        if line.startswith("- "):
            current["items"].append(line[2:].strip())
        elif line.strip() and current["items"]:
            current["items"][-1] += " " + line.strip()
    return {"source": path.name, "intro": " ".join(intro), "days": days}


def build_export(loaded: dict, headline_file: Path | None, changelog_file: Path | None = None,
                 data_dir: Path | None = None) -> dict:
    records = loaded["records"]
    data_dir = data_dir or (ROOT / "data")
    by_kind: dict[str, list[dict]] = {k: [] for k in compute.RECORD_KINDS}
    for r in records:
        by_kind[r["_kind"]].append(r)

    branch_recs = sorted(by_kind["branch"], key=lambda r: r["order"])
    branch_name = {b["key"]: b["name"] for b in branch_recs}
    branch_path = {b["key"]: f"/branches/{b['key']}/" for b in branch_recs}

    leaves = sorted(by_kind["leaf"], key=lambda r: (compute.BRANCHES.get(r["branch"], 99), r["name"]))
    tracked = [l for l in leaves if l.get("status") == "tracked"]
    leaf_by_id = {l["id"]: l for l in leaves}
    pub_by_id = {p["id"]: p for p in by_kind["publication"]}

    claims_sorted = sorted(by_kind["claim"], key=lambda r: (r["said_on"], r["id"]))
    experiments_sorted = sorted(by_kind["experiment"], key=lambda r: (r["started"], r["id"]))
    pubs_sorted = sorted(by_kind["publication"], key=lambda r: (r["added_on"], r["id"]), reverse=True)
    real_scans = sorted((s for s in by_kind["scan"] if s.get("example") is not True), key=lambda r: r["read_on"])

    h = load_headline(headline_file)
    headline_leaf: dict[str, dict] = {}
    headline_branch: dict[str, dict] = {}
    if h is not None:
        for hb in h.get("branches", []):
            headline_branch[hb["key"]] = hb
            for hl in hb.get("leaves", []):
                headline_leaf[hl["id"]] = hl

    # ---- small references, so a page never has to look a record up by id ----
    def leaf_ref(lid: str) -> dict:
        l = leaf_by_id[lid]
        return {"id": lid, "name": l["name"], "path": f"/leaves/{lid}/", "branch": l["branch"],
                "branch_name": branch_name.get(l["branch"], l["branch"]),
                "stage": l["stage"], "stage_label": STAGE_LABELS[l["stage"]],
                "stage_rank": compute.STAGE_RANK[l["stage"]], "horizon": l["horizon"],
                "status": l["status"], "example": l.get("example") is True}

    def branch_ref(key: str) -> dict:
        return {"key": key, "name": branch_name.get(key, key), "path": branch_path.get(key, f"/branches/{key}/")}

    def pub_ref(pid: str) -> dict:
        p = pub_by_id[pid]
        return {"id": pid, "title": p["title"], "date": p["date"], "path": f"/story/#{pid}",
                "link": p["link"], "first_author": (p["authors"] or [""])[0],
                "authors_short": authors_short(p["authors"])}

    def claim_ref(c: dict) -> dict:
        return {"id": c["id"], "who": c["who"], "said_on": c["said_on"], "commits_to": text(c["commits_to"]),
                "due": c.get("due"), "verdict": c["verdict"], "verdict_label": VERDICT_WORDS[c["verdict"]],
                "path": f"/claims/#{c['id']}"}

    def experiment_ref(e: dict) -> dict:
        return {"id": e["id"], "who": e["who"], "name": e.get("name", ""), "started": e["started"],
                "status": e["status"], "path": f"/self-experiments/#{e['id']}"}

    def targets(r: dict) -> tuple[list[str], list[str]]:
        return list(r.get("leaves", [])), list(r.get("branches", []))

    # ---- which records point at which leaf or branch ----
    claims_for_leaf: dict[str, list[dict]] = {l["id"]: [] for l in leaves}
    claims_for_branch: dict[str, list[dict]] = {b["key"]: [] for b in branch_recs}
    for c in claims_sorted:
        ls, bs = targets(c)
        for lid in ls:
            claims_for_leaf[lid].append(claim_ref(c))
        for bk in set(bs) | {leaf_by_id[lid]["branch"] for lid in ls}:
            claims_for_branch[bk].append(claim_ref(c))
    experiments_for_leaf: dict[str, list[dict]] = {l["id"]: [] for l in leaves}
    experiments_for_branch: dict[str, list[dict]] = {b["key"]: [] for b in branch_recs}
    for e in experiments_sorted:
        ls, bs = targets(e)
        for lid in ls:
            experiments_for_leaf[lid].append(experiment_ref(e))
        for bk in set(bs) | {leaf_by_id[lid]["branch"] for lid in ls}:
            experiments_for_branch[bk].append(experiment_ref(e))
    pubs_for_leaf: dict[str, list[dict]] = {l["id"]: [] for l in leaves}
    pubs_for_branch: dict[str, list[dict]] = {b["key"]: [] for b in branch_recs}
    # A publication is behind a leaf if the leaf names it (stage record, earlier stage, estimate
    # source, revision) or the publication names the leaf.
    leaf_pub_ids: dict[str, list[str]] = {}
    for l in leaves:
        ids: list[str] = []
        if l.get("stage_publication"):
            ids.append(l["stage_publication"])
        for e in l.get("earlier_stage", []):
            if e.get("publication"):
                ids.append(e["publication"])
        for pid in (l.get("estimate") or {}).get("sources", []) or []:
            ids.append(pid)
        for rv in l.get("revision", []):
            if rv.get("publication"):
                ids.append(rv["publication"])
        leaf_pub_ids[l["id"]] = ids
    for p in pubs_sorted:
        ls, bs = targets(p)
        for lid in ls:
            if p["id"] not in leaf_pub_ids[lid]:
                leaf_pub_ids[lid].append(p["id"])
    pubs_settle: dict[str, list[dict]] = {p["id"]: [] for p in pubs_sorted}  # pub id -> leaves whose rung it settles
    pubs_moved: dict[str, list[dict]] = {p["id"]: [] for p in pubs_sorted}   # pub id -> revisions naming it
    for l in leaves:
        if l.get("stage_publication"):
            pubs_settle[l["stage_publication"]].append({**leaf_ref(l["id"]), "rung": l["stage"], "rung_label": STAGE_LABELS[l["stage"]]})
        for e in l.get("earlier_stage", []):
            if e.get("publication"):
                pubs_settle[e["publication"]].append({**leaf_ref(l["id"]), "rung": e["stage"], "rung_label": STAGE_LABELS[e["stage"]]})
        for rv in l.get("revision", []):
            if rv.get("publication"):
                pubs_moved[rv["publication"]].append({**leaf_ref(l["id"]), "date": iso(rv["date"]), "field": rv["field"],
                                                       "old": clean(rv.get("old")), "new": clean(rv.get("new")), "why": text(rv.get("why"))})
    for lid, ids in leaf_pub_ids.items():
        seen: set[str] = set()
        for pid in ids:
            if pid in seen or pid not in pub_by_id:
                continue
            seen.add(pid)
            ref = pub_ref(pid)
            ref["settles_rung"] = next((s["rung_label"] for s in pubs_settle[pid] if s["id"] == lid), None)
            pubs_for_leaf[lid].append(ref)
    for p in pubs_sorted:
        ls, bs = targets(p)
        for bk in set(bs) | {leaf_by_id[lid]["branch"] for lid in ls} | {s["branch"] for s in pubs_settle[p["id"]]}:
            pubs_for_branch[bk].append(pub_ref(p["id"]))

    # ---- the weekly readings (real ones only; an example reading is never the site's reading) ----
    # Each reading's items are grouped by branch for the reading page: a treatment under its branch,
    # a claim or a self-experiment under the first branch it bears on (by the tree's order), and a
    # claim about the headline itself under "the whole question". A flagged item waits on John until
    # a later reading reads the record again with another verdict, or the record carries a dated
    # change on or after the reading that names it (docs/weekly-reading.md, design choice 9).
    claim_by_id = {c["id"]: c for c in claims_sorted}
    exp_by_id = {e["id"]: e for e in experiments_sorted}

    def first_branch(ls: list[str], bs: list[str]) -> str | None:
        keys = set(bs) | {leaf_by_id[lid]["branch"] for lid in ls if lid in leaf_by_id}
        return min(keys, key=lambda k: compute.BRANCHES.get(k, 99)) if keys else None

    def item_of(g: dict) -> dict:
        kind = next(k for k in ("leaf", "claim", "experiment") if k in g)
        rid = g[kind]
        if kind == "leaf":
            ref = leaf_ref(rid)
            group, name = ref["branch"], ref["name"]
        elif kind == "claim":
            c = claim_by_id[rid]
            ref = claim_ref(c)
            ls, bs = targets(c)
            group = WHOLE_QUESTION["key"] if c.get("about_the_headline") is True else first_branch(ls, bs)
            name = f"{c['who']}, {c['said_on'][:4]}: {text(c['commits_to'])}"
        else:
            e = exp_by_id[rid]
            ref = experiment_ref(e)
            ls, bs = targets(e)
            group = first_branch(ls, bs)
            name = f"{e['who']}{', ' + e['name'] if e.get('name') else ''}"
        verdict = g["verdict"]
        return {
            "kind": kind, "kind_label": READING_KINDS[kind], "id": rid, "name": name, "record": ref,
            "group": group or WHOLE_QUESTION["key"],
            "verdict": verdict, "verdict_label": READING_VERDICTS[verdict][0],
            "queries": list(g.get("queries") or []), "reused": list(g.get("reused") or []),
            "search_short": text(g.get("search_short")), "found": text(g["found"]),
            "sources": list(g.get("sources") or []),
            "publications": [pub_ref(pid) for pid in (g.get("publications") or []) if pid in pub_by_id],
            "moved_from": g.get("moved_from"), "moved_to": g.get("moved_to"),
            "moved_from_label": STAGE_LABELS.get(g.get("moved_from")), "moved_to_label": STAGE_LABELS.get(g.get("moved_to")),
            "for_john": text(g.get("for_john")),
            "sibling_stage": g.get("sibling_stage"),
            "sibling_stage_label": STAGE_LABELS.get(g.get("sibling_stage")) if g.get("sibling_stage") else None,
            "sibling_agrees": g.get("sibling_agrees"),
        }

    readings_out = []
    readings_for: dict[str, dict[str, list[dict]]] = {
        "leaf": {l["id"]: [] for l in leaves}, "claim": {c["id"]: [] for c in claims_sorted},
        "experiment": {e["id"]: [] for e in experiments_sorted},
    }
    scans_desc = list(reversed(real_scans))
    for s in scans_desc:
        items = [item_of(g) for g in s["item"]]
        for it in items:
            readings_for[it["kind"]][it["id"]].append({
                "read_on": iso(s["read_on"]), "path": f"/reading/#{s['id']}", "verdict": it["verdict"],
                "verdict_label": it["verdict_label"], "found": it["found"], "sources": it["sources"],
                "search_short": it["search_short"], "for_john": it["for_john"],
                "moved_from_label": it["moved_from_label"], "moved_to_label": it["moved_to_label"],
                "publications": it["publications"],
            })
        groups = []
        for b in branch_recs:
            mine = [it for it in items if it["group"] == b["key"]]
            if mine:
                groups.append({**branch_ref(b["key"]), "items": mine})
        whole = [it for it in items if it["group"] == WHOLE_QUESTION["key"]]
        if whole:
            groups.append({**WHOLE_QUESTION, "items": whole})
        counts = {k: sum(1 for i in items if i["verdict"] == k) for k in READING_VERDICTS}
        readings_out.append({
            "id": s["id"], "read_on": iso(s["read_on"]), "covers_from": iso(s["covers_from"]),
            "ran_at": s["ran_at"], "run_by": s["run_by"], "commit_before": s["commit_before"],
            "summary": text(s["summary"]), "read": len(items),
            "leaves_read": s["leaves_read"], "claims_read": s["claims_read"], "experiments_read": s["experiments_read"],
            "searches": s["searches"], "short_of_two": sum(1 for i in items if i["search_short"]),
            "counts": counts,
            "moved": [i["record"] for i in items if i["verdict"] == "moved"],
            "logged": sorted({p["id"] for i in items for p in i["publications"]}),
            "items": items, "groups": groups,
            "notes": text(s.get("notes")), "verify": list(s.get("verify") or []),
            "file": record_file(s, data_dir), "path": f"/reading/#{s['id']}",
        })

    # Flagged items still waiting on John, newest reading first.
    def cleared(item: dict, read_on: dt.date) -> bool:
        later = [s2 for s2 in real_scans if s2["read_on"] > read_on]
        for s2 in later:
            for g in s2["item"]:
                if g.get(item["kind"]) == item["id"] and g["verdict"] != "flagged":
                    return True
        if item["kind"] == "leaf":
            for rv in leaf_by_id[item["id"]].get("revision", []):
                if isinstance(rv.get("date"), dt.date) and rv["date"] >= read_on and read_on.isoformat() in text(rv.get("why")):
                    return True
        if item["kind"] == "claim":
            v_on = claim_by_id[item["id"]].get("verdict_on")
            if isinstance(v_on, dt.date) and v_on >= read_on:
                return True
        return False

    waiting = []
    for s, rd in zip(scans_desc, readings_out):
        for it in rd["items"]:
            if it["verdict"] == "flagged" and not cleared(it, s["read_on"]):
                waiting.append({"reading": rd["id"], "read_on": rd["read_on"], "path": rd["path"], **it})
    for rd in readings_out:
        rd["waiting"] = sum(1 for w in waiting if w["reading"] == rd["id"])

    reading = None
    if readings_out:
        r0 = readings_out[0]
        reading = {"read_on": r0["read_on"], "covers_from": r0["covers_from"], "summary": r0["summary"],
                   "read": r0["read"], "leaves_read": r0["leaves_read"], "claims_read": r0["claims_read"],
                   "experiments_read": r0["experiments_read"], "searches": r0["searches"],
                   "moved": [m["id"] for m in r0["moved"]], "movers": r0["moved"],
                   "logged": len(r0["logged"]), "flagged": r0["counts"]["flagged"], "waiting": r0["waiting"],
                   "path": r0["path"]}
    readings_for_leaf = readings_for["leaf"]

    # ---- the leaves in full ----
    def ladder_for(l: dict) -> list[dict]:
        cur = compute.STAGE_RANK[l["stage"]]
        earlier = {e["stage"]: e for e in l.get("earlier_stage", [])}
        rungs = []
        for i, key in enumerate(compute.STAGES):
            rung = {"key": key, "label": STAGE_LABELS[key], "reached": i <= cur, "current": i == cur,
                    "reached_on": None, "record": None, "publication": None}
            if i == cur and key != "idea-only":
                rung["reached_on"] = l.get("stage_reached_on")
                rung["record"] = l.get("stage_record")
                rung["publication"] = pub_ref(l["stage_publication"]) if l.get("stage_publication") else None
            elif i < cur and key in earlier:
                e = earlier[key]
                rung["reached_on"] = e.get("reached_on")
                rung["record"] = e.get("record")
                rung["publication"] = pub_ref(e["publication"]) if e.get("publication") else None
            rungs.append(rung)
        return rungs

    leaves_out = []
    for l in leaves:
        est = l.get("estimate") or None
        estimate = None
        if est:
            estimate = {
                "status": est["status"], "set_on": iso(est["set_on"]), "why": text(est["why"]),
                "sources": [pub_ref(pid) for pid in (est.get("sources") or []) if pid in pub_by_id],
                "rungs": [{"rung": r["rung"], "rung_label": STAGE_LABELS[r["rung"]], "earliest": r["earliest"],
                           "likely": r["likely"], "latest": r["latest"],
                           "feeds_headline": r["rung"] == "in-clinical-use"} for r in est.get("rung", [])],
            }
        clinic = compute.clinic_year(l) if compute.STAGE_RANK[l["stage"]] >= compute.STAGE_RANK["in-clinical-use"] else None
        hl = headline_leaf.get(l["id"])
        leaves_out.append({
            "id": l["id"], "name": l["name"], "path": f"/leaves/{l['id']}/",
            "branch": l["branch"], "branch_name": branch_name.get(l["branch"], l["branch"]), "branch_path": branch_path.get(l["branch"]),
            "description": text(l["description"]), "test": text(l["test"]), "settler": text(l["settler"]),
            "stage": l["stage"], "stage_rank": compute.STAGE_RANK[l["stage"]], "stage_label": STAGE_LABELS[l["stage"]],
            "stage_reached_on": l.get("stage_reached_on"), "stage_record": l.get("stage_record"),
            "stage_publication": pub_ref(l["stage_publication"]) if l.get("stage_publication") else None,
            "ladder": ladder_for(l),
            "status": l["status"], "horizon": l["horizon"], "horizon_words": HORIZON_WORDS[l["horizon"]],
            "horizon_label": HORIZON_LABELS[l["horizon"]],
            "long_shot": l.get("long_shot") is True, "mechanism": text(l.get("mechanism")), "breaking_point": text(l.get("breaking_point")),
            "sibling": l.get("sibling"),
            "sibling_url": f"{SIBLING_SITE}/branches/lifespan/{l['sibling']}/" if l.get("sibling") else None,
            "estimate": estimate, "estimate_status": est["status"] if est else None,
            "clinic_year": clinic,
            "headline_draw": ({"known": hl.get("known", False), "year": hl.get("year"), "earliest": hl.get("earliest"),
                               "likely": hl.get("likely"), "latest": hl.get("latest")} if hl else None),
            "revisions": [{"date": iso(rv["date"]), "field": rv["field"], "old": clean(rv.get("old")), "new": clean(rv.get("new")),
                           "why": text(rv.get("why")), "publication": pub_ref(rv["publication"]) if rv.get("publication") else None}
                          for rv in l.get("revision", [])],
            "verify": list(l.get("verify") or []), "notes": text(l.get("notes")), "example": l.get("example") is True,
            "claims": claims_for_leaf[l["id"]], "experiments": experiments_for_leaf[l["id"]],
            "publications": pubs_for_leaf[l["id"]], "readings": readings_for_leaf[l["id"]][:3],
            "file": record_file(l, data_dir),
        })

    # ---- the branches, with the six things a branch page carries ----
    branches = []
    for b in branch_recs:
        mine = [l for l in leaves if l["branch"] == b["key"]]
        by_stage = {k: sum(1 for l in mine if l["stage"] == k) for k in compute.STAGES}
        furthest = max((l["stage"] for l in mine), key=compute.STAGE_RANK.get, default=None)
        hb = headline_branch.get(b["key"])
        branches.append({
            "key": b["key"], "order": b["order"], "name": b["name"], "meaning": text(b["meaning"]),
            "hallmarks": [{"key": k, "words": HALLMARK_WORDS.get(k, k)} for k in b.get("hallmarks", [])],
            "required": b["required"], "handled_when": b["handled_when"],
            "what_would_move_this": text(b.get("what_would_move_this")), "notes": text(b.get("notes")),
            "leaves": len(mine), "leaves_tracked": sum(1 for l in mine if l.get("status") == "tracked"),
            "counts_by_stage": by_stage, "in_clinic": sum(1 for l in mine if compute.STAGE_RANK[l["stage"]] >= compute.STAGE_RANK["in-clinical-use"]),
            "furthest_stage": furthest, "furthest_label": STAGE_LABELS[furthest] if furthest else None,
            "furthest_rank": compute.STAGE_RANK[furthest] if furthest else None,
            "median_handled_year": hb.get("median_handled_year") if hb else None,
            "leaf_refs": [leaf_ref(l["id"]) for l in mine],
            "claims": claims_for_branch[b["key"]], "experiments": experiments_for_branch[b["key"]],
            "publications": pubs_for_branch[b["key"]],
            "path": branch_path[b["key"]],
        })

    # ---- the claims log ----
    claims = []
    for c in claims_sorted:
        ls, bs = targets(c)
        claims.append({
            "id": c["id"], "who": c["who"], "who_is": text(c["who_is"]), "said_on": c["said_on"],
            "where": text(c["where"]), "link": c.get("link"), "quote": text(c["quote"]),
            "is_paraphrase": c.get("is_paraphrase") is True, "paraphrase_seen_in": text(c.get("paraphrase_seen_in")),
            "commits_to": text(c["commits_to"]), "due": c.get("due"),
            "verdict": c["verdict"], "verdict_label": VERDICT_WORDS[c["verdict"]],
            "verdict_on": iso(c.get("verdict_on")), "verdict_why": text(c.get("verdict_why")),
            "about_the_headline": c.get("about_the_headline") is True,
            "leaves": [leaf_ref(lid) for lid in ls], "branches": [branch_ref(bk) for bk in bs],
            "verify": list(c.get("verify") or []), "notes": text(c.get("notes")),
            "readings": readings_for["claim"][c["id"]][:3],
            "example": c.get("example") is True, "file": record_file(c, data_dir), "path": f"/claims/#{c['id']}",
        })
    claim_years = [c["said_on"][:4] for c in claims]
    claims_counts = {
        "claims": len(claims), "speakers": len({c["who"] for c in claims}),
        "by_verdict": {k: sum(1 for c in claims if c["verdict"] == k) for k in VERDICT_WORDS},
        "about_the_headline": sum(1 for c in claims if c["about_the_headline"]),
        "coverage_only": sum(1 for c in claims if c["is_paraphrase"]),
        "to_verify": sum(len(c["verify"]) for c in claims),
        "first_year": min(claim_years) if claim_years else None, "last_year": max(claim_years) if claim_years else None,
    }

    # ---- the self-experiments ----
    experiments = []
    for e in experiments_sorted:
        ls, bs = targets(e)
        experiments.append({
            "id": e["id"], "who": e["who"], "who_is": text(e["who_is"]), "name": e.get("name", ""),
            "started": e["started"], "status": e["status"], "ended": e.get("ended"),
            "what": text(e["what"]), "measures": text(e["measures"]), "claims": text(e["claims"]),
            "public_record": text(e["public_record"]), "link": e["link"],
            "leaves": [leaf_ref(lid) for lid in ls], "branches": [branch_ref(bk) for bk in bs],
            "verify": list(e.get("verify") or []), "notes": text(e.get("notes")),
            "readings": readings_for["experiment"][e["id"]][:3],
            "example": e.get("example") is True, "file": record_file(e, data_dir), "path": f"/self-experiments/#{e['id']}",
        })

    # ---- the publications log ----
    publications = []
    for p in pubs_sorted:
        ls, bs = targets(p)
        # Whether a paper settled a stage is the paper's own settled_stage flag and nothing else. A
        # leaf can keep a paper as its stage record as written without the paper having settled the
        # rung (Waziry 2023, ruled 2026-10-17), so the leaves' stage records are not read for it.
        kind = ("stage-settled" if p["settled_stage"]
                else ("moved-range" if (p["moved_range"] or pubs_moved[p["id"]]) else "held"))
        publications.append({
            "id": p["id"], "title": p["title"], "date": p["date"], "added_on": iso(p["added_on"]),
            "authors": p["authors"], "authors_short": authors_short(p["authors"]), "venue": text(p["venue"]),
            "link": p["link"], "finding": text(p["finding"]),
            "moved_range": p["moved_range"], "settled_stage": p["settled_stage"],
            "kind": kind, "kind_label": STORY_KINDS[kind],
            "settles": pubs_settle[p["id"]], "moved": pubs_moved[p["id"]],
            "leaves": [leaf_ref(lid) for lid in ls], "branches": [branch_ref(bk) for bk in bs],
            "verify": list(p.get("verify") or []), "notes": text(p.get("notes")),
            "example": p.get("example") is True, "file": record_file(p, data_dir), "path": f"/story/#{p['id']}",
        })

    # ---- the story so far: dated entries, newest day first, with totals per kind ----
    story_entries = [{"kind": p["kind"], "kind_label": p["kind_label"], "date": p["added_on"], "world_date": p["date"],
                      "publication": p["id"]} for p in publications]
    for l in leaves_out:
        for rv in l["revisions"]:
            story_entries.append({"kind": "revision", "kind_label": STORY_KINDS["revision"], "date": rv["date"], "world_date": None,
                                  "leaf": leaf_ref(l["id"]), "revision": rv})
    for rd in readings_out:
        for m in rd["moved"]:
            story_entries.append({"kind": "reading", "kind_label": STORY_KINDS["reading"], "date": rd["read_on"], "world_date": None,
                                  "leaf": m, "reading": rd["id"]})
    # A revision the reading made is already in the leaf's revision log above, so it is not doubled here.
    story_entries.sort(key=lambda e: (e["date"] or "", e.get("publication") or ""), reverse=True)
    story = {
        "entries": story_entries,
        "totals": {k: sum(1 for e in story_entries if e["kind"] == k) for k in STORY_KINDS},
        "days": sorted({e["date"] for e in story_entries if e["date"]}, reverse=True),
        "changelog": read_changelog(changelog_file),
    }

    examples = [{"kind": r["_kind"], "id": r.get("id") or r.get("key")} for r in records if r.get("example") is True]

    # ---- the headline: the whole computed file, or the reason it is not computed, in words ----
    if h is None:
        short = compute.branches_short(loaded)
        if short:
            n = len(tracked)
            reason = (f"The year is not computed yet: {n} of the treatments and tools the tree needs "
                      f"{'is' if n == 1 else 'are'} written up so far, and the calculation needs every branch "
                      f"to have at least {min(b['handled_when'] for b in branch_recs) if branch_recs else 2}.")
        else:
            reason = "The year is not computed yet: the leaves are in place and the calculation is being written."
        headline = {"available": False, "reason": reason}
    else:
        headline = {"available": True, **h, "file": str(headline_file.relative_to(ROOT) if headline_file and headline_file.is_relative_to(ROOT) else headline_file),
                    "worked_run": worked_run(branch_recs, leaves, h)}

    counts = {
        "branches": len(branches), "branches_expected": len(compute.BRANCHES),
        "leaves": len(leaves), "leaves_tracked": len(tracked),
        "leaves_by_stage": {k: sum(1 for l in leaves if l["stage"] == k) for k in compute.STAGES},
        "leaves_in_clinic": sum(1 for l in leaves if compute.STAGE_RANK[l["stage"]] >= compute.STAGE_RANK["in-clinical-use"]),
        "leaves_first_pass": sum(1 for l in leaves if (l.get("estimate") or {}).get("status") == "first-pass"),
        "long_shots": sum(1 for l in leaves if l.get("long_shot") is True),
        "siblings": sum(1 for l in leaves if l.get("sibling")),
        "claims": len(claims), "experiments": len(experiments), "publications": len(publications),
        "scans": len(by_kind["scan"]), "scans_real": len(real_scans),
        "waiting": len(waiting),
        "retired": len(loaded["retired"]),
        "verify": sum(len(r.get("verify") or []) for r in records),
        "examples": len(examples),
    }

    return {
        "exported_on": dt.datetime.now(TZ).date().isoformat(),
        "commit": short_commit(),
        "counts": counts,
        "headline": headline,
        "fixed_dates": {"before": compute.BEFORE_YEAR, "century_end": compute.CENTURY_END},
        "reading": reading,
        "readings": readings_out,
        "waiting": waiting,
        "reading_verdicts": [{"key": k, "label": v[0], "meaning": v[1]} for k, v in READING_VERDICTS.items()],
        "stages": [{"key": k, "label": STAGE_LABELS[k], "meaning": STAGE_MEANINGS[k], "rank": i} for i, k in enumerate(compute.STAGES)],
        "verdicts": [{"key": k, "label": v, "meaning": VERDICT_MEANINGS[k]} for k, v in VERDICT_WORDS.items()],
        "story_kinds": [{"key": k, "label": v} for k, v in STORY_KINDS.items()],
        "branches": branches,
        "leaves": leaves_out,
        "claims": claims,
        "claims_counts": claims_counts,
        "experiments": experiments,
        "publications": publications,
        "story": story,
        "examples": examples,
        "retired": clean(loaded["retired"]),
    }


def authors_short(authors: list[str]) -> str:
    """'Hickson and 32 others', 'Baker and Childs', 'Horvath' for a citation line."""
    surnames = [a.split()[-1] for a in authors if a.strip()]
    if not surnames:
        return ""
    if len(surnames) == 1:
        return surnames[0]
    if len(surnames) == 2:
        return f"{surnames[0]} and {surnames[1]}"
    return f"{surnames[0]} and {len(surnames) - 1} others"


def worked_run(branch_recs: list[dict], leaves: list[dict], h: dict) -> dict:
    """One run written out for the method page, at every leaf's most likely year rather than a
    random draw: for each branch its leaves' years sorted, the handled_when-th taken; the latest
    across the required branches; plus the most likely lag (docs/method.md, 'A worked run')."""
    lag = (h.get("method") or {}).get("lag_years") or {"likely": compute.LAG[1]}
    lag_likely = lag.get("likely", compute.LAG[1])
    rows = []
    latest_required = None
    latest_branch = None
    for b in branch_recs:
        mine = [l for l in leaves if l["branch"] == b["key"] and l.get("status") == "tracked"]
        years = []
        for l in mine:
            if compute.STAGE_RANK[l["stage"]] >= compute.STAGE_RANK["in-clinical-use"]:
                y = compute.clinic_year(l)
                years.append({"id": l["id"], "name": l["name"], "year": y, "known": True})
            else:
                e, lk, lt = compute.clinic_range(l)
                years.append({"id": l["id"], "name": l["name"], "year": lk, "known": False})
        years.sort(key=lambda x: (x["year"] if x["year"] is not None else 9999, x["name"]))
        n = b["handled_when"]
        handled = years[n - 1] if len(years) >= n else None
        row = {"key": b["key"], "name": b["name"], "required": b["required"], "handled_when": n,
               "years": years, "handled_year": handled["year"] if handled else None,
               "handled_by": {"id": handled["id"], "name": handled["name"]} if handled else None}
        rows.append(row)
        if b["required"] and handled and handled["year"] is not None:
            if latest_required is None or handled["year"] > latest_required:
                latest_required = handled["year"]
                latest_branch = b["name"]
    return {"rows": rows, "latest_handled_year": latest_required, "latest_branch": latest_branch,
            "lag": lag_likely, "escape_year": (latest_required + lag_likely) if latest_required is not None else None,
            "note": "Every treatment and tool is taken at its most likely year (or the year it reached the clinic, where it already has), and the lag at its most likely value, so this is one readable run and not a random draw."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the site's JSON from the records in data/.")
    parser.add_argument("--data", default=str(ROOT / "data"))
    parser.add_argument("--out", default=str(ROOT / "site" / "src" / "data"))
    parser.add_argument("--headline", default=None, help="the headline JSON (default: DATA/headline.json)")
    parser.add_argument("--changelog", default=str(ROOT / "CHANGELOG.md"), help="the changelog to read for the story page")
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
    changelog_file = Path(args.changelog).resolve() if args.changelog else None
    export = build_export(loaded, headline_file, changelog_file, data_dir)
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
