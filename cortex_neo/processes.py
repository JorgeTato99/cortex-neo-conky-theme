"""One process walk for CPU ranking and application RSS grouped by name."""

import psutil

from .io import safe


def read_processes(iterator=None):
    cpu, memory = [], {}
    iterator = (
        iterator
        if iterator is not None
        else psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"], ad_value=None)
    )
    for process in iterator:
        try:
            info = process.info
            name = safe(info.get("name") or "?")
            percent = info.get("cpu_percent")
            if percent is not None:
                cpu.append({"pid": info["pid"], "name": name, "percent": percent})
            usage = info.get("memory_info")
            if usage is not None:
                entry = memory.setdefault(name.casefold(), {"name": name, "rss": 0, "processes": 0})
                entry["rss"] += usage.rss
                entry["processes"] += 1
                if name.casefold().startswith("qemu-system-"):
                    entry["scope"] = "virtual-machine"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return (
        sorted(cpu, key=lambda p: (-p["percent"], p["pid"]))[:5],
        sorted(memory.values(), key=lambda p: (-p["rss"], p["name"]))[:5],
    )
