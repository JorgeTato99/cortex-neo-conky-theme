"""Validate persistent user presentation choices before generating Conky code."""

import json
import math
import re

from .io import atomic, read_json
from .paths import CONFIG

CARD_NAMES = {
    "system",
    "cpu",
    "ram",
    "gpu",
    "storage",
    "network",
    "software",
    "weather",
    "calendar",
}
BASE_COLORS = dict(
    text="DAE9FC",
    primary="55AEFF",
    secondary="6DE4EF",
    muted="91A7C2",
    border="265A7C",
    accent="B3A1FF",
    warning="FFC979",
)
PALETTES = {
    "neon": BASE_COLORS,
    "contrast": {**BASE_COLORS, "text": "FFFFFF", "muted": "C9DBF0", "border": "588DB4"},
    "amber": {**BASE_COLORS, "primary": "FFCC66", "secondary": "FFE7B0", "accent": "9EBFFF"},
}


def color(value, default):
    return (
        value.upper()
        if isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{6}", value)
        else default
    )


def theme_settings(raw=None):
    raw = raw if isinstance(raw, dict) else {}
    name = raw.get("palette")
    name = name if isinstance(name, str) and name in PALETTES else "neon"
    colors = dict(PALETTES[name])
    overrides = raw.get("colors")
    if isinstance(overrides, dict):
        colors.update({key: color(overrides.get(key), value) for key, value in colors.items()})
    opacity = raw.get("opacity", 190 / 255)
    if (
        isinstance(opacity, bool)
        or not isinstance(opacity, (int, float))
        or not math.isfinite(opacity)
        or not 0 <= opacity <= 1
    ):
        opacity = 190 / 255
    return dict(
        palette=name,
        colors=colors,
        opacity=opacity,
        background=color(raw.get("background"), "081220"),
    )


def load_preferences(root=CONFIG):
    raw = read_json(root / "settings.json", {})
    raw = raw if isinstance(raw, dict) else {}
    hidden = raw.get("hidden_cards", [])
    hidden = hidden if isinstance(hidden, list) else []
    return {
        **raw,
        "hidden_cards": sorted(
            {item for item in hidden if isinstance(item, str) and item in CARD_NAMES - {"system"}}
        ),
        "anchor": "left" if raw.get("anchor") == "left" else "right",
        "profile": raw.get("profile")
        if raw.get("profile") in ("full", "compact", "auto")
        else "auto",
        "density": "comfortable" if raw.get("density") == "comfortable" else "complete",
        "history_hours": raw.get("history_hours")
        if isinstance(raw.get("history_hours"), int)
        and not isinstance(raw.get("history_hours"), bool)
        and 0 <= raw["history_hours"] <= 168
        else 24,
        "theme": theme_settings(read_json(root / "theme.json", {})),
    }


def update_preferences(
    root=CONFIG,
    *,
    palette=None,
    opacity=None,
    hidden=None,
    anchor=None,
    profile=None,
    density=None,
    history_hours=None,
):
    if palette is not None and palette not in PALETTES:
        raise ValueError("Unknown palette")
    if opacity is not None and (not math.isfinite(opacity) or not 0 <= opacity <= 1):
        raise ValueError("Opacity must be between 0 and 1")
    if anchor is not None and anchor not in ("left", "right"):
        raise ValueError("Anchor must be left or right")
    if profile is not None and profile not in ("full", "compact", "auto"):
        raise ValueError("Profile must be full, compact or auto")
    if density is not None and density not in ("complete", "comfortable"):
        raise ValueError("Density must be complete or comfortable")
    if history_hours is not None and (
        not isinstance(history_hours, int)
        or isinstance(history_hours, bool)
        or not 0 <= history_hours <= 168
    ):
        raise ValueError("History retention must be 0–168 hours")
    theme = read_json(root / "theme.json", {})
    theme = theme if isinstance(theme, dict) else {}
    settings = read_json(root / "settings.json", {})
    settings = settings if isinstance(settings, dict) else {}
    if palette is not None:
        theme["palette"] = palette
    if opacity is not None:
        theme["opacity"] = opacity
    if hidden is not None:
        settings["hidden_cards"] = sorted(
            {item for item in hidden if isinstance(item, str) and item in CARD_NAMES - {"system"}}
        )
    if anchor is not None:
        settings["anchor"] = anchor
    if profile is not None:
        settings["profile"] = profile
    if density is not None:
        settings["density"] = density
    if history_hours is not None:
        settings["history_hours"] = history_hours
    atomic(root / "theme.json", json.dumps(theme, indent=2))
    atomic(root / "settings.json", json.dumps(settings, indent=2))
    return load_preferences(root)
