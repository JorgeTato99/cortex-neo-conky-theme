"""Minute aggregates preserve absence, extrema, retention and restart identity."""

import tempfile
import unittest
from pathlib import Path

from cortex_neo.history import HistoryStore


class HistoryTests(unittest.TestCase):
    def test_minute_boundary_extrema_average_and_missing_values(self):
        with tempfile.TemporaryDirectory() as directory:
            store = HistoryStore(Path(directory), hours=1)
            store.record(
                {
                    "time": 60,
                    "cpu": 10,
                    "gpu": None,
                    "cpu_top": [{"name": "PRIVATE-PROCESS", "percent": 1}],
                }
            )
            store.record({"time": 62, "cpu": 30, "gpu": None})
            store.record({"time": 120, "cpu": 50, "gpu": 20})
            store.flush(force=True)
            self.assertNotIn("PRIVATE", (Path(directory) / "history/minutes.json").read_text())
            rows = store.query(now=121, hours=1)["minutes"]
            self.assertEqual(len(rows), 2)
            self.assertEqual(
                rows[0]["metrics"]["cpu"], {"count": 2, "minimum": 10, "maximum": 30, "average": 20}
            )
            self.assertIsNone(rows[0]["metrics"]["gpu"]["average"])
            self.assertEqual(rows[0]["metrics"]["gpu"]["count"], 0)

    def test_restart_deduplication_retention_and_clock_regression(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = HistoryStore(root, hours=1)
            store.record({"time": 0, "cpu": 10})
            store.record({"time": 2, "cpu": 20})
            store.flush(force=True)
            resumed = HistoryStore(root, hours=1)
            resumed.record({"time": 2, "cpu": 20})
            resumed.record({"time": 1, "cpu": 99})
            self.assertEqual(
                resumed.query(now=3, hours=1)["minutes"][0]["metrics"]["cpu"]["count"], 2
            )
            resumed.record({"time": 3660, "cpu": 40})
            self.assertEqual(len(resumed.query(now=3660, hours=1)["minutes"]), 1)

    def test_disabled_and_failed_write_leave_live_sampling_usable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            disabled = HistoryStore(root, hours=0)
            disabled.record({"time": 60, "cpu": 10})
            self.assertFalse(disabled.flush(force=True))
            self.assertFalse((root / "history/minutes.json").exists())
            blocked = root / "blocked"
            blocked.write_text("not a directory")
            store = HistoryStore(blocked, hours=1)
            store.record({"time": 60, "cpu": 10})
            self.assertFalse(store.flush(force=True))
            self.assertEqual(
                store.query(now=61, hours=1)["minutes"][0]["metrics"]["cpu"]["average"], 10
            )
