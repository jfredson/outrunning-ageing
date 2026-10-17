#!/usr/bin/env python3
"""Checks that the validator accepts the worked examples and refuses what the schema forbids, and
that the run command refuses until the leaves exist and otherwise writes a reproducible headline.

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
PARAPHRASE_CLAIM = Path("claims") / "barzilai-2022-tame-starts-this-year.toml"
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
        # The Barzilai record is the log's paraphrase held on coverage (2026-10-16); the Kurzweil
        # worked example stopped being a paraphrase once the book's words were checked.
        with TempData() as data:
            edit(data / PARAPHRASE_CLAIM, r'^paraphrase_seen_in = .*\n', "")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "paraphrase says where it was seen"), problems)

    def test_not_yet_due_needs_a_due_year(self):
        with TempData() as data:
            edit(data / CLAIM, r'^due = 2030\n', "")
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
            edit(data / LEAF, r'^publication = "baker-2011"\n', 'publication = "hickson-2019"\n')
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


# A small weekly reading the tests can break, in the layout of docs/record-schema.md ("The scan
# record", widened 2026-10-17): the header, then one item each for a leaf, a claim and a
# self-experiment. Written into a temporary copy of data/ as scans/2026-10-24.toml.
SCAN = Path("scans") / "2026-10-24.toml"
SCAN_TEXT = '''id = "2026-10-24"
read_on = 2026-10-24
covers_from = 2026-10-18
ran_at = "2026-10-25T02:10:00Z"
run_by = "scheduled"
commit_before = "0123abc"
leaves_read = 1
claims_read = 1
experiments_read = 1
searches = 6
summary = "A test reading."

[[item]]
leaf = "drug-clears-aged-cells-from-a-person"
verdict = "quiet"
queries = ["senolytic trial result 2026-10", "dasatinib quercetin paper 2026-10"]
found = "Nothing in the window."
sibling_stage = "first-human"
sibling_agrees = true

[[item]]
claim = "kurzweil-2029-escape-velocity"
verdict = "quiet"
queries = ["Kurzweil longevity escape velocity 2026-10", "Kurzweil 2030 interview 2026-10"]
found = "Nothing in the window."

[[item]]
experiment = "bryan-johnson-blueprint"
verdict = "quiet"
queries = ["Bryan Johnson Blueprint 2026-10", "Bryan Johnson biological age 2026-10"]
found = "Nothing in the window."
'''
STAGE_REVISION = ('\n[[revision]]\ndate = 2026-10-24\nfield = "stage"\nold = "first-human"\nnew = "in-clinical-use"\n'
                  'why = "[reading 2026-10-24] Test revision."\n')


class ScanRules(unittest.TestCase):
    """The weekly reading's record. Each test writes the fixture above into a temporary copy of
    data/ and breaks one thing in it."""

    def fixture(self, data: Path, text: str = SCAN_TEXT) -> Path:
        path = data / SCAN
        path.write_text(text, encoding="utf-8")
        return path

    def test_the_fixture_passes(self):
        with TempData() as data:
            self.fixture(data)
            self.assertEqual(problems_for(data), [])

    def test_id_must_be_the_read_on_date(self):
        with TempData() as data:
            path = self.fixture(data)
            edit(path, r'^read_on = 2026-10-24', "read_on = 2026-10-25")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "must be the read_on date 2026-10-25"), problems)

    def test_a_second_run_the_same_day_takes_a_suffix(self):
        with TempData() as data:
            path = self.fixture(data)
            edit(path, r'^id = "2026-10-24"', 'id = "2026-10-24-2"')
            path.rename(data / "scans" / "2026-10-24-2.toml")
            self.assertEqual(problems_for(data), [])

    def test_covers_from_not_after_read_on(self):
        with TempData() as data:
            edit(self.fixture(data), r'^covers_from = 2026-10-18', "covers_from = 2026-10-30")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "covers_from", "is after read_on"), problems)

    def test_header_fields_have_the_right_shape(self):
        with TempData() as data:
            path = self.fixture(data)
            edit(path, r'^ran_at = .*', 'ran_at = "2026-10-24 19:10"')
            edit(path, r'^run_by = .*', 'run_by = "robot"')
            edit(path, r'^commit_before = .*', 'commit_before = "main"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "ran_at must be universal time"), problems)
        self.assertTrue(any_with(problems, "run_by must be one of"), problems)
        self.assertTrue(any_with(problems, "commit_before must be the short commit"), problems)

    def test_header_counts_must_match_the_items(self):
        with TempData() as data:
            path = self.fixture(data)
            edit(path, r'^leaves_read = 1', "leaves_read = 2")
            edit(path, r'^searches = 6', "searches = 5")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "leaves_read says 2 but the items name 1 leaf"), problems)
        self.assertTrue(any_with(problems, "searches says 5 but the items list 6"), problems)

    def test_an_item_names_exactly_one_record(self):
        with TempData() as data:
            path = self.fixture(data)
            edit(path, r'^claim = "kurzweil-2029-escape-velocity"', 'claim = "kurzweil-2029-escape-velocity"\nleaf = "drug-clears-aged-cells-from-a-person"')
            edit(path, r'^experiment = "bryan-johnson-blueprint"\n', "")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "item 2", "more than one record"), problems)
        self.assertTrue(any_with(problems, "item 3", "names no record"), problems)

    def test_reading_of_a_missing_record_is_refused(self):
        with TempData() as data:
            edit(self.fixture(data), r'^claim = "kurzweil-2029-escape-velocity"', 'claim = "no-such-claim"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'no-such-claim'", "not a claim that exists"), problems)

    def test_a_record_read_twice_is_refused(self):
        with TempData() as data:
            append(self.fixture(data), '\n[[item]]\nleaf = "drug-clears-aged-cells-from-a-person"\nverdict = "quiet"\n'
                                       'queries = ["a", "b"]\nfound = "Again."\n')
            edit(data / SCAN, r'^leaves_read = 1', "leaves_read = 2")
            edit(data / SCAN, r'^searches = 6', "searches = 8")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "read twice"), problems)

    def test_every_record_gets_two_searches(self):
        with TempData() as data:
            edit(self.fixture(data), r'^queries = \["senolytic trial result 2026-10", "dasatinib quercetin paper 2026-10"\]',
                 'queries = ["senolytic trial result 2026-10"]')
            edit(data / SCAN, r'^searches = 6', "searches = 5")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "lists 1 search(es); every record gets at least two"), problems)

    def test_one_search_passes_when_search_short_says_why(self):
        with TempData() as data:
            edit(self.fixture(data), r'^queries = \["senolytic trial result 2026-10", "dasatinib quercetin paper 2026-10"\]',
                 'queries = ["senolytic trial result 2026-10"]\nsearch_short = "The search tool refused every further search."')
            edit(data / SCAN, r'^searches = 6', "searches = 5")
            self.assertEqual(problems_for(data), [])

    def test_a_reused_line_quotes_one_of_the_queries(self):
        with TempData() as data:
            edit(self.fixture(data), r'^found = "Nothing in the window."\nsibling_stage',
                 'reused = ["the query \\"something else\\" was first run for another leaf"]\nfound = "Nothing in the window."\nsibling_stage')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'reused' line must quote one of the item's own queries"), problems)

    def test_noted_names_a_publication_and_a_source(self):
        with TempData() as data:
            edit(self.fixture(data), r'^verdict = "quiet"', 'verdict = "noted"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'noted' item cites at least one source"), problems)
        self.assertTrue(any_with(problems, "'noted' item names the publication it logged"), problems)

    def test_noted_with_a_source_and_a_publication_passes(self):
        with TempData() as data:
            edit(self.fixture(data), r'^verdict = "quiet"',
                 'verdict = "noted"\nsources = ["https://doi.org/10.1016/j.ebiom.2019.08.069"]\npublications = ["hickson-2019"]')
            self.assertEqual(problems_for(data), [])

    def test_a_publication_that_does_not_exist_is_refused(self):
        with TempData() as data:
            edit(self.fixture(data), r'^verdict = "quiet"',
                 'verdict = "noted"\nsources = ["https://example.org/x"]\npublications = ["nobody-2099"]')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'nobody-2099'", "not a publication record that exists"), problems)

    def test_quiet_logs_nothing(self):
        with TempData() as data:
            edit(self.fixture(data), r'^verdict = "quiet"', 'verdict = "quiet"\npublications = ["hickson-2019"]')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'quiet' item logs no publication"), problems)

    def test_flagged_needs_a_line_for_john_and_only_flagged_has_one(self):
        with TempData() as data:
            path = self.fixture(data)
            edit(path, r'^verdict = "quiet"', 'verdict = "flagged"\nsources = ["https://example.org/x"]')
            edit(path, r'^found = "Nothing in the window."\n\n\[\[item\]\]\nexperiment',
                 'found = "Nothing in the window."\nfor_john = "Your call."\n\n[[item]]\nexperiment')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "item 1", "'flagged' item carries 'for_john'"), problems)
        self.assertTrue(any_with(problems, "item 2", "'for_john' is only for a 'flagged' item"), problems)

    def test_moved_needs_a_stage_revision_on_the_leaf(self):
        with TempData() as data:
            edit(self.fixture(data), r'^verdict = "quiet"',
                 'verdict = "moved"\nmoved_from = "first-human"\nmoved_to = "in-clinical-use"\nsources = ["https://example.org/x"]')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "no stage revision dated 2026-10-24", "the reading proposes and the leaf records"), problems)

    def test_moved_with_a_matching_revision_passes(self):
        with TempData() as data:
            edit(self.fixture(data), r'^verdict = "quiet"',
                 'verdict = "moved"\nmoved_from = "first-human"\nmoved_to = "in-clinical-use"\nsources = ["https://example.org/x"]')
            append(data / LEAF, STAGE_REVISION)
            self.assertEqual(problems_for(data), [])

    def test_a_move_is_exactly_one_rung(self):
        with TempData() as data:
            edit(self.fixture(data), r'^verdict = "quiet"',
                 'verdict = "moved"\nmoved_from = "first-human"\nmoved_to = "in-wide-use"\nsources = ["https://example.org/x"]')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "exactly one rung up"), problems)

    def test_only_a_leaf_can_move(self):
        with TempData() as data:
            path = self.fixture(data)
            text = path.read_text(encoding="utf-8").replace(
                'claim = "kurzweil-2029-escape-velocity"\nverdict = "quiet"',
                'claim = "kurzweil-2029-escape-velocity"\nverdict = "moved"\nmoved_from = "first-human"\nmoved_to = "in-clinical-use"\nsources = ["https://example.org/x"]')
            path.write_text(text, encoding="utf-8")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "only a leaf can be 'moved'"), problems)

    def test_moved_fields_only_on_a_moved_item(self):
        with TempData() as data:
            edit(self.fixture(data), r'^verdict = "quiet"', 'verdict = "quiet"\nmoved_to = "in-clinical-use"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'moved_to' is only for a 'moved' item"), problems)

    def test_sibling_stage_only_on_a_shared_leaf(self):
        with TempData() as data:
            self.fixture(data)
            edit(data / LEAF, r'^sibling = .*\n', "")
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "'sibling_stage' is only for a leaf that has a sibling"), problems)

    def test_unknown_reading_verdict_is_refused(self):
        with TempData() as data:
            edit(self.fixture(data), r'^verdict = "quiet"', 'verdict = "waiting"')
            problems = problems_for(data)
        self.assertTrue(any_with(problems, "verdict must be one of"), problems)

    def test_the_first_reading_is_on_the_record(self):
        loaded = compute.load_records(DATA)
        scans = [r for r in loaded["records"] if r["_kind"] == "scan" and r.get("example") is not True]
        self.assertGreaterEqual(len(scans), 1)
        first = min(scans, key=lambda r: r["read_on"])
        self.assertEqual(first["id"], "2026-10-17")
        self.assertEqual(first["run_by"], "hand")


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
            for scan in (data / "scans").glob("*.toml"):
                scan.unlink()  # the real readings read every claim, so they would name the retired one
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


class TheRun(unittest.TestCase):
    def test_run_refuses_until_every_branch_has_enough_leaves(self):
        with TempData() as data:
            (data / "headline.json").unlink(missing_ok=True)
            # Ask the measuring branch for more leaves than it has: the readiness rule refuses.
            text = (data / "branches.toml").read_text(encoding="utf-8")
            head, tail = text.rsplit("handled_when = 2", 1)
            (data / "branches.toml").write_text(head + "handled_when = 99" + tail, encoding="utf-8")
            o, e = io.StringIO(), io.StringIO()
            with redirect_stdout(o), redirect_stderr(e):
                code = compute.main(["--data", str(data), "run"])
            self.assertFalse((data / "headline.json").exists())
        self.assertEqual(code, 2)
        self.assertIn("not written yet", o.getvalue())
        self.assertIn("measuring-age: 5 of 99", o.getvalue())

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
            text = (data / "branches.toml").read_text(encoding="utf-8")
            head, tail = text.rsplit("handled_when = 2", 1)
            (data / "branches.toml").write_text(head + "handled_when = 6" + tail, encoding="utf-8")
            loaded = compute.load_and_validate(data, history=False)
            short = compute.branches_short(loaded)
        self.assertEqual(short, [("measuring-age", 5, 6)])

    def test_a_withdrawn_leaf_below_the_clinic_does_not_count(self):
        with TempData() as data:
            edit(data / LEAF, r'^status = "tracked"', 'status = "withdrawn"')
            loaded = compute.load_and_validate(data, history=False)
            short = compute.branches_short(loaded)
            leaf = next(r for r in loaded["records"] if r["_kind"] == "leaf" and r["id"] == LEAF.stem)
        self.assertFalse(compute.leaf_counts(leaf))
        self.assertEqual(short, [])  # four other worn-out-cells leaves remain

    def test_run_writes_the_headline_and_reproduces(self):
        with TempData() as data:
            o, e = io.StringIO(), io.StringIO()
            with redirect_stdout(o), redirect_stderr(e):
                code = compute.main(["--data", str(data), "run"])
            self.assertEqual(code, 0, e.getvalue())
            import json
            h = json.loads((data / "headline.json").read_text(encoding="utf-8"))
            again = compute.compute_headline(compute.load_and_validate(data, history=False))
        for key in ("median_year", "before_2050", "after_2100", "percentiles", "histogram", "branches", "counts", "method"):
            self.assertIn(key, h)
        self.assertEqual(h["median_year"], again["median_year"])
        self.assertEqual(h["percentiles"], again["percentiles"])
        self.assertEqual(h["before_2050"], again["before_2050"])
        self.assertEqual(h["method"]["runs"], compute.RUNS)
        self.assertEqual(h["method"]["seed"], compute.SEED)
        self.assertLessEqual(h["percentiles"]["p5"], h["median_year"])
        self.assertLessEqual(h["median_year"], h["percentiles"]["p95"])
        self.assertAlmostEqual(sum(b["share"] for b in h["histogram"]), 1.0, places=2)
        self.assertEqual(len(h["branches"]), 8)
        self.assertIn("Escape year:", o.getvalue())

    def test_the_first_pass_count_covers_every_estimate_and_the_drawn_count_only_those_drawn(self):
        loaded = compute.load_and_validate(DATA, history=False)
        counts = compute.compute_headline(loaded, runs=2000)["counts"]
        self.assertGreaterEqual(counts["estimates_first_pass"], counts["estimates_first_pass_drawn"])
        self.assertLessEqual(counts["estimates_first_pass"] - counts["estimates_first_pass_drawn"],
                             counts["leaves_in_clinic_already"])

    def test_a_different_seed_or_run_count_changes_nothing_structural(self):
        loaded = compute.load_and_validate(DATA, history=False)
        small = compute.compute_headline(loaded, runs=2000, seed=1)
        self.assertEqual(len(small["branches"]), 8)
        self.assertGreaterEqual(small["percentiles"]["p5"], 2026)

    def test_known_clinic_years_are_read_not_drawn(self):
        loaded = compute.load_and_validate(DATA, history=False)
        leaves = {r["id"]: r for r in loaded["records"] if r["_kind"] == "leaf"}
        self.assertEqual(compute.clinic_year(leaves["drug-stops-a-misfolded-protein-piling-up-in-the-heart"]), 2019)
        self.assertIsNone(compute.clinic_year(leaves[LEAF.stem]))
        self.assertEqual(compute.clinic_range(leaves[LEAF.stem]), (2031, 2038, 2060))

    def test_a_leaf_in_wide_use_reads_its_clinic_year_from_the_earlier_stage(self):
        leaf = {"stage": "in-wide-use", "stage_reached_on": "2030-01-01",
                "earlier_stage": [{"stage": "in-clinical-use", "reached_on": "2021-05"}]}
        self.assertEqual(compute.clinic_year(leaf), 2021)
        leaf["earlier_stage"] = []
        self.assertEqual(compute.clinic_year(leaf), 2030)

    def test_the_escape_year_is_never_before_the_latest_known_branch(self):
        # Every branch's handled year is at least its handled_when-th earliest possible year, so
        # the 5th percentile cannot be before the latest of those across required branches
        # plus the smallest lag.
        loaded = compute.load_and_validate(DATA, history=False)
        h = compute.compute_headline(loaded, runs=5000)
        floors = []
        for b in h["branches"]:
            if not b["required"]:
                continue
            years = sorted(f["year"] if f["known"] else f["earliest"] for f in b["leaves"])
            floors.append(years[b["handled_when"] - 1])
        self.assertGreaterEqual(h["percentiles"]["p5"], max(floors) + compute.LAG[0])


if __name__ == "__main__":
    unittest.main(verbosity=1)
