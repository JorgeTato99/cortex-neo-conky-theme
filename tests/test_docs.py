"""Prevent documentation moves from leaving broken local image/page links."""

import tempfile
import unittest
from pathlib import Path

from scripts.check_docs import broken_links


class DocumentationTests(unittest.TestCase):
    def test_missing_pages_and_images_fail_but_external_and_example_links_do_not(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "[valid](page.md) [external](https://example.org/x)\n"
                "![image](missing.webp) [old](old.md)\n"
                "```md\n[example](not-a-real-link.md)\n```\n"
            )
            (root / "page.md").touch()
            self.assertEqual(broken_links(root), ["README.md: missing.webp", "README.md: old.md"])
