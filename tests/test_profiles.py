"""Profiles preserve readable fonts and work-area bounds with fewer visible details."""

import re
import tempfile
import time
import unittest
from pathlib import Path

from lua_harness import LuaHarness

from cortex_neo.layout import calculate
from cortex_neo.preferences import load_preferences, update_preferences
from cortex_neo.render import config


class ProfileTests(unittest.TestCase):
    def test_compact_and_auto_keep_core_cards_inside_small_area(self):
        for area in [(0, 30, 900, 650), (50, 32, 700, 1000)]:
            for selected in ("compact", "auto"):
                plan = calculate(area, profile=selected, density="comfortable")
                self.assertEqual(plan["presentation_profile"], "compact")
                self.assertNotIn("software", plan["cards"])
                self.assertIn("cpu", plan["cards"])
                self.assertLessEqual(plan["x"] + plan["width"], area[0] + area[2])
                self.assertLessEqual(plan["y"] + plan["height"], area[1] + area[3])
                text = config("cpu", plan["cards"]["cpu"], plan, {})
                self.assertGreaterEqual(min(map(int, re.findall(r"size=(\d+)", text))), 9)
                self.assertEqual(plan["cards"]["cpu"]["h"], plan["cards"]["ram"]["h"])

    def test_profile_is_persistent_and_invalid_values_do_not_replace_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            update_preferences(root, profile="compact", density="comfortable")
            self.assertEqual(load_preferences(root)["profile"], "compact")
            with self.assertRaises(ValueError):
                update_preferences(root, profile="unlimited")
            self.assertEqual(load_preferences(root)["profile"], "compact")

    def test_comfortable_lua_limits_top_and_removes_build_details(self):
        snapshot = {
            "sampled_at": time.time(),
            "cpu": {"top": [{"name": f"process-{n}", "percent": 1} for n in range(5)]},
            "ram": {"top": [{"name": "app", "rss": 100}]},
            "software": [{"label": "Tool", "version": "1.0", "detail": "BUILD-SENTINEL"}],
        }
        view = LuaHarness(
            snapshot, ui={"density": "comfortable", "top_count": 3, "min_font_size": 9}
        )
        self.addCleanup(view.close)
        top = view.call("cpu_top")
        self.assertIn("process-2", top)
        self.assertNotIn("process-3", top)
        self.assertNotIn("BUILD-SENTINEL", view.call("software"))
        self.assertGreaterEqual(
            min(map(int, re.findall(r"size=(\d+)", view.call("memory_top")))), 9
        )
        self.assertIn("Live", view.call("status"))
