"""Probes must expose broken dependencies, not only binary/module presence."""

import subprocess
import unittest

from cortex_neo.conky import capabilities, window_settings
from cortex_neo.diagnostics import inspect

BANNER = "conky 1.22.2 compiled for Linux\n Lua bindings:\n  * Cairo\n X11:\n  * Xft\n Wayland:\n"


class DiagnosticsTests(unittest.TestCase):
    def probe(self, argv):
        output = ""
        if "--version" in argv:
            output = BANNER
        elif argv[0] == "fc-match":
            output = argv[-1]
        return subprocess.CompletedProcess(argv, 0, output, "")

    def test_legacy_and_modern_backend_versions(self):
        legacy = capabilities(BANNER)
        self.assertTrue(legacy["x11"] and legacy["lua"])
        self.assertIn("out_to_wayland=false", window_settings(legacy)[0])
        modern = capabilities(BANNER.replace("1.22.2", "1.24.3"))
        backend, color = window_settings(modern)
        self.assertEqual(backend, "output_backend='x11',")
        self.assertNotIn("argb_value", color)
        self.assertIn("#BE081220", color)
        self.assertNotIn("wayland", window_settings(capabilities(BANNER.split(" Wayland:")[0]))[0])
        self.assertFalse(capabilities("garbage")["version"])

    def test_complete_dependencies_without_session_do_not_probe_user_bus_or_display(self):
        calls = []

        def probe(argv):
            calls.append(argv)
            return self.probe(argv)

        result = inspect(session=False, runner=probe, locate=lambda name: name, version=(3, 11, 0))
        self.assertTrue(result["ok"])
        self.assertFalse(any(argv[0] == "systemctl" for argv in calls))

    def test_broken_import_and_fallback_icons_are_errors(self):
        def probe(argv):
            if "import psutil" in argv:
                return subprocess.CompletedProcess(argv, 1, "", "broken native extension")
            if argv[0] == "fc-match":
                return subprocess.CompletedProcess(argv, 0, "DejaVu Sans", "")
            return self.probe(argv)

        result = inspect(session=False, runner=probe, locate=lambda name: name)
        errors = {c["name"] for c in result["checks"] if c["status"] == "error"}
        self.assertIn("psutil", errors)
        self.assertIn("icons", errors)
        self.assertNotIn("monospace", errors)
        self.assertFalse(result["ok"])
        self.assertTrue(all(c["remedy"] for c in result["checks"] if c["status"] != "ok"))

    def test_missing_conky_does_not_pass(self):
        result = inspect(session=False, runner=self.probe, locate=lambda name: None)
        self.assertFalse(result["ok"])
        self.assertEqual(result["conky"]["version"], "")

    def test_newest_python_accepted_and_oldest_rejected(self):
        for version, expected in [((3, 10, 22), False), ((3, 11, 0), True), ((3, 15, 1), True)]:
            result = inspect(
                session=False, runner=self.probe, locate=lambda name: name, version=version
            )
            self.assertEqual(result["ok"], expected)
