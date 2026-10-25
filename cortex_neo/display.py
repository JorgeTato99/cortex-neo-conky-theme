"""Read a monitor's usable area without requesting any location information."""

import os
import subprocess


def import_session_environment(refresh=False):
    if not os.environ.get("DBUS_SESSION_BUS_ADDRESS") and os.environ.get("XDG_RUNTIME_DIR"):
        os.environ["DBUS_SESSION_BUS_ADDRESS"] = (
            "unix:path=" + os.environ["XDG_RUNTIME_DIR"] + "/bus"
        )
    try:
        result = subprocess.run(
            ["systemctl", "--user", "show-environment"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        for line in result.stdout.splitlines():
            name, separator, value = line.partition("=")
            if separator and name in (
                "DISPLAY",
                "XAUTHORITY",
                "WAYLAND_DISPLAY",
                "DBUS_SESSION_BUS_ADDRESS",
            ):
                if refresh or not os.environ.get(name):
                    os.environ[name] = value
    except (OSError, subprocess.SubprocessError):
        pass


def monitor_area(selection="primary"):
    """Use XWayland's coordinates, matching Conky's explicitly selected X11 output."""
    import gi

    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk

    # Initialize device/display management before opening a secondary connection.
    Gdk.set_allowed_backends("x11")
    if not Gdk.init_check([])[0]:
        raise RuntimeError("No X11/XWayland display can be initialized")
    display = Gdk.Display.open(os.environ.get("DISPLAY", ":0"))
    if display is None:
        raise RuntimeError("No graphical user display is available")
    try:
        count = display.get_n_monitors()
        if not count:
            raise RuntimeError("No active monitor is available")
        if isinstance(selection, int) and 0 <= selection < count:
            monitor = display.get_monitor(selection)
        else:
            monitor = display.get_primary_monitor() or display.get_monitor(0)
        area = monitor.get_workarea()
        return (area.x, area.y, area.width, area.height), monitor.get_scale_factor()
    finally:
        display.close()
