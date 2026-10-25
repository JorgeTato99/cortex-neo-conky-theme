"""Application paths following XDG; user settings never live beside generated files."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def xdg(variable: str, fallback: str) -> Path:
    candidate = Path(os.environ.get(variable, ""))
    return candidate if candidate.is_absolute() else Path.home() / fallback


CONFIG = xdg("XDG_CONFIG_HOME", ".config") / "cortex-neo"
CACHE = xdg("XDG_CACHE_HOME", ".cache") / "cortex-neo"
STATE = xdg("XDG_STATE_HOME", ".local/state") / "cortex-neo"
GENERATED = CACHE / "cards"


def ensure_directories() -> None:
    for path in (CONFIG, CACHE, STATE, GENERATED):
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
