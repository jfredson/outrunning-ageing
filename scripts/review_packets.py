#!/usr/bin/env python3
"""Build the packets for the outside-model review of the 44 ranges (docs/reviews/protocol.md).

A packet is one file under docs/reviews/packets/ that a reviewer model reads in one call: the
brief (docs/reviews/brief.md) followed by the eight branches in brief, then every leaf record in
the packet rendered as plain text (its test, stage and stage record, the estimate with its reason,
the notes and revisions, the claims that point at it, and the publications logged against it), then
the part of docs/method.md that says what a draw is and what the lag does. Packets are generated
from the records, never hand-written, so a packet is always the record as of its date.

    python3 scripts/review_packets.py                    write the four packets dated today
    python3 scripts/review_packets.py --date 2026-10-17  date them otherwise
    python3 scripts/review_packets.py --list             print the packets and their branches

Standard library only. Written 2026-10-17 for the first review, after The Quiet Galaxy's
scripts/review_packets.py of the same date.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
import tomllib
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REVIEWS = ROOT / "docs" / "reviews"

# The four packets, two branches each, in the branches' own order. Protocol decision 3.
PACKETS: dict[str, tuple[str, list[str]]] = {
    "cells-and-settings": ("The two branches about the cell itself: worn-out cells, and the cell's settings",
                           ["worn-out-cells", "cell-settings"]),
    "dna-and-proteins": ("The two branches about the molecules: damaged DNA, and broken proteins and waste",
                         ["damaged-dna", "broken-proteins"]),
    "fuel-and-parts": ("The two branches with the most leaves: energy and fuel sensing, and replacing lost cells and parts",
                       ["energy-and-fuel", "replacing-parts"]),
    "signals-and-measuring": ("The two branches about the whole body: inflammation and the body's messaging, and measuring ageing",
                              ["inflammation-and-signalling", "measuring-age"]),
}

STAGE_WORDS = {
    "idea-only": "idea only (nothing shown yet)",
    "shown-in-animals": "shown in animals",
    "first-human": "first human (a result in at least one person)",
    "in-clinical-use": "in clinical use (approved, or routine in a named setting)",
    "in-wide-use": "in wide use",
}


def load(folder: str) -> list[dict]:
    out = []
    for path in sorted((DATA / folder).glob("*.toml")):
        with path.open("rb") as f:
            out.append(tomllib.load(f))
    return out


def load_branches() -> list[dict]:
    with (DATA / "branches.toml").open("rb") as f:
        return sorted(tomllib.load(f)["branch"], key=lambda b: b["order"])


def render_branches(branches: list[dict], leaves: list[dict]) -> str:
    parts = ["# The eight branches", "",
             "Every branch is marked required, and a branch counts as handled in the year its second "
             "treatment reaches clinical use (`handled_when = 2`). The run's escape year is the latest "
             "handled year across all eight, plus the drawn lag. The treatments per branch are counted below; "
             "the ones in this packet are given in full further down.", ""]
    for b in branches:
        mine = [l for l in leaves if l["branch"] == b["key"] and l.get("status") == "tracked"]
        in_clinic = sum(1 for l in mine if l["stage"] in ("in-clinical-use", "in-wide-use"))
        parts.append(f"- **{b['name']}** (`{b['key']}`): {b['meaning'].strip()} "
                     f"Treatments tracked: {len(mine)}, of which {in_clinic} already in clinical use. "
                     f"What would move this branch: {b['what_would_move_this'].strip()}")
    return "\n".join(parts)


def render_leaf(n: int, total: int, leaf: dict, papers: list[dict], claims: list[dict], experiments: list[dict]) -> str:
    parts = [f"## Treatment {n} of {total} in this packet: {leaf['name']}",
             f"Record id: `{leaf['id']}`. Branch: `{leaf['branch']}`. Horizon the record gives: {leaf['horizon']}."
             + (" **Marked a long shot.**" if leaf.get("long_shot") else ""),
             "", "### What it is", leaf["description"].strip(),
             "", "### What would count (the test)", leaf["test"].strip(),
             f"\nWho or what settles it: {leaf['settler'].strip()}", ""]
    stage = leaf["stage"]
    line = f"### The stage now: {STAGE_WORDS.get(stage, stage)}"
    parts.append(line)
    if stage != "idea-only":
        parts.append(f"Reached {leaf.get('stage_reached_on', '?')}. Record that settles it: {leaf.get('stage_record', '?')}")
    for e in leaf.get("earlier_stage") or []:
        parts.append(f"Earlier rung, {STAGE_WORDS.get(e['stage'], e['stage'])}: reached {e['reached_on']}, record {e['record']}")
    if leaf.get("long_shot"):
        parts += ["", f"Mechanism the record gives: {leaf['mechanism'].strip()}",
                  f"Breaking point the record gives: {leaf['breaking_point'].strip()}"]
    parts.append("")
    est = leaf.get("estimate")
    if est:
        parts.append("### The estimate the site uses now (first pass)")
        parts.append(f"Set on {est['set_on'].isoformat()}. Status: {est['status']}.")
        parts.append("")
        parts.append("| rung | earliest | likely | latest |")
        parts.append("|---|---|---|---|")
        for r in est.get("rung") or []:
            flag = " **(the rung the headline draws from)**" if r["rung"] == "in-clinical-use" else ""
            parts.append(f"| {STAGE_WORDS.get(r['rung'], r['rung'])}{flag} | {r['earliest']} | {r['likely']} | {r['latest']} |")
        parts.append("")
        parts.append("The reason the record gives:")
        parts.append("")
        parts.append(est["why"].strip())
        parts.append("")
    else:
        parts.append("### No estimate: the treatment is already in clinical use, so its year is known and not drawn.")
        parts.append("")
    if leaf.get("notes"):
        parts += ["### The record's notes", leaf["notes"].strip(), ""]
    revs = leaf.get("revision") or []
    if revs:
        parts.append("### Revisions since the record was written")
        for r in revs:
            parts.append(f"- {r['date'].isoformat()}, {r['field']}: {str(r['why']).strip()}")
        parts.append("")
    verify = list(leaf.get("verify") or [])
    if verify:
        parts.append("### Claims still to be checked against a source")
        for v in verify:
            parts.append(f"- {v.strip()}")
        parts.append("")
    if papers:
        parts.append("### Publications the site has logged against this treatment")
        parts.append("Newest first. Each says whether it moved an estimate or settled a stage.")
        for p in papers:
            authors = p["authors"]
            who = ", ".join(authors[:3]) + (" and others" if len(authors) > 3 else "")
            tags = []
            if p.get("settled_stage"):
                tags.append("settled a stage")
            if p.get("moved_range"):
                tags.append("moved an estimate")
            tag = f" [{'; '.join(tags)}]" if tags else ""
            parts.append(f"- **{who} ({p['date']}), \"{p['title']}\", {p['venue']}.**{tag} {p['finding'].strip()} Link: {p['link']}")
        parts.append("")
    if claims:
        parts.append("### Public promises the site's claims log files against this treatment")
        parts.append("Talk, set against delivery; a promise moves no number.")
        for c in claims:
            parts.append(f"- {c['who']} ({c['said_on']}): \"{c['quote'].strip()}\" Verdict so far: {c.get('verdict', '?')}.")
        parts.append("")
    if experiments:
        parts.append("### Public self-experiments the site files against this treatment")
        for x in experiments:
            parts.append(f"- {x['who']}: {x['what'].strip()[:300]}")
        parts.append("")
    return "\n".join(parts)


def method_extract() -> str:
    """The part of docs/method.md that says what the computation does and gives the parameters."""
    text = (ROOT / "docs" / "method.md").read_text()
    start = text.index("## What the computation does")
    end = text.index("## What the headline file holds")
    return text[start:end].strip()


def build(name: str, date: str, branches: list[dict], leaves: list[dict], papers: list[dict],
          claims: list[dict], experiments: list[dict]) -> str:
    title, keys = PACKETS[name]
    brief = (REVIEWS / "brief.md").read_text()
    brief_body = brief.split("---", 1)[1].strip()
    mine = [l for l in leaves if l["branch"] in keys and l.get("status") == "tracked"]
    mine.sort(key=lambda l: (keys.index(l["branch"]), l["id"]))
    names = {b["key"]: b["name"] for b in branches}
    out = [f"# Review packet: {name} ({date})", "",
           f"{title}. Generated by `scripts/review_packets.py` from the records as committed on {date}; "
           "the brief (`docs/reviews/brief.md`) comes first, then the eight branches in brief, then the "
           f"{len(mine)} treatment records in this packet, then the method extract.", "",
           brief_body, "", "---", "", render_branches(branches, leaves), "", "---", "",
           f"# The treatments in this packet: {' and '.join(names[k] for k in keys)}", ""]
    for i, leaf in enumerate(mine, 1):
        lid = leaf["id"]
        ps = sorted((p for p in papers if lid in (p.get("leaves") or [])), key=lambda p: p["date"], reverse=True)
        cs = [c for c in claims if lid in (c.get("leaves") or [])]
        xs = [x for x in experiments if lid in (x.get("leaves") or [])]
        out.append(render_leaf(i, len(mine), leaf, ps, cs, xs))
        out.append("---")
        out.append("")
    out += ["# From the method document: what the computation does and the parameters", "", method_extract(), ""]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default=dt.datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat())
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    leaves = load("leaves")
    if args.list:
        for name, (title, keys) in PACKETS.items():
            n = sum(1 for l in leaves if l["branch"] in keys and l.get("status") == "tracked")
            print(f"{name}: {', '.join(keys)} ({n} treatments)")
        return 0
    branches = load_branches()
    papers = load("papers")
    claims = load("claims")
    experiments = load("experiments")
    (REVIEWS / "packets").mkdir(parents=True, exist_ok=True)
    for name in PACKETS:
        path = REVIEWS / "packets" / f"{args.date}-{name}.md"
        text = build(name, args.date, branches, leaves, papers, claims, experiments)
        path.write_text(text)
        print(f"wrote {path.relative_to(ROOT)} ({len(text.split()):,} words)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
