"""Bounded measurement of collector work and this user's own dashboard processes."""

import subprocess
import time

import psutil


class CycleMetrics:
    """Time providers even when they fail; publication is outside this sampling span."""

    def __init__(self, interval, clock=time.perf_counter):
        self.clock = clock
        self.started = clock()
        self.interval = interval
        self.providers = {}

    def call(self, name, function, *args, **kwargs):
        started = self.clock()
        try:
            return function(*args, **kwargs)
        finally:
            self.providers[name] = round((self.clock() - started) * 1000, 3)

    def finish(self):
        elapsed = self.clock() - self.started
        return {
            "sample_ms": round(elapsed * 1000, 3),
            "providers_ms": dict(self.providers),
            "interval_ms": self.interval * 1000,
            "overrun": elapsed > self.interval,
        }


def process_delta(before, after, seconds, logical_cpus):
    """Use PID plus birth time so a reused PID never contributes another task's CPU."""
    if seconds <= 0 or logical_cpus < 1:
        raise ValueError("Measurement interval and logical CPU count must be positive")
    common = before.keys() & after.keys()
    cpu = sum(max(0, after[key][0] - before[key][0]) for key in common)
    core = round(cpu / seconds * 100, 3) if common else None
    return {
        "cpu_core_percent": core,
        "cpu_machine_percent": round(core / logical_cpus, 3) if core is not None else None,
        "rss_bytes": sum(value[1] for value in after.values()),
        "processes": len(after),
        "memory_measure": "sum RSS; includes shared pages and can double count them",
    }


def own_roots():
    roots = []
    for unit in ("cortex-neo", "cortex-neo-metrics"):
        try:
            result = subprocess.run(
                ["systemctl", "--user", "show", unit, "-p", "MainPID", "--value"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            if result.returncode == 0 and int(result.stdout.strip() or 0) > 0:
                roots.append(int(result.stdout.strip()))
        except (OSError, ValueError, subprocess.SubprocessError):
            continue
    return roots


def process_sample(roots):
    values = {}
    for pid in roots:
        try:
            root = psutil.Process(pid)
            processes = [root, *root.children(recursive=True)]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        for process in processes:
            try:
                with process.oneshot():
                    cpu = process.cpu_times()
                    values[(process.pid, process.create_time())] = (
                        cpu.user + cpu.system,
                        process.memory_info().rss,
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    return values


def profile(seconds=10, cache=None):
    """Observe only the two service process trees, without reading argv or environment."""
    if not 2 <= seconds <= 60:
        raise ValueError("Choose a measurement between 2 and 60 seconds")
    roots = own_roots()
    before = process_sample(roots)
    started = time.monotonic()
    peak_rss = sum(value[1] for value in before.values())
    peak_processes = len(before)
    while time.monotonic() - started < seconds:
        time.sleep(min(1, max(0, seconds - (time.monotonic() - started))))
        after = process_sample(roots)
        peak_rss = max(peak_rss, sum(value[1] for value in after.values()))
        peak_processes = max(peak_processes, len(after))
    elapsed = time.monotonic() - started
    result = process_delta(before, after, elapsed, psutil.cpu_count() or 1)
    result.update(
        available=bool(before and after),
        elapsed_seconds=round(elapsed, 3),
        peak_rss_bytes=peak_rss,
        peak_processes=peak_processes,
        logical_cpus=psutil.cpu_count() or 1,
        scope="cortex-neo user services and their current descendants",
        limitation="CPU counts identities present at both endpoints; short-lived tasks may be missed",
    )
    if cache is not None:
        result["payload_bytes"] = {}
        for name in ("dashboard.json", "dashboard.lua", "history.json"):
            try:
                result["payload_bytes"][name] = (cache / name).stat().st_size
            except OSError:
                continue
    return result
