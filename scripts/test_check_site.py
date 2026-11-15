#!/usr/bin/env python3
"""Tests for scripts/check_site.py: which sentences the check stops and which it lets through.

    python3 scripts/test_check_site.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_site import PATTERN

STOPPED = [
    "Checked against the published article, which John saved from the publisher's site.",
    "This line was added at John's word of that day.",
    "Read 2026-11-14 from John's photographs of the book's copyright page.",
    "the page had refused a script and the browser pane",
    "which John opened by signing in with his own subscription",
    "the full article, which John downloaded through the library",
    "flagged for John",
    "(John's ruling of the same day)",
]
ALLOWED = [
    "I'm John, and I write about AI, sentience and the spread of conscious life.",
    "Outrunning Ageing, by John Andrew Fredrickson, a Sentient Horizons project",
    "The radio astronomer John Ball proposed the idea in a three-page paper in 1973.",
    "The mathematician John von Neumann had shown in the 1940s that a machine could copy itself.",
    "the catalogue traces it to John Ball's 1973 paper",
    "Read 2026-11-14 from photographs of the book's copyright page.",
    "he gave his own conclusion that space travel would stay within our planetary system",
    "The journal's own page refused an automatic fetch.",
]

failures = [f"should be stopped: {s}" for s in STOPPED if not PATTERN.search(s)]
failures += [f"should be allowed: {s}" for s in ALLOWED if PATTERN.search(s)]
if failures:
    print("\n".join(failures))
    sys.exit(1)
print(f"test_check_site: {len(STOPPED)} stopped, {len(ALLOWED)} allowed, as expected")
