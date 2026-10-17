#!/usr/bin/env python3
"""Outrunning Ageing: publish the site with one command.

Plain Python, standard library only. Run from anywhere:

    python3 scripts/publish.py                 validate, test, export and build, then stop and show what changed
    python3 scripts/publish.py --push          the same, then commit everything and push main
    python3 scripts/publish.py --push --message "2026-10-24: ..."   with your own commit message
    python3 scripts/publish.py --push --fallback-branch claude/reading-2026-10-24
                                               if the push to main is refused, push the same commit
                                               once to that branch instead (the weekly reading's
                                               way home from a cloud session; docs/weekly-reading.md)

What it does, in order, stopping at the first thing that fails:

1. Checks every record against the record layout (compute.py validate) and runs the validator's tests.
2. Writes the site's data (export.py), which reads data/headline.json as it stands; the headline
   is recomputed by `compute.py run` only when a leaf changed, as the weekly reading's procedure says.
3. Builds the site (astro build in site/), installing its packages first if they are missing.
4. Shows what changed (git status).
5. Only with --push: fetches GitHub and stops, with nothing committed, if main here is behind
   origin/main; otherwise stages everything, commits with a dated message (or --message), and
   pushes main. The GitHub Action (.github/workflows/deploy.yml) then builds and deploys the
   site from that push. This script never deploys by any other road; `npm run deploy` in site/
   stays for a deploy by hand from a machine with wrangler logged in.

Adapted 2026-10-17 from The Quiet Galaxy's scripts/publish.py (itself from The Belt Equation's
publish script of 2026-09-25 with the behind-origin check of 2026-10-12), with the test step this
repository already runs in its deploy workflow. The fallback branch is the siblings' arrangement for
a reading that runs where a push to main is refused: the commit is parked once on a branch and the
report says so, and the site does not change until John merges it.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
TZ = "America/Los_Angeles"


def run(cmd: list[str], cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    env = dict(os.environ, TZ=TZ)
    print(f"$ {' '.join(cmd)}  (in {cwd.relative_to(ROOT) if cwd != ROOT else '.'})")
    return subprocess.run(cmd, cwd=cwd, env=env, check=check)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate, test, export, build, and optionally commit and push.")
    parser.add_argument("--push", action="store_true", help="commit everything and push main after building")
    parser.add_argument("--message", help="the commit message (default: a dated 'site regenerated' line)")
    parser.add_argument("--fallback-branch", default=None,
                        help="if the push to main is refused, push the same commit once to this branch and say so")
    args = parser.parse_args(argv)

    try:
        run([sys.executable, str(ROOT / "scripts" / "compute.py"), "validate"])
        run([sys.executable, str(ROOT / "scripts" / "test_compute.py")])
        run([sys.executable, str(ROOT / "scripts" / "export.py")])
        if not (SITE / "node_modules").exists():
            run(["npm", "ci"], cwd=SITE)
        run(["npm", "run", "build"], cwd=SITE)
    except subprocess.CalledProcessError as e:
        print(f"Stopped: a step failed (exit {e.returncode}). Nothing committed.", file=sys.stderr)
        return e.returncode or 1

    run(["git", "status", "--short"], check=False)
    if not args.push:
        print("Built. Nothing committed; run again with --push to commit and push main.")
        return 0

    branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True, check=True).stdout.strip()
    if branch != "main":
        print(f"Stopped: the checkout is on {branch!r}, not main. The reading commits on main "
              "(docs/weekly-reading.md, step 0); nothing committed.", file=sys.stderr)
        return 1
    run(["git", "fetch", "origin", "main"])
    behind = subprocess.run(["git", "rev-list", "--count", "HEAD..origin/main"], cwd=ROOT,
                            capture_output=True, text=True, check=True).stdout.strip()
    if behind not in ("", "0"):
        print(f"Stopped: main here is {behind} commit(s) behind origin/main; pull first. Nothing committed.",
              file=sys.stderr)
        return 1
    if not subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip():
        print("Nothing to commit; main is already as built.")
        return 0
    today = dt.datetime.now(ZoneInfo(TZ)).date().isoformat()
    message = args.message or f"{today}: site regenerated"
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", message])
    pushed = run(["git", "push", "origin", "main"], check=False)
    if pushed.returncode == 0:
        print("Pushed. The deploy workflow builds and publishes the site from this push.")
        return 0
    if not args.fallback_branch:
        print("The push to main was refused. Nothing else was tried; the commit is on main here.", file=sys.stderr)
        return pushed.returncode or 1
    # A cloud session's push to main can be refused (no permission, or main moved while the
    # reading ran). Park the same commit on a branch once, so the work is not lost and John can
    # merge it with one click; the site does not change until he does.
    print(f"The push to main was refused; pushing the same commit once to {args.fallback_branch}.", file=sys.stderr)
    fallback = run(["git", "push", "origin", f"HEAD:refs/heads/{args.fallback_branch}"], check=False)
    if fallback.returncode != 0:
        print("That push was refused too. Stop here and put the record's contents in the report.", file=sys.stderr)
        return fallback.returncode or 1
    print(f"Parked on {args.fallback_branch}. The site does not update until it is merged into main.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
