#!/usr/bin/env python3
"""Refuse a built site that carries a note addressed to John.

    python3 scripts/check_site.py            # reads site/dist
    python3 scripts/check_site.py path/to/dist

Added 2026-11-14, decided by John the same day, after a review of the live site found
working notes on public pages: lines in the record or the changelog saying what was
"flagged for John", what was "waiting on me", who ruled, which computer a task ran on and
how a change reached the repository. Those were reworded; this check stops new ones. The
same check has run on The Belt Equation since 2026-10-27. It runs after the build and
before the deploy, so it reads exactly what a visitor would see, whatever file the text
came from.

The phrases are kept narrow on purpose. "For me" alone is not on the list, because I write
in my own voice to the reader ("left for me to decide" reads naturally), and "Waiting on me" is
the reading page's heading for what a reading may not do on its own; the list names the
ways a note to myself has actually been written. A phrase that turns out to be fine in a
visitor's sentence comes off the list with a reason in this comment.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

PHRASES = [
    r"for john\b",             # "flagged for John", "a note for John"
    r"(reported|sent|passed|left|put) to john\b",   # "reported to John" (not "traces it to John Ball")
    r"john'?s ruling",         # "(John's ruling of the same day)"
    r"john to (rewrite|review|approve|check|read|decide)",
    r"flagged (it |the range |)for me",
    r"put to me\b",
    r"\bhis call\b",
    r"\bhe ruled\b",
    r"reads it on return",
    r"\bmy mac\b",
    r"cloud (session|workspace|routine)",
    r"pull request",
    r"\[draft\b",
    r"\bTODO\b",
    r"\bFIXME\b",
]
PATTERN = re.compile("|".join(PHRASES), re.IGNORECASE)
TAGS = re.compile(r"<script\b.*?</script>|<style\b.*?</style>|<[^>]+>", re.IGNORECASE | re.DOTALL)


def visible_text(page: Path) -> str:
    """The words a visitor reads: tags, scripts and styles stripped, entities decoded."""
    raw = page.read_text(encoding="utf-8", errors="replace")
    return re.sub(r"\s+", " ", html.unescape(TAGS.sub(" ", raw)))


def check(dist: Path) -> list[str]:
    problems: list[str] = []
    for page in sorted(dist.rglob("*.html")):
        text = visible_text(page)
        for m in PATTERN.finditer(text):
            start = max(0, m.start() - 60)
            problems.append(f"{page.relative_to(dist)}: …{text[start:m.end() + 60]}…")
    return problems


def main() -> int:
    dist = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "site" / "dist"
    if not dist.is_dir():
        print(f"no built site at {dist}; build it first", file=sys.stderr)
        return 2
    problems = check(dist)
    if problems:
        print("The built site carries text written as a note to John, which must not be public:")
        for p in problems:
            print("  " + p)
        return 1
    print(f"check_site: no note addressed to John in {dist}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
