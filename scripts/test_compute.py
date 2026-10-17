#!/usr/bin/env python3
"""Checks that the validator accepts the worked examples and refuses what the schema forbids, and
that the run command refuses until the leaves exist.

Written 2026-10-16 with the validator (weekend step 2 of docs/2026-10-16-kickoff.md). Plain
Python, standard library only, no dependencies:

    python3 scripts/test_compute.py

Each refusal test copies data/ to a temporary folder, breaks one thing in one file by editing
its text (so the test exercises the same TOML the validator reads), and checks that the
validator names the problem. The history check (ids that were committed before and are now
gone) is exercised by passing the set of previously seen ids directly, since a temporary copy
has no git history.
"""

from __future__ import annotations

import io
import re
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import compute  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LEAF = Path("leaves") / "drug-clears-aged-cells-from-a-person.toml"
CLAIM = Path("claims") / "kurzweil-2029-escape-velocity.toml"
EXPERIMENT = Path("experiments") / "bryan-johnson-blueprint.toml"
PAPER = Path("papers") / "hickson-2019.toml"
SCAN = Path("scans") / "2026-10-16.toml"


def problems_for(data_dir: Path, previously_seen=None) -> list[str]:
    loaded = compute.load_records(data_dir)
    return compute.validate(loaded, previously_seen)


class TempData:
    """A throwaway copy of data/ that a test can break."""

    def __enter__(self) -> Path:
        self.tmp = Path(tempfile.mkdtemp(prefix="outrunning-ageing-test-"))
        self.data = self.tmp / "data"
        shutil.copytree(DATA, self.data)
        return self.data

    def __exit__(self, *exc) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


def edit(path: Path, pattern: str, replacement: str, count: int = 1) -> None:
    text = path.read_text(encoding="utf-8")
    new, n = re.subn(pattern, replacement, text, count=count, flags=re.M)
    assert n >= 1, f"pattern {pattern!r} not found in {path.name}"
    path.write_text(new, encoding="utf-8")


def append(path: Path, text: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(text)


def any_with(problems: list[str], *needles: str) -> bool:
    return any(all(n in p for n in needles) for p in problems)


class TheRecords(unittest.TestCase):
    def test_examples_pass(self):
        self.assertEqual(problems_for(DATA), [])

    def test_examples_pass_with_history(self):
        seen = compute.ids_in_history(DATA)
        if seen is None:
            self.skipTest("data/ is not in a git repository here")
        self.assertEqual(problems_for(DATA, seen), [])

    def test_one_of_each_kind_and_all_eight_branches(self):
        loaded = compute.load_records(DATA)
        kinds = {r["_kind"] for r in loaded["records"]}
        self.assertEqual(kinds, compute.RECORD_KINDS)
        branches = sorted(r["key"] for r in loaded["records"] if r["_kind"] == "branch")
        self.assertEqual(branches, sorted(compute.BRANCHES))

    def test_the_twelve_hallmarks_are_each_grouped_once(self):
        loaded = compute.load_records(DATA)
        grouped = [h for r in loaded["records"] if r["_kind"] == "branch" for h in r["hallmarks"]]
        self.assertEqual(sorted(grouped), sorted(compute.HALLMARKS))

    def test_validate_command_exits_zero(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = compute.main(["--data", str(DATA), "validate"])
        self.assertEqual(code, 0)
        self.assertIn("OK", out.getvalue())


class BranchRules(unittest.TestCase):
    def test_a_missing_branch_is_refused(self):
        with TempData() as data:
            path = data / "branches.toml"
            text = path.read_text(encoding="utf-8")
            start = text.index('[[branch]]\nkey = "damaged-dna"')
            end = text.index('[[branch]]\nkey = "cell-settings"')
            path.write_text(text[:start] + text[end:], encoding="utf-8")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "missing the branch", "damaged-dna"), problems)

    def test_a_hallmark_in_two_branches_is_refused(self):
        with TempData() as data:
            edit(data / "branches.toml", r'^hallmarks = \["cellular-senescence"\]', 'hallmarks = ["cellular-senescence", "dysbiosis"]')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'dysbiosis'", "both"), problems)

    def test_an_ungrouped_hallmark_is_refused(self):
        with TempData() as data:
            edit(data / "branches.toml", r'^hallmarks = \["cellular-senescence"\]', 'hallmarks = []')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "cellular-senescence", "belong to no branch"), problems)

    def test_order_must_match_key(self):
        with TempData() as data:
            edit(data / "branches.toml", r'^order = 8$', "order = 7")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "order must be 8", "measuring-age"), problems)

    def test_handled_when_at_least_one(self):
        with TempData() as data:
            edit(data / "branches.toml", r'^handled_when = 2$', "handled_when = 0")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "handled_when must be at least 1"), problems)


