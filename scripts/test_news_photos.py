#!/usr/bin/env python3
"""Checks for the picture rules in scripts/check_news.py (tracker pattern, rule 4.23).

    python3 scripts/test_news_photos.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_news  # noqa: E402

HEAD = ("---\ntitle: A comet\ndate: 2026-11-09\nkind: claim\nsummary: Found.\n"
        "photos:\n  - file: 2026-11-09-a-comet.jpg\n    source: https://example.org/picture\n"
        "    credit: \"The Agency, A. Person\"\n    licence: Creative Commons Attribution 4.0\n"
        "    licence_url: https://creativecommons.org/licenses/by/4.0/\n    read_on: 2026-11-14\n---\n")
FIGURE = ('<figure>\n<img src="/news/2026-11-09-a-comet.jpg" alt="A fuzzy smudge on a dark sky." width="420" height="420">\n'
          '<figcaption>The comet. <a href="https://example.org/picture">Picture</a>: The Agency, A. Person.</figcaption>\n</figure>\n')


class Pictures(unittest.TestCase):
    def problems(self, text, with_file=True):
        fm, body = check_news.frontmatter(text)
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            if with_file:
                (d / "2026-11-09-a-comet.jpg").write_bytes(b"x")
            return check_news.check_photos("post.md", fm, body, d)

    def test_a_recorded_picture_passes(self):
        self.assertEqual(self.problems(HEAD + "\n" + FIGURE), [])

    def test_a_post_with_no_picture_passes(self):
        self.assertEqual(self.problems("---\ntitle: T\n---\n\nWords only.\n"), [])

    def test_a_picture_with_no_entry_is_refused(self):
        bare = "---\ntitle: T\n---\n\n" + FIGURE
        self.assertTrue(any("no entry under photos" in p for p in self.problems(bare)))

    def test_a_missing_licence_is_refused(self):
        bad = HEAD.replace("    licence: Creative Commons Attribution 4.0\n", "")
        self.assertTrue(any("has no licence under photos" in p for p in self.problems(bad + "\n" + FIGURE)))

    def test_a_missing_description_is_refused(self):
        bad = FIGURE.replace(' alt="A fuzzy smudge on a dark sky."', "")
        self.assertTrue(any("no description" in p for p in self.problems(HEAD + "\n" + bad)))

    def test_a_picture_loaded_from_another_site_is_refused(self):
        bad = FIGURE.replace('src="/news/', 'src="https://example.org/')
        self.assertTrue(any("not served from /news/" in p for p in self.problems(HEAD + "\n" + bad)))

    def test_a_caption_that_does_not_link_to_the_source_is_refused(self):
        bad = FIGURE.replace('<a href="https://example.org/picture">Picture</a>', "Picture")
        self.assertTrue(any("does not link to its source page" in p for p in self.problems(HEAD + "\n" + bad)))

    def test_a_picture_outside_a_figure_is_refused(self):
        bad = '<img src="/news/2026-11-09-a-comet.jpg" alt="A smudge.">\n'
        self.assertTrue(any("outside a <figure>" in p for p in self.problems(HEAD + "\n" + bad)))

    def test_a_markdown_picture_is_refused(self):
        self.assertTrue(any("write it as a <figure>" in p for p in self.problems(HEAD + "\n" + FIGURE + "\n![a](/news/x.jpg)\n")))

    def test_a_listed_picture_that_is_not_shown_is_refused(self):
        self.assertTrue(any("does not show" in p for p in self.problems(HEAD + "\nWords only.\n")))

    def test_a_missing_file_is_refused(self):
        self.assertTrue(any("is not in" in p for p in self.problems(HEAD + "\n" + FIGURE, with_file=False)))


if __name__ == "__main__":
    unittest.main()
