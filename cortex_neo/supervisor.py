"""Own the card processes and rebuild only when the screen/capabilities change."""

import logging
import os
import re
import shutil
import signal
import subprocess
import time

from .conky import capabilities
from .display import import_session_environment, monitor_area
from .io import read_json
from .layout import calculate, visible_cards
from .paths import CACHE, CONFIG, ROOT, ensure_directories
from .preferences import load_preferences
from .render import generate
from .sharing import presentation_file

LOG = logging.getLogger(__name__)
STOPPING = False


def stop_children(children):
    for child in children:
        if child.poll() is None:
            child.terminate()
    for child in children:
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()


def overflow(layout, monitor_scale):
    """Check natural Xft text height against the allocated rows after mapping."""
    for name, box in layout["cards"].items():
        try:
            result = subprocess.run(
                ["xwininfo", "-name", "Cortex Neo - " + name],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )
            match = re.search(r"Height:\s*(\d+)", result.stdout)
            if match and int(match[1]) > round(box["h"]) * monitor_scale + 2:
                return True
        except (OSError, subprocess.SubprocessError):
            return False
    return False


def launch(layout, snapshot, conky, monitor_scale, build=None):
    children = []
    generation = None
    # Integer Xft sizes can round up on smaller displays; verify actual windows.
    for attempt in range(4):
        layout["font_adjustment"] = 0.95**attempt
        generation = generate(layout, snapshot, build)
        try:
            presentation_path = str(presentation_file())
        except OSError:
            presentation_path = ""
        env = {
            **os.environ,
            "CORTEX_NEO_CACHE_DIR": str(CACHE),
            "CORTEX_NEO_UI_FILE": str(generation / "ui.lua"),
            "CORTEX_NEO_THEME_DIR": str(ROOT / "theme"),
            "CORTEX_NEO_PRESENTATION_FILE": presentation_path,
        }
        try:
            for path in sorted(generation.glob("*.conf")):
                children.append(subprocess.Popen([conky, "-c", str(path)], env=env))
            time.sleep(3)
            if any(child.poll() is not None for child in children):
                raise RuntimeError("A Conky card exited during startup; see the journal")
            if not overflow(layout, monitor_scale):
                return children, generation
        except Exception:
            stop_children(children)
            raise
        if attempt < 3:
            stop_children(children)
            children = []
    LOG.warning("Some text exceeds its row after font fitting; inspect the current screen")
    return children, generation


def retire_generations(current):
    parent = current.parent.resolve()
    old = sorted(parent.glob("generation-*"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in old[3:]:
        if path != current and not path.is_symlink() and path.resolve().parent == parent:
            shutil.rmtree(path)


def main():
    global STOPPING
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ensure_directories()
    import_session_environment()
    conky = shutil.which("conky")
    if not conky:
        LOG.error("Conky is not installed. Run cortex-neo doctor for prerequisites.")
        return 78
    try:
        banner = subprocess.run(
            [conky, "--version"], capture_output=True, text=True, timeout=5, check=True
        )
        build = capabilities(banner.stdout + banner.stderr)
        if not build["x11"] or not build["lua"]:
            LOG.error("Conky requires X11 and Lua support; run cortex-neo doctor")
            return 78
    except (OSError, subprocess.SubprocessError):
        LOG.error("Unable to inspect Conky; run cortex-neo doctor")
        return 78

    def stop(_signum, _frame):
        global STOPPING
        STOPPING = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    children = []
    signature = None
    next_check = 0
    initial_wait_deadline = time.monotonic() + 10
    try:
        while not STOPPING:
            if children and any(child.poll() is not None for child in children):
                LOG.error("A card exited; restarting the card group")
                stop_children(children)
                children = []
                signature = None
                next_check = time.monotonic() + 5
            if time.monotonic() < next_check:
                time.sleep(0.5)
                continue
            next_check = time.monotonic() + 10
            snapshot = read_json(CACHE / "dashboard.json", {})
            if not isinstance(snapshot, dict) or not snapshot.get("sampled_at"):
                continue
            if (
                not children
                and not snapshot.get("software_ready")
                and time.monotonic() < initial_wait_deadline
            ):
                next_check = time.monotonic() + 1
                continue
            settings = load_preferences(CONFIG)
            try:
                area, monitor_scale = monitor_area(settings.get("monitor", "primary"))
                active = visible_cards(snapshot, settings["hidden_cards"])
                gpu = snapshot.get("gpu", {}) or {}
                modes = tuple(
                    key for key in ("load", "frequency", "memory_load") if gpu.get(key) is not None
                )
                weeks = len((snapshot.get("calendar") or {}).get("weeks", [])) or 6
                candidate = (
                    area,
                    monitor_scale,
                    tuple(sorted(active)),
                    modes,
                    weeks,
                    str(
                        {
                            key: settings.get(key)
                            for key in (
                                "monitor",
                                "scale_multiplier",
                                "layout",
                                "profile",
                                "density",
                                "hidden_cards",
                                "anchor",
                                "theme",
                            )
                        }
                    ),
                )
                if candidate == signature:
                    continue
                layout = calculate(
                    area,
                    snapshot,
                    weeks,
                    settings.get("scale_multiplier", 1),
                    settings.get("layout", "auto"),
                    hidden=settings["hidden_cards"],
                    anchor=settings["anchor"],
                    profile=settings["profile"],
                    density=settings["density"],
                )
                layout["theme"] = settings["theme"]
                stop_children(children)
                children = []
                children, generation = launch(layout, snapshot, conky, monitor_scale, build)
                signature = candidate
                retire_generations(generation)
                LOG.info(
                    "Mapped %s cards, %s layout, scale %.3f",
                    len(children),
                    layout["profile"],
                    layout["scale"],
                )
            except (RuntimeError, OSError, ValueError, ImportError) as error:
                LOG.error("Desktop layout unavailable: %s", error)
                signature = None
                import_session_environment(refresh=True)
    finally:
        stop_children(children)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
