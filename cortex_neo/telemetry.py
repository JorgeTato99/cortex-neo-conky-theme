"""One bounded sampler shared by every desktop card."""

import calendar
import fcntl
import json
import logging
import os
import shlex
import signal
import socket
import sys
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path

import psutil

from .docker import DockerMonitor
from .gpu import GPU
from .history import HistoryStore
from .io import atomic, command, finite_values, publish_snapshot, read, read_json
from .memory import MemoryMonitor
from .observability import CycleMetrics
from .paths import CACHE, STATE, ensure_directories
from .preferences import load_preferences
from .processes import read_processes
from .sharing import presentation_state
from .system import disk_inventory, docker_endpoints, inventory, mount_signature, mounts, ready
from .versions import installed_versions
from .weather import Weather

INTERVAL = 2
HISTORY_SECONDS = 240
LOG = logging.getLogger(__name__)


def operating_system():
    info = {}
    for line in read("/etc/os-release").splitlines():
        key, separator, value = line.partition("=")
        if separator:
            try:
                tokens = shlex.split(value)
            except ValueError:
                continue
            info[key] = tokens[0] if tokens else ""
    return {
        "name": info.get("PRETTY_NAME", "Linux"),
        "codename": info.get("VERSION", "").partition("(")[2].rstrip(")"),
        "kernel": os.uname().release,
        "arch": os.uname().machine,
        "signature": read("/proc/version_signature"),
        "compiled": read("/proc/sys/kernel/version"),
    }


def disk_samples(devices):
    result = []
    for device in devices:
        if device.get("type") != "disk":
            continue
        paths = mounts(device)
        item = {
            "name": device["name"],
            "model": device.get("model") or device["name"],
            "size": device.get("size", 0),
            "kind": "HDD" if device.get("rota") else "SSD",
            "transport": (device.get("tran") or "").upper(),
            "mounts": paths,
        }
        if paths:
            target = "/" if "/" in paths else paths[0]
            try:
                usage = psutil.disk_usage(target)
                item.update(used=usage.used, total=usage.total, load=usage.percent, target=target)
            except OSError:
                pass
        result.append(item)
    if not any("/" in item["mounts"] for item in result):
        # Containers and restricted desktops may expose the filesystem but no lsblk data.
        try:
            usage = psutil.disk_usage("/")
            result.append(
                dict(
                    name="root",
                    model="Sistema de archivos /",
                    kind="",
                    size=usage.total,
                    mounts=["/"],
                    used=usage.used,
                    total=usage.total,
                    load=usage.percent,
                    target="/",
                )
            )
        except OSError:
            pass
    return sorted(
        result,
        key=lambda item: ("/" not in item["mounts"], not item["mounts"], item["name"]),
    )


class DiskMonitor:
    """Keep expensive topology scans separate from cheap two-second usage reads."""

    def __init__(self):
        self.devices = []
        self.signature = None
        self.next_refresh = 0

    def sample(self, now):
        signature = mount_signature()
        if signature != self.signature or now >= self.next_refresh:
            self.devices = disk_inventory()
            self.signature = signature
            self.next_refresh = now + 30
        return disk_samples(self.devices)


def network_route():
    try:
        routes = json.loads(command(["ip", "-j", "route", "show", "default"]) or "[]")
        routes.sort(key=lambda route: route.get("metric", 0))
        interface = routes[0]["dev"]
        return {
            "interface": interface,
            "kind": "Wi-Fi"
            if (Path("/sys/class/net") / interface / "wireless").exists()
            else "Ethernet",
        }
    except (ValueError, TypeError, AttributeError, IndexError, KeyError):
        return {}


