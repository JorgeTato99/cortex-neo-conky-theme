"""Inspect the real mapped windows, alignment and current service health."""

import json
import re
import subprocess

from cortex_neo.display import import_session_environment, monitor_area
from cortex_neo.io import atomic, read_json
from cortex_neo.paths import CACHE, CONFIG, STATE


def main():
    import_session_environment()
    settings = read_json(CONFIG / "settings.json", {})
    area, factor = monitor_area(settings.get("monitor", "primary"))
    plan = read_json(CACHE / "layout.json", {})
    boxes = {}
    for name, expected in plan["cards"].items():
        text = subprocess.check_output(["xwininfo", "-name", "Cortex Neo - " + name], text=True)
        box = {
            key: int(re.search(pattern + r"\s*(-?\d+)", text).group(1))
            for key, pattern in [
                ("x", "Absolute upper-left X:"),
                ("y", "Absolute upper-left Y:"),
                ("w", "Width:"),
                ("h", "Height:"),
            ]
        }
        assert abs(box["h"] - round(expected["h"]) * factor) <= 2, (name, box, expected)
        assert box["x"] >= area[0] * factor - 2 and box["y"] >= area[1] * factor - 2, box
        assert box["x"] + box["w"] <= (area[0] + area[2]) * factor + 2, box
        assert box["y"] + box["h"] <= (area[1] + area[3]) * factor + 2, box
        boxes[name] = box
    for name, a in boxes.items():
        for other, b in boxes.items():
            if name >= other:
                continue
            assert not (
                min(a["x"] + a["w"], b["x"] + b["w"]) > max(a["x"], b["x"])
                and min(a["y"] + a["h"], b["y"] + b["h"]) > max(a["y"], b["y"])
            ), (name, other)
    for left, right in [("cpu", "ram"), ("gpu", "storage")]:
        if left in boxes and right in boxes:
            assert (
                boxes[left]["y"] == boxes[right]["y"] and boxes[left]["h"] == boxes[right]["h"]
            ), (left, right)
    services = {}
    for unit in ["cortex-neo", "cortex-neo-metrics"]:
        value = subprocess.check_output(
            [
                "systemctl",
                "--user",
                "show",
                unit,
                "-p",
                "ActiveState",
                "-p",
                "NRestarts",
                "-p",
                "MainPID",
            ],
            text=True,
        )
        services[unit] = dict(line.split("=", 1) for line in value.splitlines())
        assert services[unit]["ActiveState"] == "active" and services[unit]["NRestarts"] == "0", (
            services
        )
    result = dict(
        area=area,
        monitor_scale=factor,
        layout_scale=plan["scale"],
        font_adjustment=plan.get("font_adjustment", 1),
        boxes=boxes,
        services=services,
    )
    atomic(STATE / "desktop-verification.json", json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
