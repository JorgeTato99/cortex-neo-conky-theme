"""Discover newly mounted volumes without polling full topology every two seconds."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from cortex_neo.system import mount_signature
from cortex_neo.telemetry import DiskMonitor


class StorageTests(unittest.TestCase):
    def test_mount_signature_ignores_container_churn_but_tracks_block_mounts(self):
        root = "35 1 253:1 / / rw - ext4 /dev/mapper/root rw\n"
        container = "40 35 0:55 / /var/lib/docker/overlay rw - overlay overlay rw\n"
        dev = "50 35 253:2 / /srv/dev rw - ext4 /dev/mapper/devssd rw\n"
        with patch("cortex_neo.system.read", return_value=root):
            baseline = mount_signature()
        with patch("cortex_neo.system.read", return_value=root + container):
            self.assertEqual(mount_signature(), baseline)
        with patch("cortex_neo.system.read", return_value=root + dev):
            self.assertNotEqual(mount_signature(), baseline)

    def test_mount_and_unmount_refresh_before_periodic_deadline(self):
        root = dict(name="rootdisk", type="disk", mountpoints=["/"])
        dev = dict(name="devdisk", type="disk", mountpoints=[])
        mounted_dev = {**dev, "children": [dict(mountpoints=["/srv/dev"])]}
        usage = SimpleNamespace(used=10, total=100, percent=10)
        with (
            patch("cortex_neo.telemetry.mount_signature", return_value=("root",)) as signature,
            patch("cortex_neo.telemetry.disk_inventory", return_value=[root, dev]) as scan,
            patch("cortex_neo.telemetry.psutil.disk_usage", return_value=usage),
        ):
            monitor = DiskMonitor()
            self.assertNotIn("target", monitor.sample(0)[1])
            monitor.sample(2)
            monitor.sample(4)
            self.assertEqual(scan.call_count, 1)
            signature.return_value = ("root", "dev")
            scan.return_value = [root, mounted_dev]
            self.assertEqual(monitor.sample(6)[1]["target"], "/srv/dev")
            self.assertEqual(scan.call_count, 2)
            signature.return_value = ("root",)
            scan.return_value = [root, dev]
            self.assertNotIn("target", monitor.sample(8)[1])
            self.assertEqual(scan.call_count, 3)
            monitor.sample(36)
            self.assertEqual(scan.call_count, 3)
            monitor.sample(38)
            self.assertEqual(scan.call_count, 4)
