"""Missing software and a failed sibling probe must not corrupt the inventory."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cortex_neo import versions


class VersionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.home = Path(self.directory.name)

    def test_no_tools_no_language_rows(self):
        with (
            patch.object(Path, "home", return_value=self.home),
            patch.object(versions, "executable", return_value=None),
            patch.object(versions, "command", return_value=None),
            patch.object(versions, "read_json", return_value={}),
        ):
            self.assertEqual(versions.installed_versions(), [])

    def test_dpkg_partial_output_is_preserved(self):
        output = "code\t1.2.3\tii \nbrave-browser\t1.2.0\trc \ndocker-ce\t5:29.9.2-1\tii "
        with patch.object(versions, "command", return_value=output) as probe:
            self.assertEqual(versions.packages(), {"code": "1.2.3", "docker-ce": "5:29.9.2-1"})
            self.assertEqual(probe.call_args.kwargs["accepted"], (0, 1))

    def test_broken_compiler_probe_does_not_drop_other_entries(self):
        def broken_node_probe():
            raise ValueError("bad JSON")

        with (
            patch.object(
                versions,
                "applications",
                return_value=[dict(label="Brave", version="1.2", detail="", group="Aplicaciones")],
            ),
            patch.object(versions, "node_versions", new=broken_node_probe),
            patch.object(versions, "python_versions", return_value=[]),
            patch.object(versions, "compiled_languages", return_value=[]),
            patch.object(versions, "other_languages", return_value=[]),
            patch.object(versions, "shells", return_value=[]),
        ):
            with self.assertLogs("cortex_neo.versions", level="WARNING"):
                self.assertEqual([v["label"] for v in versions.installed_versions()], ["Brave"])

    def test_failing_gcc_never_indexes_an_empty_banner(self):
        with (
            patch.object(
                versions,
                "executable",
                side_effect=lambda name, *args: "/fake/gcc" if name == "gcc" else None,
            ),
            patch.object(versions, "command", return_value=None),
        ):
            self.assertEqual(versions.compiled_languages(), [])

    def test_leftover_product_metadata_does_not_claim_an_uninstalled_app(self):
        with (
            patch.object(versions, "packages", return_value={}),
            patch.object(versions, "executable", return_value=None),
            patch.object(versions, "read_json", return_value={"version": "9.9.9", "commit": "old"}),
        ):
            self.assertEqual(versions.applications(), [])