class LeafRules(unittest.TestCase):
    def test_leaf_with_no_test_is_refused(self):
        with TempData() as data:
            path = data / LEAF
            text = path.read_text(encoding="utf-8")
            start = text.index('test = """')
            end = text.index('settler = ')
            path.write_text(text[:start] + text[end:], encoding="utf-8")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'test'", "missing"), problems)

    def test_leaf_with_no_settler_is_refused(self):
        with TempData() as data:
            edit(data / LEAF, r'^settler = .*\n', "")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'settler'", "missing"), problems)

    def test_stage_above_idea_only_needs_a_record(self):
        with TempData() as data:
            edit(data / LEAF, r'^stage_record = .*\n', "")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'stage_record'", "public record"), problems)

    def test_unknown_stage_is_refused(self):
        with TempData() as data:
            edit(data / LEAF, r'^stage = "first-human"', 'stage = "phase-3"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "stage must be one of"), problems)

    def test_earlier_stage_must_be_below_current(self):
        with TempData() as data:
            edit(data / LEAF, r'^stage = "shown-in-animals"\nreached_on', 'stage = "in-clinical-use"\nreached_on')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "not below the current stage"), problems)

    def test_earliest_after_likely_is_refused(self):
        with TempData() as data:
            edit(data / LEAF, r'^earliest = 2031$', "earliest = 2040")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "earliest <= likely <= latest"), problems)

    def test_latest_past_2300_is_refused(self):
        with TempData() as data:
            edit(data / LEAF, r'^latest = 2060$', "latest = 2400")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "past 2300"), problems)

    def test_earliest_before_set_on_is_refused(self):
        with TempData() as data:
            edit(data / LEAF, r'^earliest = 2031$', "earliest = 2020")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "before the year the estimate was set"), problems)

    def test_a_leaf_below_the_clinic_needs_the_clinic_rung(self):
        with TempData() as data:
            # Rename the clinic rung to wide use: the clinic rung disappears and wide use is doubled.
            edit(data / LEAF, r'^rung = "in-clinical-use"$', 'rung = "in-wide-use"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "no rung for 'in-clinical-use'"), problems)
        self.assertTrue(any_with(problems, "listed twice"), problems)

    def test_a_leaf_below_the_clinic_needs_an_estimate(self):
        with TempData() as data:
            path = data / LEAF
            text = path.read_text(encoding="utf-8")
            path.write_text(text[: text.index("[estimate]")], encoding="utf-8")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "needs an [estimate]"), problems)

    def test_a_leaf_in_the_clinic_needs_no_estimate(self):
        with TempData() as data:
            path = data / LEAF
            text = path.read_text(encoding="utf-8")
            text = text[: text.index("[estimate]")]
            text = text.replace('stage = "first-human"', 'stage = "in-clinical-use"')
            path.write_text(text, encoding="utf-8")
            problems = problems_for(data)
        self.assertEqual(problems, [])

    def test_a_rung_not_above_the_stage_is_refused(self):
        with TempData() as data:
            edit(data / LEAF, r'^rung = "in-wide-use"$', 'rung = "first-human"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "not above the current stage"), problems)

    def test_horizon_top_only_in_wide_use(self):
        with TempData() as data:
            edit(data / LEAF, r'^horizon = "mid"', 'horizon = "top"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "horizon 'top' is only"), problems)

    def test_a_long_shot_needs_mechanism_and_breaking_point(self):
        with TempData() as data:
            edit(data / LEAF, r'^horizon = "mid"\n', 'horizon = "mid"\nlong_shot = true\n')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'mechanism'"), problems)
        self.assertTrue(any_with(problems, "'breaking_point'"), problems)

    def test_unknown_field_is_refused(self):
        with TempData() as data:
            edit(data / LEAF, r'^settler = ', "setler = ")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "unknown field 'setler'"), problems)
        self.assertTrue(any_with(problems, "'settler'", "missing"), problems)

    def test_a_health_field_cannot_arrive_by_accident(self):
        with TempData() as data:
            edit(data / LEAF, r'^horizon = "mid"\n', 'horizon = "mid"\njohns_dose = "none"\n')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "unknown field 'johns_dose'"), problems)

    def test_world_date_must_be_text(self):
        with TempData() as data:
            edit(data / LEAF, r'^stage_reached_on = "2019-09-18"', "stage_reached_on = 2019-09-18")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'stage_reached_on' must be text"), problems)

    def test_project_date_must_be_a_date(self):
        with TempData() as data:
            edit(data / LEAF, r'^set_on = 2026-10-16', 'set_on = "2026-10-16"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "set_on must be a TOML date"), problems)


class ClaimRules(unittest.TestCase):
    def test_claim_with_no_source_is_refused(self):
        with TempData() as data:
            edit(data / CLAIM, r'^where = .*\n', "")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'where'", "missing"), problems)

    def test_claim_with_nothing_to_bear_on_is_refused(self):
        with TempData() as data:
            edit(data / CLAIM, r'^about_the_headline = true\n', "")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "names no leaf and no branch and is not about the headline"), problems)

    def test_paraphrase_says_where_it_was_seen(self):
        with TempData() as data:
            edit(data / CLAIM, r'^paraphrase_seen_in = .*\n', "")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "paraphrase says where it was seen"), problems)

    def test_not_yet_due_needs_a_due_year(self):
        with TempData() as data:
            edit(data / CLAIM, r'^due = 2029\n', "")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "needs a 'due' year"), problems)

    def test_missed_needs_a_date_and_a_reason(self):
        with TempData() as data:
            edit(data / CLAIM, r'^verdict = "not-yet-due"', 'verdict = "missed"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'missed' verdict needs 'verdict_on'"), problems)
        self.assertTrue(any_with(problems, "'missed' verdict needs 'verdict_why'"), problems)

    def test_unknown_verdict_is_refused(self):
        with TempData() as data:
            edit(data / CLAIM, r'^verdict = "not-yet-due"', 'verdict = "maybe"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "verdict must be one of"), problems)

    def test_dangling_leaf_link_is_refused(self):
        with TempData() as data:
            edit(data / CLAIM, r'^about_the_headline = true', 'leaves = ["no-such-leaf"]')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'no-such-leaf'", "not a leaf that exists"), problems)


class ExperimentRules(unittest.TestCase):
    def test_experiment_cannot_move_a_leaf(self):
        with TempData() as data:
            edit(data / EXPERIMENT, r'^status = "running"\n', 'status = "running"\nstage = "first-human"\n')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "a self-experiment moves no leaf"), problems)
        self.assertFalse(any_with(problems, "unknown field 'stage'"), problems)

    def test_experiment_needs_a_target(self):
        with TempData() as data:
            edit(data / EXPERIMENT, r'^branches = \[.*\]\n', "")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "self-experiment tries at least one"), problems)

    def test_ended_experiment_says_when(self):
        with TempData() as data:
            edit(data / EXPERIMENT, r'^status = "running"', 'status = "ended"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "says when ('ended')"), problems)

    def test_experiment_needs_its_own_publication(self):
        with TempData() as data:
            edit(data / EXPERIMENT, r'^link = .*\n', "")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'link'", "missing"), problems)


class PublicationRules(unittest.TestCase):
    def test_settled_stage_must_be_named_by_a_leaf(self):
        with TempData() as data:
            edit(data / LEAF, r'^stage_publication = "hickson-2019"\n', "")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "settled a stage, but no leaf names 'hickson-2019'"), problems)

    def test_settled_stage_via_an_earlier_stage_passes(self):
        with TempData() as data:
            edit(data / LEAF, r'^stage_publication = "hickson-2019"\n', "")
            edit(data / LEAF, r'^record = "https://doi.org/10.1038/nature10600"\n',
                 'record = "https://doi.org/10.1038/nature10600"\npublication = "hickson-2019"\n')
            problems = problems_for(data)
        self.assertEqual(problems, [])

    def test_moved_range_needs_a_revision(self):
        with TempData() as data:
            edit(data / PAPER, r'^moved_range = false', "moved_range = true")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "no leaf has a revision naming 'hickson-2019'"), problems)

    def test_moved_range_backed_by_a_revision_passes(self):
        with TempData() as data:
            edit(data / PAPER, r'^moved_range = false', "moved_range = true")
            append(data / LEAF, '\n[[revision]]\ndate = 2026-10-16\nfield = "estimate.rung.in-clinical-use.likely"\n'
                                'old = 2040\nnew = 2038\nwhy = "Test revision."\npublication = "hickson-2019"\n')
            problems = problems_for(data)
        self.assertEqual(problems, [])

    def test_publication_needs_a_target(self):
        with TempData() as data:
            edit(data / PAPER, r'^leaves = \[.*\]\n', "")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "publication bears on at least one"), problems)

    def test_dangling_stage_publication_is_refused(self):
        with TempData() as data:
            edit(data / LEAF, r'^stage_publication = "hickson-2019"', 'stage_publication = "nobody-1999"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'nobody-1999'", "not a publication record that exists"), problems)


class ScanRules(unittest.TestCase):
    def test_id_must_equal_read_on(self):
        with TempData() as data:
            edit(data / SCAN, r'^read_on = 2026-10-16', "read_on = 2026-10-17")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "must equal the read_on date"), problems)

    def test_covers_from_not_after_read_on(self):
        with TempData() as data:
            edit(data / SCAN, r'^covers_from = 2026-10-09', "covers_from = 2026-10-20")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "covers_from", "is after read_on"), problems)

    def test_moved_needs_a_revision_on_the_leaf(self):
        with TempData() as data:
            edit(data / SCAN, r'^verdict = "quiet"', 'verdict = "moved"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "has no revision dated 2026-10-16", "the reading proposes and the leaf records"), problems)

    def test_moved_with_a_matching_revision_passes(self):
        with TempData() as data:
            edit(data / SCAN, r'^verdict = "quiet"', 'verdict = "moved"')
            append(data / LEAF, '\n[[revision]]\ndate = 2026-10-16\nfield = "estimate.rung.in-clinical-use.likely"\n'
                                'old = 2040\nnew = 2038\nwhy = "Test revision."\n')
            problems = problems_for(data)
        self.assertEqual(problems, [])

    def test_reading_of_a_missing_leaf_is_refused(self):
        with TempData() as data:
            edit(data / SCAN, r'^leaf = "drug-clears-aged-cells-from-a-person"', 'leaf = "no-such-leaf"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'no-such-leaf'", "not a leaf that exists"), problems)

    def test_a_leaf_read_twice_is_refused(self):
        with TempData() as data:
            append(data / SCAN, '\n[[reading]]\nleaf = "drug-clears-aged-cells-from-a-person"\nverdict = "quiet"\nline = "Again."\n')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "read twice"), problems)

    def test_sibling_stage_only_on_a_shared_leaf(self):
        with TempData() as data:
            edit(data / LEAF, r'^sibling = .*\n', "")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'sibling_stage' is only for a leaf that has a sibling"), problems)

    def test_unknown_reading_verdict_is_refused(self):
        with TempData() as data:
            edit(data / SCAN, r'^verdict = "quiet"', 'verdict = "fine"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "verdict must be one of"), problems)


class RenamedIds(unittest.TestCase):
    def test_file_name_must_equal_id(self):
        with TempData() as data:
            (data / LEAF).rename(data / "leaves" / "senolytics.toml")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "named 'senolytics' but its id is 'drug-clears-aged-cells-from-a-person'"), problems)

    def test_id_gone_from_history_without_retirement_is_refused(self):
        with TempData() as data:
            (data / CLAIM).unlink()
            seen = {("claim", "kurzweil-2029-escape-velocity"), ("leaf", "drug-clears-aged-cells-from-a-person")}
            problems = problems_for(data, seen)
        self.assertTrue(any_with(problems, "'kurzweil-2029-escape-velocity' was committed before and is now gone"), problems)

    def test_retired_id_satisfies_the_history_check(self):
        with TempData() as data:
            (data / CLAIM).unlink()
            (data / "retired.toml").write_text(
                '[[retired]]\nid = "kurzweil-2029-escape-velocity"\nkind = "claim"\ndate = 2026-10-16\n'
                'why = "Test retirement."\n', encoding="utf-8")
            seen = {("claim", "kurzweil-2029-escape-velocity")}
            problems = problems_for(data, seen)
        self.assertEqual(problems, [])

    def test_retired_id_cannot_be_reused(self):
        with TempData() as data:
            (data / "retired.toml").write_text(
                '[[retired]]\nid = "hickson-2019"\nkind = "publication"\ndate = 2026-10-16\n'
                'why = "Test retirement."\n', encoding="utf-8")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "retired but", "never reused"), problems)

    def test_ids_are_unique_across_kinds(self):
        with TempData() as data:
            edit(data / CLAIM, r'^id = "kurzweil-2029-escape-velocity"', 'id = "hickson-2019"')
            (data / CLAIM).rename(data / "claims" / "hickson-2019.toml")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'hickson-2019' is also used by"), problems)


