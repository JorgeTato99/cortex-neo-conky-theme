"""Capture real bounded timelines and remove private names only when exporting."""

import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from cortex_neo.incidents import capture_incident, list_incidents, load_incident, public_incident
from cortex_neo.io import atomic


class IncidentTests(unittest.TestCase):
    def test_concurrent_writers_preserve_valid_json_and_retention(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def capture(_):
                return capture_incident(
                    "concurrent", after=0, cache=root / "missing", state=root, max_records=1
                )

            with ThreadPoolExecutor(max_workers=2) as workers:
                results = list(workers.map(capture, range(2)))
            records = list_incidents(state=root)
            self.assertEqual(len(records), 1)
            self.assertIn(records[0]["id"], {record["id"] for record in results})
            self.assertEqual(load_incident(records[0]["id"], state=root)["status"], "no_data")

    def test_before_and_after_samples_are_saved_with_private_local_tops(self):
        with tempfile.TemporaryDirectory() as directory:
            cache, state = Path(directory) / "cache", Path(directory) / "state"
            current = [100.0]

            def publish():
                points = [
                    {
                        "time": t,
                        "cpu": t - 90,
                        "ram": 20,
                        "cpu_top": [{"name": "PRIVATE-PROCESS", "percent": 5}],
                    }
                    for t in (98, 100, 102, 104)
                    if t <= current[0]
                ]
                atomic(cache / "dashboard.json", json.dumps({"history": points}))

            def sleep(seconds):
                current[0] += seconds
                publish()

            publish()
            record = capture_incident(
                "PRIVATE-LABEL",
                before=10,
                after=4,
                cache=cache,
                state=state,
                clock=lambda: current[0],
                monotonic=lambda: current[0],
                sleep=sleep,
            )
            self.assertEqual([p["time"] for p in record["points"]], [98, 100, 102, 104])
            self.assertIn("PRIVATE", json.dumps(record))
            self.assertNotIn("PRIVATE", json.dumps(public_incident(record)))
            self.assertEqual(load_incident(record["id"], state=state)["id"], record["id"])

    def test_retention_never_removes_foreign_files_and_empty_data_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "incidents").mkdir()
            foreign = root / "incidents/do-not-delete.json"
            foreign.write_text("keep")
            for _ in range(4):
                result = capture_incident(
                    "empty", before=0, after=0, cache=root / "missing", state=root, max_records=2
                )
            self.assertEqual(result["status"], "no_data")
            self.assertEqual(len(list_incidents(state=root)), 2)
            self.assertEqual(foreign.read_text(), "keep")
            with self.assertRaises(ValueError):
                load_incident("../../secret", state=root)
            with self.assertRaises(ValueError):
                capture_incident("bad", before=241, state=root)

    def test_keyboard_interrupt_preserves_the_partial_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def interrupt(seconds):
                raise KeyboardInterrupt

            result = capture_incident(
                "partial", after=2, cache=root / "missing", state=root, sleep=interrupt
            )
            self.assertEqual(result["status"], "interrupted")
            self.assertEqual(len(list_incidents(state=root)), 1)
