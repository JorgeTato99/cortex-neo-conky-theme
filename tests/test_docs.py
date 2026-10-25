"Prevent documentation moves from leaving broken local image/page links."

import hashlib
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.check_docs import broken_links
from scripts.generate_readme import render_readmes, stale_readmes


class DocumentationTests(unittest.TestCase):
    def copy_readme_sources(self, root):
        source = Path(__file__).resolve().parents[1]
        shutil.copytree(source / "docs/readme", root / "docs/readme")
        (root / "assets/screenshots").mkdir(parents=True)
        shutil.copyfile(
            source / "assets/screenshots/manifest.json", root / "assets/screenshots/manifest.json"
        )

    def test_published_readmes_are_generated_from_the_same_structure(self):
        self.assertEqual(stale_readmes(), [])
        pages = render_readmes()
        self.assertEqual(pages["README.en.md"], pages["README.md"])

    def test_bilingual_galleries_use_the_same_ten_native_images(self):
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads((root / "assets/palettes/manifest.json").read_text(encoding="utf-8"))
        expected = [str((root / item["file"]).resolve()) for item in manifest["palettes"]]
        self.assertEqual(len(expected), 10)
        self.assertEqual(len(set(expected)), 10)
        for item in manifest["palettes"]:
            self.assertEqual(item["capture_type"], "native GNOME screenshot portal")
            self.assertTrue(item["lossless"] and item["decoded_pixels_equal"])
            self.assertTrue((root / item["file"]).is_file())
            self.assertEqual(
                hashlib.sha256((root / item["file"]).read_bytes()).hexdigest(), item["webp_sha256"]
            )
        for name in ("docs/reference/appearance.md", "docs/es/reference/appearance.md"):
            page = root / name
            images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", page.read_text(encoding="utf-8"))
            self.assertEqual([str((page.parent / image).resolve()) for image in images], expected)

    def test_manual_language_only_image_drift_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_readme_sources(root)
            for name, content in render_readmes(root).items():
                (root / name).write_text(content, encoding="utf-8")
            spanish = root / "README.es.md"
            spanish.write_text(
                spanish.read_text(encoding="utf-8") + "\n![extra](extra.webp)\n", encoding="utf-8"
            )
            self.assertEqual(stale_readmes(root), ["README.es.md"])

    def test_missing_translations_and_block_structure_in_catalogs_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_readme_sources(root)
            path = root / "docs/readme/es.json"
            original = json.loads(path.read_text(encoding="utf-8"))
            incomplete = {key: value for key, value in original.items() if key != "CAPTURE_NOTE"}
            path.write_text(json.dumps(incomplete), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "translation keys"):
                render_readmes(root)
            path.write_text(
                json.dumps({**original, "INTRO": "Paragraph\n\n## Extra section"}), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "inline text"):
                render_readmes(root)

    def test_each_primary_topic_has_a_spanish_counterpart(self):
        root = Path(__file__).resolve().parents[1] / "docs"
        for page in root.rglob("*.md"):
            relative = page.relative_to(root)
            if relative.parts[0] not in ("en", "es"):
                self.assertTrue((root / "es" / relative).is_file(), str(relative))

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
