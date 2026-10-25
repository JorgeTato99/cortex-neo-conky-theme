"""Synthetic hardware and display partitions; these do not certify real GPUs."""

import itertools
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from cortex_neo.gpu import GPU
from cortex_neo.layout import calculate
from cortex_neo.system import inventory
from cortex_neo.telemetry import disk_samples

FIXTURE = json.loads((Path(__file__).parent / "fixtures/hardware.json").read_text())


class PortabilityTests(unittest.TestCase):
    def test_amd_intel_nvidia_without_driver_and_missing_sensor_files(self):
        with tempfile.TemporaryDirectory() as directory, patch("cortex_neo.gpu.nvml", None):
            for profile in FIXTURE["gpus"]:
                root = Path(directory) / profile["vendor"]
                card = root / "card0"
                files = {"device/vendor": profile["vendor"], **profile["sensors"]}
                for name, text in files.items():
                    path = card / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(text)
                result = GPU(profile["model"], root).sample()
                self.assertEqual(result["model"], profile["model"])
                if profile["vendor"] == "0x1002":
                    self.assertEqual(result["load"], 42)
                    self.assertEqual(result["memory_load"], 12.5)
                    self.assertEqual(result["temperature"], 63)
                elif profile["vendor"] == "0x8086":
                    self.assertEqual(result["frequency"], 450)
                    self.assertNotIn("load", result)
                else:
                    self.assertNotIn("load", result)
                    self.assertNotIn("memory_load", result)

    def test_encrypted_identical_ssds_and_unmounted_disks(self):
        usage = SimpleNamespace(used=10, total=100, percent=10)
        with patch("cortex_neo.telemetry.psutil.disk_usage", return_value=usage) as probe:
            samples = disk_samples(FIXTURE["blockdevices"])
        self.assertEqual([s.get("target") for s in samples], ["/", "/srv/dev", None])
        self.assertEqual(probe.call_count, 2)
        self.assertNotIn("load", samples[-1])
        with patch("cortex_neo.telemetry.psutil.disk_usage", side_effect=PermissionError):
            samples = disk_samples(FIXTURE["blockdevices"])
        self.assertTrue(all("load" not in item for item in samples))

    def test_denied_smbios_does_not_request_interactive_elevation(self):
        with (
            patch("cortex_neo.system.command", return_value=None) as command,
            patch("cortex_neo.system.read", return_value=""),
            patch("cortex_neo.system.glob.glob", return_value=[]),
            patch("cortex_neo.system.write"),
        ):
            data = inventory()
        self.assertEqual(data["ram_model"], "")
        self.assertEqual(data["ram_speed"], "")
        sudo = [call.args[0] for call in command.call_args_list if call.args[0][0] == "sudo"]
        self.assertEqual(sudo, [["sudo", "-n", "/usr/sbin/dmidecode", "--type", "17"]])

    def test_optional_card_combinations_fit_shifted_and_fractional_workareas(self):
        # Physical 1080p/125% and 1440p/166.67% share this logical desktop area.
        areas = [
            (67, 32, 1469, 832),
            (1536, 32, 1469, 832),
            (-1080, 32, 1080, 1888),
            (67, 32, 1213, 688),
            (67, 32, 3773, 2128),
        ]
        for enabled in itertools.product((False, True), repeat=5):
            gpu, disks, software, weather, network = enabled
            snapshot = {
                "gpu": {"model": "Fixture GPU"} if gpu else {},
                "disks": [{"model": "SSD"}] if disks else [],
                "software": [{"version": "1.0"}] if software else [],
                "weather": {"location": {"name": "Manual fixture"}} if weather else {},
                "network": {"interface": "eth0"} if network else {},
            }
            for area, weeks, multiplier in itertools.product(areas, (4, 5, 6), (0.5, 1)):
                with self.subTest(cards=enabled, area=area, weeks=weeks, multiplier=multiplier):
                    plan = calculate(area, snapshot, weeks, multiplier)
                    self.assertGreaterEqual(plan["x"], area[0])
                    self.assertLessEqual(plan["x"] + plan["width"], area[0] + area[2] + 0.01)
                    self.assertLessEqual(plan["y"] + plan["height"], area[1] + area[3] + 0.01)
                    cards = plan["cards"]
                    self.assertEqual(cards["cpu"]["h"], cards["ram"]["h"])
                    for left, right in itertools.combinations(cards.values(), 2):
                        x = min(left["x"] + left["w"], right["x"] + right["w"]) - max(
                            left["x"], right["x"]
                        )
                        y = min(left["y"] + left["h"], right["y"] + right["h"]) - max(
                            left["y"], right["y"]
                        )
                        self.assertFalse(x > 0.01 and y > 0.01)
