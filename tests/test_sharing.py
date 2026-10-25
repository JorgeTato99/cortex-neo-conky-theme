"""Presentation masks live labels and support reports select only public fields."""

import json
import tempfile
import time
import unittest
from pathlib import Path

from lua_harness import LuaHarness

from cortex_neo.layout import calculate
from cortex_neo.sharing import presentation_state, set_presentation, support_report, support_text


class SharingTests(unittest.TestCase):
    def test_explicit_missing_runtime_flag_restores_normal_view_despite_old_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            set_presentation(True, runtime=root)
            set_presentation(False, runtime=root)
            view = LuaHarness(
                self.private_snapshot(),
                ui={"presentation_file": str(root / "cortex-neo/presentation.flag")},
            )
            self.addCleanup(view.close)
            self.assertIn("PRIVATE-HOST", view.call("system_meta"))
            self.assertIn("En vivo", view.call("status"))

    def test_runtime_expiry_off_and_corrupt_flags_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            set_presentation(True, runtime=root, minutes=1, now=100)
            self.assertTrue(presentation_state(runtime=root, now=159)["enabled"])
            self.assertFalse(presentation_state(runtime=root, now=160)["enabled"])
            flag = root / "cortex-neo/presentation.flag"
            flag.write_text("broken")
            self.assertTrue(presentation_state(runtime=root, now=160)["enabled"])
            flag.write_bytes(b"\xff\xfe\x00")
            self.assertTrue(presentation_state(runtime=root, now=160)["enabled"])
            set_presentation(False, runtime=root)
            self.assertFalse(presentation_state(runtime=root)["enabled"])
            foreign = root / "foreign.flag"
            foreign.write_text("v1 100 160\n")
            flag.symlink_to(foreign)
            self.assertTrue(presentation_state(runtime=root, now=200)["enabled"])
            set_presentation(False, runtime=root)
            self.assertEqual(foreign.read_text(), "v1 100 160\n")
            with self.assertRaises(ValueError):
                set_presentation(True, runtime=root / "missing")

    def private_snapshot(self):
        return {
            "sampled_at": time.time(),
            "presentation": {"enabled": True},
            "hostname": "PRIVATE-HOST",
            "software": [{"label": "Tool", "version": "1.0", "detail": "PRIVATE-BUILD"}],
            "os": {"name": "Linux", "compiled": "PRIVATE-BUILD"},
            "cpu": {"top": [{"name": "PRIVATE-PROCESS", "percent": 1}]},
            "ram": {"top": [{"name": "PRIVATE-APP", "rss": 100}]},
            "weather": {"location": {"name": "PRIVATE-CITY"}},
            "network": {"kind": "Wi-Fi", "interface": "PRIVATE-INTERFACE"},
            "disks": [
                {"model": "SSD", "target": "/home/PRIVATE-PATH", "load": 5},
                {"model": "SSD2", "target": "/srv/PRIVATE-PATH", "load": 10},
            ],
        }

    def test_lua_masks_personal_labels_and_weather_leaves_layout(self):
        snapshot = self.private_snapshot()
        view = LuaHarness(snapshot)
        self.addCleanup(view.close)
        values = [
            view.call(name)
            for name in (
                "system_meta",
                "cpu_top",
                "memory_top",
                "weather",
                "disk_usage",
                "other_disks",
                "network_label",
                "software",
            )
        ]
        self.assertNotIn("PRIVATE", "\n".join(values))
        self.assertIn("Presentación", view.call("status"))
        self.assertNotIn("weather", calculate((0, 0, 1500, 900), snapshot)["cards"])

    def test_runtime_flag_masks_even_when_collector_snapshot_did_not_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            set_presentation(True, runtime=root)
            snapshot = self.private_snapshot()
            snapshot["presentation"] = {"enabled": False}
            view = LuaHarness(
                snapshot, ui={"presentation_file": str(root / "cortex-neo/presentation.flag")}
            )
            self.addCleanup(view.close)
            self.assertNotIn("PRIVATE", view.call("system_meta"))

    def test_support_diagnostics_and_layout_are_allowlisted(self):
        report = support_report(
            self.private_snapshot(),
            diagnostics={
                "checks": [{"name": "display", "status": "ok", "detail": "PRIVATE-DETAIL"}],
                "token": "PRIVATE-TOKEN",
                "conky": {"version": "1.22.2", "x11": True, "detail": "PRIVATE-BANNER"},
            },
            layout={
                "area": [10, 20, 1400, 800],
                "cards": {"cpu": {}, "PRIVATE-CARD": {}},
                "_private": "PRIVATE-LAYOUT",
            },
        )
        self.assertNotIn("PRIVATE", json.dumps(report))
        self.assertEqual(report["display"]["workarea_size"], [1400, 800])
        self.assertEqual(report["conky"]["version"], "1.22.2")
        self.assertIn("Conky: 1.22.2", support_text(report))
        self.assertIn("Versión: 1.2.0", support_text(report))
