"""Exercise real filesystem transactions; replace only external process execution."""

import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import manage_installation as installer


@unittest.skipUnless(os.name == "posix", "Linux filesystem installation contract")
class InstallationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.paths = installer.Paths.for_user(self.root / "hogar con espacios", {})
        self.calls = []
        self.available = False
        self.active = False
        self.fail_restart = False
        self.addCleanup(patch.stopall)
        patch("sys.stdout", new=io.StringIO()).start()

    def command(self, argv, *, check=True):
        self.calls.append(argv)
        if "show-environment" in argv:
            return 0 if self.available else 1
        if "is-active" in argv:
            return 0 if self.active else 1
        if "restart" in argv and self.fail_restart:
            raise RuntimeError("Injected activation failure")
        return 0

    def prepare(self, source, release, command):
        release.mkdir()
        (release / installer.MARKER).write_text(json.dumps({"project": "cortex-neo"}))
        for name in ("config", "systemd", "cortex_neo", "theme", "venv"):
            (release / name).mkdir()
        for name in ("settings", "location"):
            (release / f"config/{name}.example.json").write_text('{"example": true}')
        for name in ("cortex-neo", "cortex-neo-metrics"):
            (release / f"systemd/{name}.service").write_text(
                (installer.SOURCE / f"systemd/{name}.service").read_text()
            )

    def install(self, *args):
        installer.install(
            self.paths, installer.arguments(list(args)), command=self.command, prepare=self.prepare
        )

    def test_clean_install_and_reinstall_keep_one_enabled_service_and_settings(self):
        self.install("--no-start")
        first = self.paths.target.resolve()
        settings = self.paths.config / "settings.json"
        settings.write_text('{"personal": true}')
        theme = self.paths.config / "theme.json"
        theme.write_text('{"palette":"amber","opacity":0.9}')
        self.install("--no-start")
        self.assertNotEqual(self.paths.target.resolve(), first)
        self.assertEqual(settings.read_text(), '{"personal": true}')
        self.assertEqual(theme.read_text(), '{"palette":"amber","opacity":0.9}')
        self.assertEqual(
            len(list((self.paths.units / "graphical-session.target.wants").iterdir())), 1
        )
        self.assertEqual(len(list(self.paths.applications.glob("*.desktop"))), 1)
        self.assertNotIn("restart", sum(self.calls, []))
        self.assertTrue(first.is_dir())

    def test_dependency_failure_never_stops_or_replaces_existing_release(self):
        self.install("--no-start")
        original = self.paths.target.resolve()
        self.calls.clear()
        self.available = self.active = True

        def failure(source, release, command):
            self.prepare(source, release, command)
            raise RuntimeError("Injected download failure")

        with self.assertRaisesRegex(RuntimeError, "download"):
            installer.install(
                self.paths, installer.arguments([]), command=self.command, prepare=failure
            )
        self.assertEqual(self.paths.target.resolve(), original)
        self.assertNotIn("stop", sum(self.calls, []))
        self.assertEqual(len(list(self.paths.releases.iterdir())), 1)

    def test_activation_failure_restores_release_environment_controls_and_config(self):
        self.install("--no-start")
        original = self.paths.target.resolve()
        marker = original / "venv/keep-this-environment"
        marker.write_text("original dependencies")
        before = {str(p): installer.fingerprint(p) for p in installer.controls(self.paths)}
        self.available = self.active = self.fail_restart = True
        with self.assertRaisesRegex(RuntimeError, "activation"):
            self.install()
        self.assertEqual(self.paths.target.resolve(), original)
        self.assertEqual(marker.read_text(), "original dependencies")
        self.assertEqual(
            before, {str(p): installer.fingerprint(p) for p in installer.controls(self.paths)}
        )
        self.assertIn(
            ["systemctl", "--user", "start", "cortex-neo.service", "cortex-neo-metrics.service"],
            self.calls,
        )

    def test_failed_first_activation_removes_new_controls_and_configuration(self):
        self.available = self.fail_restart = True
        with self.assertRaises(RuntimeError):
            self.install()
        self.assertFalse(self.paths.target.exists())
        self.assertFalse(any(p.exists() or p.is_symlink() for p in installer.controls(self.paths)))
        self.assertFalse((self.paths.config / "location.json").exists())

    def test_failed_atomic_switch_does_not_remove_the_old_target(self):
        self.install("--no-start")
        original = self.paths.target.resolve()
        with patch.object(installer.os, "replace", side_effect=OSError("Injected rename failure")):
            with self.assertRaises(OSError):
                self.install("--no-start")
        self.assertEqual(self.paths.target.resolve(), original)
        self.assertFalse(list(self.paths.target.parent.glob("cortex-neo.next-*")))

    def test_uninstall_preserves_personal_data_and_edited_controls(self):
        self.install("--no-start")
        (self.paths.cache / "history.json").write_text("history")
        shortcut = self.paths.applications / "cortex-neo.desktop"
        shortcut.write_text("personal shortcut")
        installer.uninstall(self.paths, self.command)
        self.assertFalse(self.paths.target.is_symlink())
        self.assertTrue((self.paths.config / "settings.json").is_file())
        self.assertEqual((self.paths.cache / "history.json").read_text(), "history")
        self.assertEqual(shortcut.read_text(), "personal shortcut")
        self.assertFalse(list(self.paths.releases.iterdir()))
        self.assertTrue(any((self.paths.state / "backups").iterdir()))

    def test_foreign_target_and_release_symlinks_are_rejected(self):
        outside = self.root / "foreign"
        outside.mkdir()
        (outside / "keep").write_text("data")
        self.paths.target.parent.mkdir(parents=True)
        self.paths.target.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            self.install("--no-start")
        self.paths.releases.mkdir()
        link = self.paths.releases / "link"
        link.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            installer.remove_release(link, self.paths.releases)
        self.assertEqual((outside / "keep").read_text(), "data")

    def test_legacy_directory_migration_removes_only_owned_old_shortcut(self):
        (self.paths.target / "cortex_neo").mkdir(parents=True)
        (self.paths.target / "theme").mkdir()
        (self.paths.target / "cortex_neo/__main__.py").touch()
        (self.paths.target / "theme/formatter.lua").touch()
        self.paths.applications.mkdir(parents=True)
        old = self.paths.applications / "conky.desktop"
        old.write_text("Name=Conky CÓRTEX NEO\n")
        self.install("--no-start")
        self.assertFalse(old.exists())
        self.assertTrue(self.paths.target.is_symlink())
        self.assertTrue(any(p.name.startswith("legacy-") for p in self.paths.releases.iterdir()))

    def test_no_start_refuses_to_replace_an_active_installation(self):
        self.install("--no-start")
        self.available = self.active = True
        original = self.paths.target.resolve()
        with self.assertRaises(RuntimeError):
            self.install("--no-start")
        self.assertEqual(self.paths.target.resolve(), original)

    def test_dry_run_never_installs_packages_or_creates_home(self):
        with (
            patch.object(installer.Paths, "for_user", return_value=self.paths),
            patch.object(
                installer.platform,
                "freedesktop_os_release",
                return_value={"ID": "ubuntu", "VERSION_ID": "24.04"},
            ),
            patch.object(installer, "run", side_effect=AssertionError("must not run")),
        ):
            self.assertEqual(installer.main(["--dry-run"]), 0)
        self.assertFalse(self.paths.home.exists())

    def test_supported_profiles_and_unsupported_or_older_python(self):
        for distribution, versions in installer.PROFILES.items():
            for version in versions:
                packages = installer.package_plan({"ID": distribution, "VERSION_ID": version})
                self.assertIn("conky-all", packages)
                self.assertIn("python3-gi", packages)
        with self.assertRaises(RuntimeError):
            installer.package_plan({"ID": "ubuntu", "VERSION_ID": "22.04"})
        with (
            patch.object(installer.sys, "version_info", (3, 10, 22)),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(installer.main(["--dry-run"]), 78)

    def test_xdg_roots_and_literal_shell_paths_are_preserved(self):
        paths = installer.Paths.for_user(
            self.paths.home,
            {
                "XDG_DATA_HOME": str(self.root / "datos 100%"),
                "XDG_CONFIG_HOME": "relative/ignored",
            },
        )
        self.assertEqual(paths.target, self.root / "datos 100%/cortex-neo")
        self.assertEqual(paths.config, self.paths.config)
        self.assertEqual(installer.quote_unit("100%"), "100%%")
        self.assertEqual(installer.unit_path("/path with spaces"), "/path with spaces")
        with self.assertRaises(RuntimeError):
            installer.unit_path("/bad\n[Service]")

    def test_concurrent_operations_are_rejected_and_lock_is_released(self):
        with installer.installation_lock(self.paths):
            with self.assertRaisesRegex(RuntimeError, "en curso"):
                with installer.installation_lock(self.paths):
                    self.fail("Concurrent operation acquired the lock")
        with installer.installation_lock(self.paths):
            self.assertTrue((self.paths.state / "installation.lock").is_file())

    def test_launcher_executes_literal_path_with_spaces(self):
        self.install("--no-start")
        interpreter = self.paths.target / "venv/bin/python"
        interpreter.parent.mkdir()
        interpreter.write_text(
            "#!/usr/bin/python3\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n"
        )
        interpreter.chmod(0o755)
        result = subprocess.check_output(
            [str(installer.controls(self.paths)[0]), "doctor"], text=True
        )
        self.assertEqual(json.loads(result), ["-I", "-m", "cortex_neo", "doctor"])
        unit = (self.paths.units / "cortex-neo.service").read_text()
        self.assertIn("WorkingDirectory=" + str(self.paths.target) + "\n", unit)

    def test_orphan_metrics_service_also_prevents_unsafe_no_start_update(self):
        self.install("--no-start")
        original = self.paths.target.resolve()

        def command(argv, *, check=True):
            if "show-environment" in argv:
                return 0
            if "is-active" in argv:
                return 0 if argv[-1] == "cortex-neo-metrics.service" else 1
            return 0

        with self.assertRaises(RuntimeError):
            installer.install(
                self.paths,
                installer.arguments(["--no-start"]),
                command=command,
                prepare=self.prepare,
            )
        self.assertEqual(self.paths.target.resolve(), original)
