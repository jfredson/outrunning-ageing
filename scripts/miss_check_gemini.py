#!/usr/bin/env python3
"""Ask a non-Claude model what the weekly readings missed, and file its answer.

    python3 scripts/miss_check_gemini.py --from 2026-10-12 --to 2026-11-09
    python3 scripts/miss_check_gemini.py --from 2026-10-12 --to 2026-11-09 --dry-run

Why. The weekly reading (docs/weekly-reading.md) is run by Claude models. The trial of 2026-11-09
(docs/readings/fable-trial-2026-11-09.md) showed that every Claude reader, on two models and two
designs, can miss the same story. Once a month a model from another lab is asked the same question
from scratch, so the readers are not the only check on themselves. Agreed by John on 2026-11-09.

What it does. It sends Gemini the names of the branches and the treatments, and nothing the readings
found, so its list is its own. It asks for the most important news in the window, each with a date,
a source address and the treatment it bears on, with Google Search lookup on. It files the answer
verbatim at docs/readings/miss-checks/<to>-<model>.md, followed by a list this script builds from
the records themselves: every item the readings in the window marked noted, moved or flagged, and
every publication logged in the window. Comparing the two lists, and opening every source Gemini
names, is the next reader's work: Gemini's list is a model's account, not a record, and nothing in
it is written into a record or a post until its source has been opened.

Cost. One call a month. Paid to Google out of pocket, so each run needs John's go first and is
written into the spending record. With --dry-run nothing is sent and nothing is spent: the prompt
and the records' own list are printed.

Reads the key from GEMINI_API_KEY in the environment and never prints or writes it. Standard
library only. Uses the streaming call in scripts/review_gemini.py.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import tomllib
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_gemini import call  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "docs" / "readings" / "miss-checks"


def load(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def field_outline() -> str:
    """The branches and the treatments by name, with each treatment's test. No stage, no estimate
    and nothing a reading found: the reviewer is told what the site follows, not what it knows."""
    branches = load(DATA / "branches.toml")
    names = {}
    for b in branches.get("branch", []):
        names[b.get("key")] = b.get("name", b.get("key"))
    by_branch: dict[str, list[str]] = {}
    for p in sorted((DATA / "leaves").glob("*.toml")):
        leaf = load(p)
        test = " ".join(str(leaf.get("test", "")).split())
        by_branch.setdefault(leaf.get("branch", "?"), []).append(f"- {leaf.get('name', p.stem)}. What would count: {test}")
    lines = []
    for bid, items in by_branch.items():
        lines.append(f"\n{names.get(bid, bid)}")
        lines.extend(items)
    return "\n".join(lines)


def build_prompt(start: str, end: str) -> str:
    return f"""You are checking a public tracker of treatments against ageing for news it may have missed.

The tracker follows the treatments listed below, grouped by the kind of damage they address. For each
one it records the evidence so far and an estimate of when it reaches the clinic.

Your task: list the most important things that happened between {start} and {end} (both dates
included) that bear on any of these treatments, or on the field of treating ageing as a whole. Use
web search. Look in particular for what a reader searching by treatment name tends to miss:

- trial results announced by companies in press releases or filings, especially results that failed
- trials stopped, paused, withdrawn or put on a safety hold
- decisions by regulators in any country, including conditional approvals and refusals
- new trials registered, and results posted on a trial registry
- peer-reviewed papers and preprints reporting a result in people or in animals
- companies dropping a programme, closing, merging or raising large funding
- stories about treating ageing that match none of the treatments listed

For each item give, on separate lines:
1. The date it happened or was published, as year-month-day. Leave out anything you cannot date inside the window.
2. What happened, in two plain sentences, with the numbers that matter.
3. The address of the best source you found: the release, the filing, the registry entry or the paper.
4. Which listed treatment it bears on, by its name as written below, or "no listed treatment".
5. How sure you are that the item is real and correctly dated: sure, fairly sure, or unsure.

List as many items as you find that meet the test; do not stop at a round number. Put the most
important first. Do not include anything dated outside the window, and do not pad the list. If you
could not check something, say so in the item. End with one paragraph on what you could not search.

