"""Capture the composed desktop through the standard GNOME screenshot portal."""

import shutil
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

from .display import import_session_environment
from .paths import STATE, ensure_directories


def main():
    from gi.repository import Gio, GLib

    ensure_directories()
    import_session_environment()
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    loop = GLib.MainLoop()
    token = "cortex_capture_" + str(time.time_ns())
    result = {"status": 1}
    request_path = None

    def response(_connection, _sender, path, _interface, _signal, params, _user_data):
        if token not in path and path != request_path:
            return
        code, values = params.unpack()
        if code == 0 and "uri" in values:
            source = Path(unquote(urlparse(values["uri"]).path))
            output = STATE / "desktop.png"
            try:
                shutil.copyfile(source, output)
                result["status"] = 0
                print("CAPTURE_OK", output, flush=True)
            except OSError as error:
                print("CAPTURE_UNAVAILABLE", str(error), flush=True)
        else:
            print("CAPTURE_DENIED", code, flush=True)
        loop.quit()

    def timeout():
        print("CAPTURE_TIMEOUT", flush=True)
        # Do not leave a permission dialog behind after its caller has expired.
        if request_path:
            try:
                bus.call_sync(
                    "org.freedesktop.portal.Desktop",
                    request_path,
                    "org.freedesktop.portal.Request",
                    "Close",
                    None,
                    None,
                    Gio.DBusCallFlags.NONE,
                    1000,
                    None,
                )
            except GLib.Error:
                pass
        loop.quit()
        return False

    subscription = bus.signal_subscribe(
        None,
        "org.freedesktop.portal.Request",
        "Response",
        None,
        None,
        Gio.DBusSignalFlags.NONE,
        response,
        None,
    )
    try:
        request = bus.call_sync(
            "org.freedesktop.portal.Desktop",
            "/org/freedesktop/portal/desktop",
            "org.freedesktop.portal.Screenshot",
            "Screenshot",
            GLib.Variant(
                "(sa{sv})",
                (
                    "",
                    {
                        "handle_token": GLib.Variant("s", token),
                        "interactive": GLib.Variant("b", False),
                        "modal": GLib.Variant("b", False),
                    },
                ),
            ),
            None,
            Gio.DBusCallFlags.NONE,
            10000,
            None,
        )
        request_path = request.unpack()[0]
        GLib.timeout_add_seconds(45, timeout)
        loop.run()
    except GLib.Error as error:
        print("CAPTURE_UNAVAILABLE", error.message, flush=True)
    finally:
        bus.signal_unsubscribe(subscription)
    return result["status"]


if __name__ == "__main__":
    raise SystemExit(main())
