"""Opt-in task measurement with inherited output and owned process cancellation."""

import argparse
import errno
import math
import os
import signal
import subprocess
import sys
import time

import psutil

from .i18n import tr
from .io import safe
from .observability import process_sample
from .paths import STATE
from .records import new_identifier, read_records, save_record


def _known_alive(process, identities):
    if process.poll() is None:
        return True
    for pid, created in identities:
        try:
            item = psutil.Process(pid)
            if (
                item.create_time() == created
                and item.status() != psutil.STATUS_ZOMBIE
                and os.getpgid(pid) == process.pid
            ):
                return True
        except (OSError, psutil.Error):
            continue
    return False


def _stop_owned(process, identities):
    """Never signal by executable name or an unverified reused process identity."""
    if _known_alive(process, identities):
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass
        deadline = time.monotonic() + 2
        while _known_alive(process, identities) and time.monotonic() < deadline:
            time.sleep(0.03)
        if _known_alive(process, identities):
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        return False
    deadline = time.monotonic() + 1
    while _known_alive(process, identities) and time.monotonic() < deadline:
        time.sleep(0.02)
    return not _known_alive(process, identities)


def run_task(
    argv,
    *,
    label="",
    timeout=None,
    state=STATE,
    sample_interval=0.2,
    max_records=10,
    sleeper=time.sleep,
):
    if (
        not isinstance(argv, (list, tuple))
        or not argv
        or not argv[0]
        or any(not isinstance(arg, str) or "\x00" in arg for arg in argv)
    ):
        raise ValueError("Choose a command with string arguments and no NUL characters")
    if timeout is not None and (
        not isinstance(timeout, (int, float))
        or isinstance(timeout, bool)
        or not math.isfinite(timeout)
        or not 0.1 <= timeout <= 604800
    ):
        raise ValueError("Task timeout must be 0.1 seconds to seven days")
    if (
        not 0.01 <= sample_interval <= 2
        or not isinstance(max_records, int)
        or isinstance(max_records, bool)
        or not 1 <= max_records <= 50
    ):
        raise ValueError("Invalid sampling interval or retention limit")
    started, wall = time.monotonic(), time.time()
    identities = {}
    peak_rss = None
    truncated = False
    status = "completed"
    cleanup_complete = True
    launch_errno = None
    returncode = None
    outlived = False
    try:
        process = subprocess.Popen(list(argv), start_new_session=True)
    except OSError as error:
        launch_errno = error.errno
        status = "launch_failed"
        exit_code = (
            127 if error.errno == errno.ENOENT else (126 if error.errno == errno.EACCES else 125)
        )
    else:
        try:
            while process.poll() is None:
                sample = process_sample([process.pid])
                if sample:
                    peak_rss = max(peak_rss or 0, sum(value[1] for value in sample.values()))
                for identity, (cpu, _rss) in sample.items():
                    if identity in identities or len(identities) < 4096:
                        identities[identity] = max(identities.get(identity, 0), cpu)
                    else:
                        truncated = True
                if timeout is not None and time.monotonic() - started >= timeout:
                    status = "timed_out"
                    cleanup_complete = _stop_owned(process, identities)
                    break
                sleeper(sample_interval)
        except KeyboardInterrupt:
            status = "interrupted"
            cleanup_complete = _stop_owned(process, identities)
        except BaseException:
            _stop_owned(process, identities)
            raise
        returncode = process.poll()
        if status == "timed_out":
            exit_code = 124
        elif status == "interrupted":
            exit_code = 130
        else:
            returncode = process.wait()
            exit_code = returncode if returncode >= 0 else 128 - returncode
            status = "completed" if exit_code == 0 else "failed"
        outlived = _known_alive(process, identities)
    elapsed = max(0.000001, time.monotonic() - started)
    cpu = sum(identities.values()) if identities else None
    record = {
        "kind": "cortex-neo-task",
        "format_version": 1,
        "id": new_identifier(wall),
        "label": safe(label or "tarea")[:80],
        "started_at": wall,
        "elapsed_seconds": round(elapsed, 4),
        "status": status,
        "exit_code": exit_code,
        "process_returncode": returncode,
        "launch_errno": launch_errno,
        "observed_cpu_seconds": cpu,
        "cpu_machine_percent_observed": round(cpu / elapsed / (psutil.cpu_count() or 1) * 100, 3)
        if cpu is not None
        else None,
        "peak_rss_bytes": peak_rss,
        "tracked_identities": len(identities),
        "identities_truncated": truncated,
        "cleanup_complete": cleanup_complete,
        "cleanup_requested": status in ("timed_out", "interrupted"),
        "known_descendants_outlived_parent": outlived,
        "observation_limits": "RSS includes shared pages; short-lived or detached descendants and work in external daemons may be missed",
    }
    save_record(state / "tasks", record, "cortex-neo-task", limit=max_records)
    return record


def list_tasks(*, state=STATE):
    return read_records(state / "tasks", "cortex-neo-task")


def run_cli(argv):
    parser = argparse.ArgumentParser(
        prog="cortex-neo run",
        description=tr("Measure a command while preserving its output and exit code."),
    )
    parser.add_argument("--label", default="")
    parser.add_argument("--timeout", type=float)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    options = parser.parse_args(argv)
    command = options.command
    if command and command[0] == "--":
        command = command[1:]
    try:
        result = run_task(command, label=options.label, timeout=options.timeout)
    except ValueError as error:
        parser.error(str(error))
    print(
        tr("CORTEX · {p0} · {p1} · exit {p2} · {p3:.2f} s").format(
            p0=result["id"],
            p1=result["status"],
            p2=result["exit_code"],
            p3=result["elapsed_seconds"],
        ),
        file=sys.stderr,
    )
    return result["exit_code"]