class TheRunStub(unittest.TestCase):
    def test_run_refuses_until_the_leaves_exist(self):
        o, e = io.StringIO(), io.StringIO()
        with redirect_stdout(o), redirect_stderr(e):
            code = compute.main(["--data", str(DATA), "run"])
        self.assertEqual(code, 2)
        self.assertIn("not written yet", o.getvalue())
        self.assertIn("worn-out-cells: 1 of 2", o.getvalue())
        self.assertIn("measuring-age: 0 of 2", o.getvalue())

    def test_run_refuses_invalid_data(self):
        with TempData() as data:
            edit(data / LEAF, r'^settler = .*\n', "")
            o, e = io.StringIO(), io.StringIO()
            with redirect_stdout(o), redirect_stderr(e):
                code = compute.main(["--data", str(data), "run"])
        self.assertEqual(code, 1)
        self.assertIn("Refusing to run", e.getvalue())

    def test_branches_short_counts_tracked_leaves_only(self):
        with TempData() as data:
            edit(data / LEAF, r'^status = "tracked"', 'status = "withdrawn"')
            loaded = compute.load_and_validate(data, history=False)
            short = compute.branches_short(loaded)
        self.assertEqual(short[0], ("worn-out-cells", 0, 2))
        self.assertEqual(len(short), 8)


if __name__ == "__main__":
    unittest.main(verbosity=1)
