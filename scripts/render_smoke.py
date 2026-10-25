"""Render actual Conky windows inside Xvfb; never run against a personal desktop."""

import argparse
import calendar
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--profile", choices=["full", "compact"], default="full")
    parser.add_argument("--density", choices=["complete", "comfortable"], default="complete")
    parser.add_argument("--palette", default="blue")
    parser.add_argument("--font", choices=["ubuntu", "dejavu", "liberation"], default="ubuntu")
    parser.add_argument("--language", choices=["en", "es"], default="en")
    parser.add_argument("--detail-level", choices=["essential", "full"], default="full")
    options = parser.parse_args()
    if os.environ.get("CORTEX_NEO_HEADLESS_TEST") != "1":
        parser.error(
            "Use CORTEX_NEO_HEADLESS_TEST=1 xvfb-run -a python scripts/render_smoke.py ..."
        )
    # PyGObject can initialize a default display while importing Gdk overrides.
    # Force the test backend before that import, not only before Gdk.init().
    os.environ["GDK_BACKEND"] = "x11"
    os.environ.pop("WAYLAND_DISPLAY", None)
    os.environ["GDK_SCALE"] = "1"
    os.environ["GDK_DPI_SCALE"] = "1"
    import gi

    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk

    # A real host may expose WAYLAND_DISPLAY over SSH. Select Xvfb before the
    # first GDK initialization, or its default root can refer to another display.
    Gdk.set_allowed_backends("x11")

    from cortex_neo.conky import capabilities
    from cortex_neo.display import monitor_area
    from cortex_neo.io import atomic, lua
    from cortex_neo.layout import calculate
    from cortex_neo.render import generate
    from cortex_neo.supervisor import stop_children

    Gdk.init([])
    display = Gdk.Display.get_default()
    area, _ = monitor_area()
    assert area[2] > 0 and area[3] > 0, "Production display discovery failed"
    root = display.get_default_screen().get_root_window()
    processes = []
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        logs = (directory / "conky.log").open("w+")
        try:
            for command in (["openbox", "--sm-disable"], ["xcompmgr"]):
                processes.append(subprocess.Popen(command, stdout=logs, stderr=logs))
            time.sleep(1)
            if shutil.which("xsetroot"):
                subprocess.run(["xsetroot", "-solid", "#050B14"], check=True)
            before = bytes(Gdk.pixbuf_get_from_window(root, 0, 0, 1920, 1080).get_pixels())
            snapshot = {
                "sampled_at": time.time(),
                "hostname": "fixture-host",
                "os": {"name": "Linux fixture", "kernel": "test-kernel", "arch": "x86_64"},
                "hardware": {
                    "cpu_model": "Fixture CPU",
                    "cpu_topology": "8 cores / 16 threads",
                    "cpu_threads": 16,
                    "ram_model": "Fixture memory",
                    "ram_type": "DDR4",
                    "ram_speed": "3200 MT/s",
                },
                "cpu": {
                    "load": 25,
                    "top": [
                        {"pid": n, "name": f"fixture-process-{n}", "percent": n} for n in range(5)
                    ],
                },
                "ram": {
                    "load": 40,
                    "used": 4e9,
                    "total": 10e9,
                    "top": [{"name": f"fixture-app-{n}", "rss": 500e6} for n in range(5)],
                },
                "gpu": {"model": "Fixture GPU", "load": 20},
                "disks": [
                    {
                        "model": "Fixture SSD",
                        "target": "/",
                        "load": 15,
                        "used": 15e9,
                        "total": 100e9,
                    }
                ],
                "software": [
                    {
                        "label": "Python",
                        "version": "3.14",
                        "group": "Languages",
                        "detail": "CPython fixture build",
                    },
                    {
                        "label": "Rust",
                        "version": "1.99",
                        "group": "Languages",
                        "detail": "LLVM fixture build",
                    },
                ],
                "network": {"interface": "eth0", "rx": 100, "tx": 50},
                "calendar": {
                    "year": 2026,
                    "month": 10,
                    "day": 24,
                    "weeks": calendar.monthcalendar(2026, 10),
                },
                "weather": {
                    "location": {"name": "Ciudad manual de prueba"},
                    "status": "current",
                    "current": {"temperature_2m": 20, "weather_code": 3},
                    "local_date": "2026-10-24",
                    "days": [
                        {
                            "date": f"2026-10-{day}",
                            "temperature_2m_min": 14,
                            "temperature_2m_max": 24,
                            "weather_code": 3,
                            "precipitation_probability_max": 30,
                        }
                        for day in range(24, 31)
                    ],
                },
            }
            atomic(directory / "dashboard.lua", "return " + lua(snapshot))
            banner = subprocess.check_output(["conky", "--version"], text=True)
            plan = calculate(area, snapshot, profile=options.profile, density=options.density)
            from cortex_neo.palettes import PALETTES

            if options.palette not in PALETTES:
                parser.error("Unknown palette")
            plan.update(
                theme={"palette": options.palette},
                font=options.font,
                language=options.language,
                detail_level=options.detail_level,
            )
            generation = generate(plan, snapshot, capabilities(banner))
            environment = {
                **os.environ,
                "CORTEX_NEO_CACHE_DIR": str(directory),
                "CORTEX_NEO_THEME_DIR": str(SOURCE / "theme"),
                "CORTEX_NEO_UI_FILE": str(generation / "ui.lua"),
            }
            for path in generation.glob("*.conf"):
                processes.append(
                    subprocess.Popen(
                        ["conky", "-c", str(path)], env=environment, stdout=logs, stderr=logs
                    )
                )
            for _ in range(5):
                snapshot["sampled_at"] = time.time()
                atomic(directory / "dashboard.lua", "return " + lua(snapshot))
                time.sleep(1)
            assert all(p.poll() is None for p in processes), "A graphical test process exited"
            image = Gdk.pixbuf_get_from_window(root, 0, 0, 1920, 1080)
            after = bytes(image.get_pixels())
            changed = sum(a != b for a, b in zip(before, after, strict=True))
            if changed <= 10000:
                options.output.parent.mkdir(parents=True, exist_ok=True)
                image.savev(str(options.output.with_suffix(".failed.png")), "png", [], [])
                logs.flush()
                logs.seek(0)
                tree = subprocess.run(
                    ["xwininfo", "-root", "-tree"], capture_output=True, text=True, check=False
                )
                options.output.with_suffix(".failed.log").write_text(
                    logs.read()
                    + "\n"
                    + tree.stdout
                    + "\nGDK="
                    + display.get_name()
                    + " DISPLAY="
                    + os.environ.get("DISPLAY", ""),
                    encoding="utf-8",
                )
            assert changed > 10000, f"Desktop remained blank: {changed} changed bytes"
            # Each mapped card must contribute visible content, not just an empty window.
            for name, box in plan["cards"].items():
                x, y = round(plan["x"] + box["x"]), round(plan["y"] + box["y"])
                crop = image.new_subpixbuf(x, y, round(box["w"]), round(box["h"]))
                body = crop.new_subpixbuf(16, 60, crop.get_width() - 32, crop.get_height() - 76)
                colors = bytes(body.get_pixels())
                assert len(set(colors)) > 20, f"Blank or monochrome card: {name}"
            logs.flush()
            logs.seek(0)
            text = logs.read()
            for error in ("llua_do_call", "llua_load", "Syntax error", "unknown setting"):
                assert error.lower() not in text.lower(), text
            options.output.parent.mkdir(parents=True, exist_ok=True)
            image.savev(str(options.output), "png", [], [])
            print(
                json.dumps(
                    {
                        "cards": len(plan["cards"]),
                        "changed_bytes": changed,
                        "conky": capabilities(banner)["version"],
                        "capture": str(options.output),
                        "palette": options.palette,
                        "font": options.font,
                        "language": options.language,
                        "detail_level": options.detail_level,
                        "resolution": [1920, 1080],
                        "desktop_scale": 1,
                    }
                )
            )
        finally:
            stop_children(processes)
            logs.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
