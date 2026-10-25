"""Real Lua behavior for empty inventories, paging, stale metrics and scaling."""

import re
import time
import unittest

from lua_harness import LuaHarness

from cortex_neo.layout import calculate
from cortex_neo.render import config


class RenderTests(unittest.TestCase):
    def view(self, snapshot, scale=1):
        harness = LuaHarness({"sampled_at": time.time(), **snapshot}, scale)
        self.addCleanup(harness.close)
        return harness

    def test_no_language_heading_without_languages(self):
        self.assertEqual(self.view({"software": []}).call("software"), "")
        value = self.view(
            {"software": [dict(label="Code", version="1.0", detail="", group="Applications")]}
        ).call("software")
        self.assertIn("APPLICATIONS", value)
        self.assertNotIn("LENGUAJES", value)
        self.assertNotIn("Rust", value)

    def test_malformed_optional_rows_are_ignored(self):
        value = self.view(
            {"software": [{}, None, dict(label="Rust", version=None), dict(label="Go", version="")]}
        ).call("software")
        self.assertEqual(value, "")

    def test_long_inventory_pages_without_losing_entries(self):
        entries = [
            dict(
                label=f"APP_{i:02d}",
                version="1.0",
                detail="Build " + ("a" * 100),
                group="Languages",
            )
            for i in range(30)
        ]
        view = self.view({"software": entries})
        first = view.call("software", 1)
        total = int(re.search("Page 1 / (\\d+)", first).group(1))
        self.assertGreater(total, 1)
        pages = "\n".join(view.call("software", i) for i in range(1, total + 1))
        for item in entries:
            self.assertEqual(pages.count(item["label"]), 1)

    def test_stale_data_does_not_present_zero_percent(self):
        view = self.view({"sampled_at": 0, "cpu": {"load": 12}, "ram": {"load": 20}})
        self.assertEqual(view.call("cpu_usage"), "—")
        self.assertEqual(view.call("ram_usage"), "—")
        self.assertEqual(view.call("has", "cpu.load"), "0")
        self.assertIn("color6", view.call("status"))

    def test_intel_frequency_and_generated_graphs_keep_their_unit(self):
        snapshot = {"gpu": {"model": "Intel Iris Xe", "frequency": 400}, "software": []}
        text = self.view(snapshot).call("gpu_summary")
        self.assertIn("400 MHz", text)
        self.assertNotIn("%", text)
        plan = calculate((67, 32, 1299, 736), snapshot)
        output = config("gpu", plan["cards"]["gpu"], plan, snapshot)
        self.assertIn("gpu_frequency", output)
        self.assertNotIn("lua_graph gpu_load", output)
        self.assertNotIn("@", output)

    def test_small_monitor_scales_callback_fonts_as_well_as_card_sizes(self):
        text = self.view(
            {"software": [dict(label="Go", version="1.0", detail="", group="Languages")]}, 0.88
        ).call("software")
        self.assertIn("size=10", text)
        self.assertNotIn("size=11", text)

    def test_engine_only_does_not_invent_a_desktop_endpoint(self):
        text = self.view(
            {"docker_contexts": ["default"], "docker": {"default": {"running": 2}}}
        ).call("containers")
        self.assertIn("Engine: 2 running", text)
        self.assertNotIn("Desktop", text)

    def test_storage_distinguishes_mounted_ssds_by_target(self):
        view = self.view(
            {
                "disks": [
                    dict(model="Acer SSD", target="/", load=4, used=4, total=100),
                    dict(model="Acer SSD", target="/srv/dev", load=0, size=10**12),
                    dict(model="HDD", size=2 * 10**12),
                ]
            }
        )
        self.assertEqual(view.call("disk_summary"), "2 mounted / 1 unmounted")
        self.assertIn("/srv/dev 0.0%", view.call("other_disks", 1))
        self.assertIn("/ · USED", view.call("disk_usage"))