The treatments the tracker follows:
{field_outline()}
"""


def records_list(start: str, end: str) -> str:
    """What the readings in the window themselves found, from the records."""
    lines = ["## What the readings in the window found (built from the records by the script)", ""]
    any_item = False
    for p in sorted((DATA / "scans").glob("*.toml")):
        scan = load(p)
        read_on = str(scan.get("read_on", p.stem))[:10]
        if not (start <= read_on <= end):
            continue
        items = [i for i in scan.get("item", []) if i.get("verdict") in ("noted", "moved", "flagged")]
        lines.append(f"### Reading of {read_on}: {len(scan.get('item', []))} records read, {len(items)} not quiet")
        for i in items:
            any_item = True
            what = i.get("leaf") or i.get("claim") or i.get("experiment") or "?"
            found = " ".join(str(i.get("found", "")).split())
            lines.append(f"- {i['verdict']}: `{what}`. {found}")
            for s in i.get("sources", []) or []:
                lines.append(f"  - {s}")
        lines.append("")
    lines.append("### Publications logged in the window")
    for p in sorted((DATA / "papers").glob("*.toml")):
        paper = load(p)
        added = str(paper.get("added_on", ""))[:10]
        if start <= added <= end:
            any_item = True
            lines.append(f"- logged {added}, dated {paper.get('date', '?')}: {paper.get('title', p.stem)} ({paper.get('link', 'no link')})")
    if not any_item:
        lines.append("- nothing")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="start", required=True, help="first day of the window, YYYY-MM-DD")
    ap.add_argument("--to", dest="end", required=True, help="last day of the window, YYYY-MM-DD")
    ap.add_argument("--model", default="gemini-3.1-pro-preview")
    ap.add_argument("--raw", type=Path, default=Path(os.environ.get("REVIEW_RAW_DIR", ".")))
    ap.add_argument("--dry-run", action="store_true", help="print the prompt and the records' list; send nothing")
    args = ap.parse_args()
    for d in (args.start, args.end):
        dt.date.fromisoformat(d)
    if args.start > args.end:
        raise SystemExit("stopped: --from is after --to")

    prompt = build_prompt(args.start, args.end)
    ours = records_list(args.start, args.end)
    if args.dry_run:
        print(prompt)
        print("=" * 70)
        print(ours)
        print(f"dry run: nothing sent. The prompt is {len(prompt)} characters.")
        return 0

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("stopped: GEMINI_API_KEY is not set in this shell")
    model_slug = args.model.replace(".", "-")
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{args.end}-{model_slug}.md"
    if out.exists():
        raise SystemExit(f"stopped: {out.relative_to(ROOT)} is already filed and is never edited")
    args.raw.mkdir(parents=True, exist_ok=True)
    partial = args.raw / f"miss-check-{args.end}-{model_slug}.partial.txt"
    started = time.time()
    reply = call(args.model, prompt, key, True, True, partial)
    took = time.time() - started
    raw_path = args.raw / f"miss-check-{args.end}-{model_slug}.json"
    raw_path.write_text(json.dumps(reply, indent=1))

    cand = (reply.get("candidates") or [{}])[0]
    text = "\n".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []) if not p.get("thought"))
    if not text.strip():
        raise SystemExit(f"stopped: no answer in the reply (saved at {raw_path}); feedback: {reply.get('promptFeedback')}")
    queries = (cand.get("groundingMetadata") or {}).get("webSearchQueries") or []
    usage = reply.get("usageMetadata") or {}
    today = dt.datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
    header = (
        f"# Check for missed stories, {args.start} to {args.end}: {args.model}\n\n"
        f"Model: `{args.model}`, version string reported by the API `{reply.get('modelVersion') or args.model}`. "
        f"Run on {today} by `scripts/miss_check_gemini.py`, with Google Search lookup on "
        f"({len(queries)} searches made). The model was shown the names and tests of the treatments and "
        f"nothing the readings found. Finish reason: {cand.get('finishReason')}. Tokens: "
        f"{usage.get('promptTokenCount', '?')} in, {usage.get('candidatesTokenCount', '?')} out, "
        f"{usage.get('thoughtsTokenCount', 0)} thinking; {took:.0f} seconds. Filed verbatim and never edited.\n\n"
        f"**This is a model's account, not a record.** No item below has been checked. Each one is opened at "
        f"its source before it is written anywhere else, and the comparison with the readings is filed "
        f"beside this file.\n\n"
        + ("Searches the model made: " + "; ".join(queries) + "\n\n" if queries else "")
        + "---\n\n## The outside model's list (verbatim)\n\n"
    )
    out.write_text(header + text.strip() + "\n\n---\n\n" + ours)
    print(f"\nfiled {out.relative_to(ROOT)}: {len(queries)} searches, {usage.get('promptTokenCount', '?')} tokens in, "
          f"{usage.get('candidatesTokenCount', '?')} out, {usage.get('thoughtsTokenCount', 0)} thinking, {took:.0f} s; "
          f"raw reply at {raw_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
