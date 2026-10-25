"""Temporary presentation flags and support exports with selected fields only."""

import os
import re
import stat
import sys
import time
from pathlib import Path

from .context import context_report, context_text
from .io import atomic
from .preferences import CARD_NAMES
from .samples import number


def presentation_file(runtime=None):
    if runtime is None:
        candidate = os.environ.get("XDG_RUNTIME_DIR", "")
        runtime = (
            Path(candidate)
            if Path(candidate).is_absolute()
            else Path("/run/user") / str(os.getuid())
        )
    root = Path(runtime)
    if not root.is_absolute():
        raise PermissionError("Runtime path must be absolute")
    metadata = root.stat()
    if (
        root.is_symlink()
        or not stat.S_ISDIR(metadata.st_mode)
        or metadata.st_uid != os.getuid()
        or metadata.st_mode & 0o077
    ):
        raise PermissionError("Runtime must be a private directory owned by this user")
    folder = root / "cortex-neo"
    if folder.is_symlink():
        raise PermissionError("Presentation directory must not be a symlink")
    if folder.exists() and (
        folder.is_symlink() or folder.stat().st_uid != os.getuid() or folder.stat().st_mode & 0o077
    ):
        raise PermissionError("Presentation directory is not private")
    return folder / "presentation.flag"


def presentation_state(*, runtime=None, now=None):
    now = time.time() if now is None else now
    try:
        path = presentation_file(runtime)
        if path.is_symlink():
            return {"enabled": True, "status": "invalid", "expires_at": None}
        with path.open() as file:
            text = file.read(257)
    except FileNotFoundError:
        return {"enabled": False, "status": "disabled", "expires_at": None}
    except (OSError, UnicodeError):
        return {"enabled": True, "status": "invalid_runtime", "expires_at": None}
    match = re.fullmatch(r"v1 ([0-9]+) ([0-9]+)", text.strip()) if len(text) <= 256 else None
    if not match:
        return {"enabled": True, "status": "invalid", "expires_at": None}
    created, expires = map(int, match.groups())
    if created > now + 5 or (expires and not created < expires <= created + 480 * 60):
        return {"enabled": True, "status": "invalid", "expires_at": None}
    active = expires == 0 or now < expires
    return {
        "enabled": active,
        "status": "active" if active else "expired",
        "expires_at": expires or None,
    }


def set_presentation(enabled, *, runtime=None, minutes=None, now=None):
    if not isinstance(enabled, bool) or (
        minutes is not None
        and (not isinstance(minutes, int) or isinstance(minutes, bool) or not 1 <= minutes <= 480)
    ):
        raise ValueError("Use an optional expiry of 1–480 minutes")
    try:
        path = presentation_file(runtime)
    except OSError as error:
        raise ValueError("A private user runtime directory is required") from error
    if not enabled:
        path.unlink(missing_ok=True)
    else:
        path.parent.mkdir(mode=0o700, exist_ok=True)
        created = int(time.time() if now is None else now)
        expires = created + minutes * 60 if minutes is not None else 0
        # A tiny data-only protocol is also parsed by Lua; it is never executed.
        atomic(path, f"v1 {created} {expires}\n")
    return presentation_state(runtime=runtime, now=now)


def support_report(snapshot, *, diagnostics=None, layout=None):
    from .version import version_info

    snapshot = snapshot if isinstance(snapshot, dict) else {}
    diagnostics = diagnostics if isinstance(diagnostics, dict) else {}
    layout = layout if isinstance(layout, dict) else {}
    allowed = {
        "python",
        "conky",
        "conky_x11",
        "conky_lua",
        "psutil",
        "gi",
        "icons",
        "monospace",
        "xwininfo",
        "user_bus",
        "display",
        "cortex-neo",
        "cortex-neo-metrics",
    }
    checks = diagnostics.get("checks")
    checks = checks if isinstance(checks, list) else []
    selected = [
        {"name": item["name"], "status": item["status"]}
        for item in checks[:32]
        if isinstance(item, dict)
        and isinstance(item.get("name"), str)
        and item["name"] in allowed
        and item.get("status") in ("ok", "warning", "error")
    ]
    area = layout.get("area")
    size = (
        list(area[2:4])
        if isinstance(area, (list, tuple))
        and len(area) == 4
        and all(number(value) is not None and value > 0 for value in area[2:4])
        else None
    )
    cards = layout.get("cards")
    cards = cards if isinstance(cards, dict) else {}
    presentation = snapshot.get("presentation")
    presentation = presentation if isinstance(presentation, dict) else {}
    conky = diagnostics.get("conky")
    conky = conky if isinstance(conky, dict) else {}
    conky_version = conky.get("version")
    conky_version = (
        conky_version
        if isinstance(conky_version, str)
        and re.fullmatch(r"[0-9]+(?:\.[0-9]+){1,3}", conky_version)
        else None
    )
    theme = layout.get("theme")
    theme = theme if isinstance(theme, dict) else {}
    opacity = number(theme.get("opacity"))
    return {
        "kind": "cortex-neo-support",
        "application": version_info(),
        "runtime_python": ".".join(map(str, sys.version_info[:3])),
        "conky": {
            "version": conky_version,
            **{
                key: conky.get(key) if isinstance(conky.get(key), bool) else None
                for key in ("x11", "lua", "wayland", "modern_backend", "modern_color")
            },
        },
        "format_version": 1,
        "context": context_report(snapshot),
        "checks": selected,
        "display": {
            "workarea_size": size,
            "theme_scale": number(layout.get("scale")),
            "palette": theme.get("palette")
            if theme.get("palette") in ("neon", "contrast", "amber")
            else None,
            "opacity": opacity if opacity is not None and opacity <= 1 else None,
            "density": layout.get("density")
            if layout.get("density") in ("complete", "comfortable")
            else "unknown",
            "presentation_profile": layout.get("presentation_profile")
            if layout.get("presentation_profile") in ("full", "compact")
            else "unknown",
            "cards": sorted(CARD_NAMES & cards.keys()),
        },
        "presentation_enabled": presentation.get("enabled") is True,
        "privacy": "Selected fields only; no raw diagnostics, paths, hostname, processes, project labels or city. Nothing is sent.",
    }


def support_text(report):
    application = report["application"]
    lines = [
        "# CÓRTEX NEO — informe de soporte",
        "",
        "Versión: " + application["version"],
        "Revisión: " + (application["revision"] or "desconocida"),
        "Huella de fuentes: " + (application["source_fingerprint"] or "no disponible"),
        "Python del dashboard: " + report["runtime_python"],
        "Conky: " + (report["conky"]["version"] or "desconocida"),
        "",
        context_text(report["context"]),
        "",
        "## Presentación",
        "",
        str(report["display"]),
        "",
        "## Comprobaciones",
        "",
        "| Comprobación | Estado |",
        "|---|---|",
    ]
    lines.extend(f"| {check['name']} | {check['status']} |" for check in report["checks"])
    lines.extend(
        [
            "",
            "Revisa estos campos antes de compartirlos. No se adjuntó una captura ni se envió información.",
        ]
    )
    return "\n".join(lines)
