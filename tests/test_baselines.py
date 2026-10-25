"""Named observations compare capabilities without claiming removal or causation."""

import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from cortex_neo.baselines import (
    compare_contexts,
    export_baseline,
    list_baselines,
    load_context_file,
    remove_baseline,
    save_baseline,
)
from cortex_neo.context import context_report


class BaselineTests(unittest.TestCase):
    def test_capacity_and_concurrent_names_never_displace_references(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index in range(20):
                save_baseline(f"reference-{index}", self.context(), state=root)
            with self.assertRaises(ValueError):
                save_baseline("overflow", self.context(), state=root)
            self.assertEqual(len(list_baselines(state=root)), 20)
            self.assertEqual(
                export_baseline("reference-0", state=root)["software"][0]["version"], "1.0"
            )

            def save(_):
                try:
                    save_baseline("same-name", self.context(), state=root / "parallel")
                    return True
                except ValueError:
                    return False

            with ThreadPoolExecutor(max_workers=2) as workers:
                self.assertEqual(sum(workers.map(save, range(2))), 1)

    def context(self, version="1.0", ready=True):
        return context_report(
            {
                "sampled_at": 100,
                "software_ready": ready,
                "os": {"kernel": "7.0"},
                "software": [{"label": "Python", "version": version}],
                "hostname": "PRIVATE-HOST",
            },
            now=100,
        )

    def test_save_export_compare_remove_and_preserve_named_references(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            save_baseline("frontend validado", self.context(), state=state)
            self.assertEqual(len(list_baselines(state=state)), 1)
            with self.assertRaises(ValueError):
                save_baseline("FRONTEND VALIDADO", self.context("2.0"), state=state)
            reference = export_baseline("frontend validado", state=state)
            self.assertNotIn("PRIVATE", json.dumps(reference))
            self.assertEqual(compare_contexts(reference, reference)["differences"], [])
            compared = compare_contexts(reference, self.context("2.0"))
            self.assertIn("Python", json.dumps(compared))
            self.assertTrue(compared["differences"])
            remove_baseline("frontend validado", state=state)
            self.assertEqual(list_baselines(state=state), [])

    def test_partial_inventory_differences_stay_uncertain(self):
        result = compare_contexts(self.context(), self.context("2.0", ready=False))
        software = next(
            item for item in result["differences"] if item["field"] == "software.Python"
        )
        self.assertEqual(software["evidence"], "partial_inventory")
        self.assertNotIn("uninstalled", json.dumps(result))

    def test_untrusted_files_schema_size_and_names_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "context.json"
            path.write_text(json.dumps(self.context()))
            self.assertEqual(load_context_file(path)["kind"], "cortex-neo-context")
            path.write_text('{"kind":"something-else"}')
            with self.assertRaises(ValueError):
                load_context_file(path)
            path.write_bytes(b" " * (1024 * 1024 + 1))
            with self.assertRaises(ValueError):
                load_context_file(path)
            with self.assertRaises(ValueError):
                save_baseline("../../secret", self.context(), state=root)
