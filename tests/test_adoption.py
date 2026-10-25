"""Identify installed source bytes without guessing revisions or exposing paths."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cortex_neo.version import stamp_source, version_info


class AdoptionTests(unittest.TestCase):
    def test_clone_revision_is_carried_without_git_or_private_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, release = root / "source", root / "release"
            (source / "cortex_neo").mkdir(parents=True)
            (source / ".git").mkdir()
            (source / "pyproject.toml").write_text('[project]\nversion="1.2.0"\n')
            (source / "cortex_neo/_revision.txt").write_text("$Format:%H$")
            release.mkdir()
            shutil.copytree(source / "cortex_neo", release / "cortex_neo")
            shutil.copy2(source / "pyproject.toml", release / "pyproject.toml")
            with patch("cortex_neo.version._git", side_effect=["b" * 40, " M changed.py"]):
                stamp_source(source, release)
            info = version_info(release, allow_git=False)
            self.assertEqual(info["revision"], "b" * 40)
            self.assertTrue(info["source_dirty"])
            self.assertFalse((release / ".git").exists())
            fingerprint = info["source_fingerprint"]
            (release / "config").mkdir()
            (release / "config/location.json").write_text('{"name":"PRIVATE-CITY"}')
            self.assertEqual(
                version_info(release, allow_git=False)["source_fingerprint"], fingerprint
            )

    def test_archive_identity_and_local_source_change_are_distinguished(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "cortex_neo").mkdir()
            (root / "pyproject.toml").write_text('[project]\nversion = "1.2.0"\n')
            (root / "cortex_neo/_revision.txt").write_text("a" * 40)
            code = root / "cortex_neo/provider.py"
            code.write_text("value = 1\n")
            before = version_info(root, allow_git=False)
            self.assertEqual(before["version"], "1.2.0")
            self.assertEqual(before["revision"], "a" * 40)
            self.assertEqual(len(before["source_fingerprint"]), 64)
            (root / "installation.json").write_text(
                json.dumps(
                    {
                        "project": "cortex-neo",
                        "format": 1,
                        "application": {"source_fingerprint": before["source_fingerprint"]},
                    }
                )
            )
            self.assertTrue(version_info(root, allow_git=False)["matches_installed_source"])
            code.write_text("value = 2\n")
            self.assertFalse(version_info(root, allow_git=False)["matches_installed_source"])
            self.assertNotIn(str(root), json.dumps(version_info(root, allow_git=False)))

    def test_unversioned_source_never_claims_a_revision_or_complete_fingerprint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = version_info(root, allow_git=False)
            self.assertEqual(value["version"], "unknown")
            self.assertIsNone(value["revision"])
            self.assertIsNone(value["source_fingerprint"])
            self.assertIsNone(value["matches_installed_source"])

    def test_cli_version_json_reports_the_actual_project_version(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "-m", "cortex_neo", "version", "--format", "json"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["version"], "1.2.0")
        self.assertEqual(len(report["source_fingerprint"]), 64)
