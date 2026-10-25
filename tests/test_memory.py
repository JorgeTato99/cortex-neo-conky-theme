"""Memory pressure is an observation; missing counters and shared RSS are explicit."""

import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

import psutil
from lua_harness import LuaHarness

from cortex_neo.memory import MemoryMonitor, explain_memory, memory_details, parse_pressure


class MemoryTests(unittest.TestCase):
    def test_card_distinguishes_vm_scope_and_unknown_pressure(self):
        snapshot = {
            "sampled_at": time.time(),
            "ram": {
                "used": 1024**3,
                "total": 8 * 1024**3,
                "available": 7 * 1024**3,
                "top": [{"name": "qemu-system-x86_64", "rss": 1024**3, "scope": "virtual-machine"}],
            },
        }
        view = LuaHarness(snapshot)
        self.addCleanup(view.close)
        self.assertIn("disp 7.0G", view.call("memory_usage"))
        self.assertIn("[VM]", view.call("memory_top"))
        self.assertIn("PSI —", view.call("memory_top"))
        self.assertNotIn("Docker", view.call("memory_top"))

    def test_pressure_zero_missing_and_invalid_are_distinct(self):
        zero = parse_pressure(
            "some avg10=0.00 avg60=0.00 avg300=0.00 total=100\nfull avg10=0 avg60=0 avg300=0 total=0"
        )
        self.assertEqual(zero["some"]["avg10"], 0)
        self.assertIsNone(parse_pressure("some avg10=nan avg60=0 avg300=0 total=-1"))
        self.assertIsNone(parse_pressure(""))
        self.assertIn("No se observaron", explain_memory({"pressure": zero}))
        self.assertIn("no disponible", explain_memory({}))

    def test_swap_rates_and_available_keep_host_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "memory").write_text("some avg10=2.0 avg60=1 avg300=0 total=100")
            swaps = iter(
                [
                    SimpleNamespace(total=1000, used=10, sin=20, sout=40),
                    SimpleNamespace(total=1000, used=15, sin=120, sout=80),
                ]
            )
            monitor = MemoryMonitor(root, swap_reader=lambda: next(swaps))
            memory = SimpleNamespace(available=500, cached=200, buffers=20)
            first = monitor.sample(memory, 10)
            second = monitor.sample(memory, 12)
            self.assertIsNone(first["swap"]["in_bytes_per_second"])
            self.assertEqual(second["swap"]["in_bytes_per_second"], 50)
            self.assertEqual(second["available"], 500)
            self.assertIn("2.00%", explain_memory(second))
            self.assertNotIn("caus", explain_memory(second))

    def test_private_footprint_is_only_requested_for_explicit_bounded_pids(self):
        calls = []

        def factory(pid):
            calls.append(pid)
            if pid == 2:
                raise psutil.AccessDenied(pid)
            return SimpleNamespace(
                name=lambda: "qemu-system-x86_64",
                memory_full_info=lambda: SimpleNamespace(rss=100, pss=80, uss=60),
            )

        self.assertEqual(memory_details([], factory=factory), [])
        self.assertEqual(calls, [])
        details = memory_details([1, 2], factory=factory)
        self.assertEqual(details[0]["pss_bytes"], 80)
        self.assertEqual(details[1]["status"], "denied")
        self.assertNotIn("pss_bytes", details[1])
        with self.assertRaises(ValueError):
            memory_details(list(range(1, 7)), factory=factory)
