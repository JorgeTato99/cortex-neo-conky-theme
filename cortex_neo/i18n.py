"""Data-only message catalogs shared by Python controls and generated Lua UI.

English is the source language. JSON avoids a build-time gettext dependency in
this small mixed-language application. Machine-readable keys are never localized.
"""

import json
from functools import lru_cache
from pathlib import Path

_language = None


def set_language(language):
    global _language
    _language = language if language in ("en", "es") else "en"


@lru_cache(maxsize=2)
def catalog(language="en"):
    path = Path(__file__).with_name("locales") / ("es.json" if language == "es" else "en.json")
    try:
        values = json.loads(path.read_text(encoding="utf-8"))
        return {
            key: value
            for key, value in values.items()
            if isinstance(key, str) and isinstance(value, str)
        }
    except (OSError, ValueError, AttributeError):
        return {}


def tr(message):
    global _language
    if _language is None:
        from .preferences import load_preferences

        set_language(load_preferences()["language"])
    return catalog(_language).get(message, message)
