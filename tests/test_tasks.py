"""Measure real commands while preserving exit codes and owning cancellation."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from itertools import count
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import psutil

from cortex_neo.tasks import list_tasks, run_task


class TaskTests(unittest.TestCase):
    def test_denied_cancellation_reports_incomplete_cleanup_without_escalation(self):
        ticks = count(0, 0.25)

        def wait(**_):
            raise subprocess.TimeoutExpired("fake", 2)

        process = SimpleNamespace(pid=999999, poll=lambda: None, wait=wait)
        with (
            tempfile.TemporaryDirectory() as directory,
            patch("cortex_neo.tasks.subprocess.Popen", return_value=process),
            patch("cortex_neo.tasks.process_sample", return_value={}),
            patch("cortex_neo.tasks.os.killpg", side_effect=PermissionError),
            patch("cortex_neo.tasks.time.monotonic", side_effect=lambda: next(ticks)),
            patch("cortex_neo.tasks.time.sleep"),
        ):
            record = run_task(["fake"], timeout=0.1, state=Path(directory))
            self.assertEqual(record["exit_code"], 124)
            self.assertFalse(record["cleanup_complete"])
            self.assertTrue(record["known_descendants_outlived_parent"])

    def test_exit_code_resources_and_no_argument_or_environment_logging(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            with patch.dict(os.environ, {"CORTEX_TEST_PRIVATE": "PRIVATE-ENV"}):
                record = run_task(
                    [
                        sys.executable,
                        "-c",
                        "import time,sys; time.sleep(0.08); sys.exit(3) # PRIVATE-ARGUMENT",
                    ],
                    label="suite",
                    state=state,
                    sample_interval=0.02,
                )
            self.assertEqual(record["exit_code"], 3)
            self.assertEqual(record["status"], "failed")
            self.assertGreater(record["elapsed_seconds"], 0)
            self.assertGreater(record["peak_rss_bytes"], 0)
            self.assertNotIn("PRIVATE-ARGUMENT", json.dumps(list_tasks(state=state)))
            self.assertNotIn("PRIVATE-ENV", json.dumps(list_tasks(state=state)))
            self.assertNotIn("argv", json.dumps(record))
            self.assertNotIn("environment", json.dumps(record))

    def test_timeout_stops_owned_group_but_preserves_an_unrelated_process(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            child_pid_file = state / "child.pid"
            outsider = subprocess.Popen(
                [sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True
            )
            code = "import pathlib,subprocess,sys,time; p=subprocess.Popen([sys.executable,'-c','import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(30)']); pathlib.Path(sys.argv[1]).write_text(str(p.pid)); time.sleep(30)"
            try:
                record = run_task(
                    [sys.executable, "-c", code, str(child_pid_file)],
                    timeout=0.6,
                    state=state,
                    sample_interval=0.03,
                )
                self.assertEqual(record["exit_code"], 124)
                self.assertEqual(record["status"], "timed_out")
                self.assertIsNone(outsider.poll())
                pid = int(child_pid_file.read_text())
                self.assertTrue(
                    not psutil.pid_exists(pid)
                    or psutil.Process(pid).status() == psutil.STATUS_ZOMBIE
                )
            finally:
                outsider.terminate()
                outsider.wait(3)

    def test_interrupt_launch_failure_and_retention(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)

            def interrupt(_):
                raise KeyboardInterrupt

            record = run_task(
                [sys.executable, "-c", "import time; time.sleep(30)"],
                state=state,
                sleeper=interrupt,
            )
            self.assertEqual(record["exit_code"], 130)
            missing = run_task(["__cortex_missing_program__"], state=state, max_records=1)
            self.assertEqual(missing["exit_code"], 127)
            self.assertEqual(missing["status"], "launch_failed")
            self.assertEqual(len(list_tasks(state=state)), 1)
            path = state / "tasks" / (missing["id"] + ".json")
            path.write_text('{"kind":"cortex-neo-task"}')
            self.assertEqual(list_tasks(state=state), [])
            with self.assertRaises(ValueError):
                run_task([], state=state)
