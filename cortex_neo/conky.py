"""Describe the installed Conky build without starting a desktop window."""

import re


def capabilities(banner):
    """Prefer explicit X11 output on every supported build, including Wayland."""
    match = re.search(r"\bconky\s+(\d+)\.(\d+)\.(\d+)", banner, re.IGNORECASE)
    version = tuple(map(int, match.groups())) if match else ()
    return {
        "version": ".".join(map(str, version)),
        "modern_backend": version >= (1, 24, 3) if version else False,
        "modern_color": version >= (1, 23, 0) if version else False,
        "x11": bool(re.search(r"^\s*X11\s*:", banner, re.MULTILINE)),
        "wayland": bool(re.search(r"^\s*Wayland\s*:", banner, re.MULTILINE)),
        "lua": bool(re.search(r"Lua bindings\s*:", banner, re.IGNORECASE)),
    }


def window_settings(build=None, theme=None):
    """Keep legacy syntax only where newer settings are unavailable."""
    build = build or {}
    theme = theme or {}
    alpha = round(theme.get("opacity", 190 / 255) * 255)
    background = theme.get("background", "081220")
    if build.get("modern_backend"):
        backend = "output_backend='x11',"
    else:
        backend = "out_to_x=true,"
        if build.get("wayland"):
            backend += "out_to_wayland=false,"
    if build.get("modern_color"):
        color = f"own_window_color='#{alpha:02X}{background}',"
    else:
        color = (
            "own_window_transparent=false,own_window_argb_visual=true,"
            f"own_window_argb_value={alpha},own_window_colour='{background}',"
        )
    return backend, color
