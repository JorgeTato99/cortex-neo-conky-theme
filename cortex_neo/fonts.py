"""Allowlisted monospace profiles; resolve availability once per process."""

from functools import lru_cache

from .io import command

FONTS = {"ubuntu": "Ubuntu Sans Mono", "dejavu": "DejaVu Sans Mono", "liberation": "Liberation Mono"}


@lru_cache(maxsize=3)
def resolve_font(profile="ubuntu"):
    requested = FONTS.get(profile, FONTS["ubuntu"])
    for family in dict.fromkeys((requested, FONTS["dejavu"], "monospace")):
        result = command(["fc-match", "-f", "%{family}", family], timeout=2)
        # Fontconfig may silently substitute an unavailable family.
        if result and (family == "monospace" or family in result.split(",")):
            return family
    return "monospace"
