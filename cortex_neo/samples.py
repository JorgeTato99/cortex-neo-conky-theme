"""Small data-only timeline samples shared by incident and history tools."""

import math

from .io import safe

METRICS = (
    "cpu",
    "ram",
    "gpu",
    "vram",
    "available",
    "swap_used",
    "psi_memory",
    "network_rx",
    "network_tx",
)


def number(value):
    return (
        value
        if isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
        else None
    )


def compact_point(raw):
    if not isinstance(raw, dict) or number(raw.get("time")) is None:
        return None
    point = {"time": raw["time"], **{key: number(raw.get(key)) for key in METRICS}}
    for key in ("cpu", "ram", "gpu", "vram", "psi_memory"):
        if point[key] is not None and point[key] > 100:
            point[key] = None
    disks = raw.get("disks")
    point["disks"] = (
        {safe(key)[:32]: number(value) for key, value in list(disks.items())[:16]}
        if isinstance(disks, dict)
        else {}
    )
    for key, metric in (("cpu_top", "percent"), ("ram_top", "rss")):
        rows = raw.get(key)
        point[key] = []
        for row in rows[:5] if isinstance(rows, list) else []:
            if not isinstance(row, dict) or number(row.get(metric)) is None:
                continue
            item = {"name": safe(row.get("name"))[:64], metric: row[metric]}
            if row.get("scope") == "virtual-machine":
                item["scope"] = "virtual-machine"
            point[key].append(item)
    return point
