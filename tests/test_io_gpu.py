"""Unavailable commands, corrupt data and non-NVIDIA hardware are ordinary states."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cortex_neo.gpu import GPU, sensor
from cortex_neo.io import atomic, command, finite_values, lua, read_json, safe


class IOTests(unittest.TestCase):
    def test_commands_missing_failing_and_timed_out(self):
        self.assertIsNone(command(["/does/not/exist"]))
        self.assertIsNone(command([sys.executable, "-c", "raise SystemExit(1)"]))
        self.assertIsNone(
            command([sys.executable, "-c", "import time; time.sleep(1)"], timeout=0.03)
        )
        self.assertEqual(
            command(
                [sys.executable, "-c", 'print("partial"); raise SystemExit(1)'], accepted=(0, 1)
            ),
            "partial",
        )

    def test_atomic_json_and_numeric_sanitization(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "snapshot.json"
            value = finite_values({"load": float("nan"), "other": [float("inf"), 1]})
            atomic(path, json.dumps(value, allow_nan=False))
            self.assertEqual(read_json(path), {"load": None, "other": [None, 1]})
            path.write_text("{")
            self.assertEqual(read_json(path, {}), {})
            self.assertFalse(list(Path(folder).glob("*.tmp")))
        self.assertEqual(lua(float("nan")), "nil")
        self.assertNotIn("$", safe("${exec unsafe}"))

    def test_version_probes_disable_toolchain_downloads(self):
        value = command(
            [
                sys.executable,
                "-c",
                'import os; print(os.environ["RUSTUP_AUTO_INSTALL"],os.environ["GOTOOLCHAIN"])',
            ]
        )
        self.assertEqual(value, "0 local")

    def test_intel_frequency_is_not_utilization(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            card = root / "card1"
            (card / "device").mkdir(parents=True)
            (card / "device/vendor").write_text("0x8086")
            (card / "gt_cur_freq_mhz").write_text("400")
            (card / "gt_max_freq_mhz").write_text("1300")
            with patch("cortex_neo.gpu.nvml", None):
                result = GPU("Intel Iris Xe", root).sample()
            self.assertEqual(result["frequency"], 400)
            self.assertNotIn("load", result)
            (card / "gt_cur_freq_mhz").write_text("nan")
            self.assertIsNone(sensor(card / "gt_cur_freq_mhz"))

    def test_no_gpu_no_optional_metrics(self):
        with tempfile.TemporaryDirectory() as folder, patch("cortex_neo.gpu.nvml", None):
            self.assertEqual(GPU("", Path(folder)).sample(), {})