def cpu_temperature():
    try:
        for values in psutil.sensors_temperatures().values():
            for item in values:
                if item.label in ("Tctl", "Package id 0"):
                    return item.current
    except (AttributeError, OSError):
        pass
    return None


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ensure_directories()
    lock = (CACHE / "collector.lock").open("a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        LOG.error("A collector is already running for this user")
        return 75
    hardware = inventory()
    gpu_reader = GPU(hardware.get("gpu_model", ""))
    weather = Weather()
    weather.start()
    history = deque(maxlen=121)
    previous_history = read_json(CACHE / "history.json", [])
    for point in previous_history if isinstance(previous_history, list) else []:
        if (
            isinstance(point, dict)
            and isinstance(point.get("time"), (float, int))
            and 0 <= time.time() - point["time"] < HISTORY_SECONDS
        ):
            history.append(point)
    previous = read_json(CACHE / "dashboard.json", {})
    previous = previous if isinstance(previous, dict) else {}
    old_software = previous.get("software", [])
    software = {
        "items": old_software if isinstance(old_software, list) else [],
        "ready": False,
        "observed_at": previous.get("software_observed_at"),
    }

    def refresh_versions():
        try:
            software["items"] = installed_versions()
            software["observed_at"] = time.time()
            software["ready"] = True
        except Exception:
            # An inventory bug must not take live CPU/RAM metrics down with it.
            LOG.exception("Version inventory failed; retaining the previous valid inventory")

    worker = threading.Thread(target=refresh_versions, name="versions", daemon=True)
    worker.start()
    disk_monitor = DiskMonitor()
    memory_monitor = MemoryMonitor()
    docker_monitor = DockerMonitor()
    long_history = HistoryStore(STATE, hours=load_preferences()["history_hours"])
    next_history_settings = 0
    stopping = False

    def request_stop(_signal, _frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    containers, route = {}, {}
    next_docker = next_route = next_os = next_history = 0
    next_versions = time.monotonic() + 3600
    endpoints = {}
    os_info = operating_system()
    psutil.cpu_percent(None)
    read_processes()
    last_network = psutil.net_io_counters(pernic=True)
    last_time = time.monotonic()
    first = True
    while not stopping:
        start, now = time.monotonic(), time.time()
        cycle = CycleMetrics(INTERVAL)
        if start >= next_history_settings:
            long_history.hours = load_preferences()["history_hours"]
            next_history_settings = start + 30
        if start >= next_docker:
            endpoints = docker_endpoints()
            cycle.call("docker_schedule", docker_monitor.refresh, endpoints)
            next_docker = start + 15
        containers = docker_monitor.snapshot()
        if start >= next_route:
            route, next_route = network_route(), start + 15
        if start >= next_os:
            os_info, next_os = operating_system(), start + 60
        if start >= next_versions and not worker.is_alive():
            worker = threading.Thread(target=refresh_versions, name="versions", daemon=True)
            worker.start()
            next_versions = start + 3600
        cpu = psutil.cpu_percent(None) if not first else None
        memory = cycle.call("memory", psutil.virtual_memory)
        memory_signals = cycle.call("memory_pressure", memory_monitor.sample, memory, start)
        cpu_top, memory_top = cycle.call("processes", read_processes)
        gpu = cycle.call("gpu", gpu_reader.sample)
        disks = cycle.call("storage", disk_monitor.sample, start)
        current_network = psutil.net_io_counters(pernic=True)
        interface = route.get("interface", "")
        old, current = last_network.get(interface), current_network.get(interface)
        elapsed = max(0.001, start - last_time)
        network = dict(route)
        if old and current and not first:
            network.update(
                rx=max(0, current.bytes_recv - old.bytes_recv) / elapsed,
                tx=max(0, current.bytes_sent - old.bytes_sent) / elapsed,
            )
        last_network, last_time = current_network, start
        history.append(
            dict(
                time=now,
                cpu=cpu,
                ram=memory.percent,
                gpu=gpu.get("load"),
                vram=gpu.get("memory_load"),
                disks={d["name"]: d.get("load") for d in disks},
                available=memory.available,
                swap_used=(memory_signals.get("swap") or {}).get("used"),
                psi_memory=((memory_signals.get("pressure") or {}).get("some") or {}).get("avg10"),
                network_rx=network.get("rx"),
                network_tx=network.get("tx"),
                cpu_top=cpu_top if not first else [],
                ram_top=memory_top,
            )
        )
        cycle.call("history", long_history.record, history[-1])
        presentation = cycle.call("presentation", presentation_state)
        today = datetime.now()
        snapshot = dict(
            schema=5,
            sampled_at=now,
            hostname=socket.gethostname(),
            uptime=now - psutil.boot_time(),
            os=os_info,
            hardware=hardware,
            cpu=dict(load=cpu, temperature=cpu_temperature(), top=cpu_top if not first else []),
            ram=dict(
                load=memory.percent,
                used=memory.total - memory.available,
                total=memory.total,
                top=memory_top,
                **memory_signals,
            ),
            gpu=gpu,
            disks=disks,
            network=network,
            docker=containers,
            docker_available=bool(endpoints),
            docker_contexts=list(endpoints),
            software=list(software["items"]),
            software_ready=software["ready"],
            software_observed_at=software["observed_at"],
            presentation=presentation,
            collector=cycle.finish(),
            history_status=dict(
                recording_enabled=bool(long_history.hours),
                retained_minutes=len(long_history.minutes),
                write_failed=long_history.write_failed,
            ),
            history=list(history),
            weather=weather.snapshot(),
            calendar=dict(
                year=today.year,
                month=today.month,
                day=today.day,
                weeks=calendar.monthcalendar(today.year, today.month),
            ),
        )
        snapshot = finite_values(snapshot)
        publish_snapshot(CACHE, snapshot)
        if start >= next_history:
            atomic(
                CACHE / "history.json", json.dumps(finite_values(list(history)), allow_nan=False)
            )
            next_history = start + 30
        if first:
            ready()
            first = False
        if "--once" in sys.argv:
            long_history.flush(force=True)
            return 0
        time.sleep(max(0.1, INTERVAL - (time.monotonic() - start)))
    long_history.flush(force=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
