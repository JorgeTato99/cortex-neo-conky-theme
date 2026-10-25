"""Measure collector work and own processes without counting shared RSS as private."""

import json
import tempfile
import unittest
from pathlib import Path

from cortex_neo.io import publish_snapshot
from cortex_neo.observability import CycleMetrics, process_delta


class ObservabilityTests(unittest.TestCase):
    def test_publication_keeps_history_for_tools_but_not_graphic_readers(self):
        snapshot = {"sampled_at": 12, "cpu": {"load": 5}, "history": [{"cpu": 5}] * 121}
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            publish_snapshot(cache, snapshot)
            self.assertEqual(json.loads((cache / "dashboard.json").read_text()), snapshot)
            graphic = (cache / "dashboard.lua").read_text()
            self.assertNotIn('["history"]', graphic)
            self.assertIn('["load"]=5', graphic)
            self.assertLess(len(graphic), (cache / "dashboard.json").stat().st_size)
        self.assertEqual(len(snapshot["history"]), 121)

    def test_cycle_records_success_failure_and_deadline(self):
        ticks = iter([0, 0.1, 0.3, 0.4, 0.7, 2.1])
        cycle = CycleMetrics(2, clock=lambda: next(ticks))
        self.assertEqual(cycle.call("cpu", lambda: 42), 42)
        with self.assertRaisesRegex(ValueError, "sensor"):
            cycle.call("gpu", lambda: (_ for _ in ()).throw(ValueError("sensor")))
        result = cycle.finish()
        self.assertAlmostEqual(result["providers_ms"]["cpu"], 200)
        self.assertAlmostEqual(result["providers_ms"]["gpu"], 300)
        self.assertEqual(result["sample_ms"], 2100)
        self.assertTrue(result["overrun"])

    def test_process_identity_churn_and_machine_normalization(self):
        before = {(1, 10): (4, 100), (2, 20): (2, 200)}
        after = {(1, 10): (6, 110), (2, 30): (50, 300)}
        result = process_delta(before, after, 2, 4)
        self.assertEqual(result["cpu_core_percent"], 100)
        self.assertEqual(result["cpu_machine_percent"], 25)
        self.assertEqual(result["rss_bytes"], 410)
        self.assertEqual(result["processes"], 2)
        self.assertIn("shared", result["memory_measure"])

    def test_invalid_measurement_never_produces_fake_utilization(self):
        self.assertIsNone(process_delta({}, {}, 2, 4)["cpu_core_percent"])
        with self.assertRaises(ValueError):
            process_delta({}, {}, 0, 4)


if __name__ == "__main__":
    unittest.main()
