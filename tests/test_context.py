"""Agent context exposes selected observations, never private raw snapshots."""

import json
import unittest

from cortex_neo.context import context_report, context_text


class ContextTests(unittest.TestCase):
    def test_symbolic_slashes_survive_while_absolute_paths_are_redacted(self):
        result = context_report(
            {
                "software": [
                    {"label": "Python (active/OS)", "version": "3.14"},
                    {"label": "C/C++", "version": "/home/PRIVATE/tool"},
                ]
            }
        )
        self.assertEqual(
            {item["label"] for item in result["software"]}, {"Python (active/OS)", "C/C++"}
        )
        self.assertNotIn("PRIVATE", json.dumps(result))

    def test_driver_and_inventory_have_their_own_observation_age(self):
        result = context_report(
            {"sampled_at": 100, "software_observed_at": 80, "gpu": {"driver": "595.99"}}, now=105
        )
        self.assertEqual(result["gpu"]["driver"], "595.99")
        self.assertEqual(result["age_seconds"], 5)
        self.assertEqual(result["software_age_seconds"], 25)

    def test_selected_context_is_useful_without_personal_fields(self):
        raw = {
            "sampled_at": 100,
            "hostname": "PRIVATE-HOST",
            "weather": {"location": {"name": "PRIVATE-CITY"}},
            "cpu": {"top": [{"name": "PRIVATE-PROCESS"}]},
            "disks": [{"target": "/home/private-project"}],
            "hardware": {
                "cpu_model": "Ryzen 7",
                "cpu_topology": "8 cores / 16 threads",
                "ram_model": "PRIVATE-SERIAL",
            },
            "ram": {"total": 16 * 1024**3},
            "gpu": {"model": "Intel Iris Xe", "frequency": 400},
            "os": {"name": "Ubuntu", "kernel": "7.0", "arch": "x86_64"},
            "software_ready": True,
            "software": [{"label": "Python", "version": "3.14", "detail": "PRIVATE-BUILD-PATH"}],
        }
        report = context_report(raw, now=105)
        text = context_text(report)
        self.assertIn("Ryzen 7", text)
        self.assertIn("Python", text)
        self.assertIn("frequency", text)
        self.assertNotIn("PRIVATE", json.dumps(report))
        self.assertTrue(report["fresh"])
        self.assertTrue(report["software_complete"])

    def test_partial_stale_and_missing_are_not_absence_claims(self):
        report = context_report({"sampled_at": 100, "software_ready": False}, now=120)
        self.assertFalse(report["fresh"])
        self.assertFalse(report["software_complete"])
        self.assertIn("does not mean", context_text(report))
        missing = context_report(None, now=120)
        self.assertEqual(missing["status"], "unavailable")
        self.assertIsNone(missing["age_seconds"])

    def test_malformed_long_inventory_and_paths_are_bounded(self):
        report = context_report(
            {
                "software": [None, {}, {"label": "Python", "version": "/home/secret/tool"}] * 200,
                "os": [],
            },
            now=0,
        )
        self.assertLessEqual(len(report["software"]), 100)
        self.assertNotIn("/home/secret", json.dumps(report))
        self.assertEqual(context_report({"sampled_at": float("nan")})["status"], "unavailable")
