"""Bounded commands, defensive reads and atomic cache publication."""

import json
import logging
import math
import os
import re
import subprocess
import tempfile
from pathlib import Path

LOG = logging.getLogger(__name__)


def command(args, timeout=2, accepted=(0,), stderr=False):
    """Return successful output, or None for missing, failing or timed-out tools.

    dpkg-query intentionally uses accepted=(0, 1): missing one requested package
    must not discard the stdout records of the packages that are installed.
    """
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            cwd=Path.home(),
            # Manager shims must report installed tools, never download a missing toolchain.
            env={**os.environ, "LC_ALL": "C", "RUSTUP_AUTO_INSTALL": "0", "GOTOOLCHAIN": "local"},
            check=False,
        )
        if result.returncode not in accepted:
            return None
        return (result.stdout + ("\n" + result.stderr if stderr else "")).strip() or None
    except (subprocess.SubprocessError, OSError, ValueError):
        LOG.debug("Optional command unavailable: %s", args[0] if args else "?")
        return None


def read(path, default=""):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return default


def read_json(path, default=None):
    try:
        return json.loads(read(path))
    except (ValueError, TypeError):
        return default


def safe(value):
    """Prevent external labels from injecting Conky substitutions into lua_parse."""
    if value is None:
        return ""
    if isinstance(value, bytes):
        value = value.decode(errors="replace")
    return re.sub(r"[\x00-\x1f\x7f$]", " ", str(value)).strip()


def atomic(path, content):
    """Publish a complete UTF-8 file; readers never observe half-written Lua/JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary = Path(file.name)
            file.write(content)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def lua(value):
    """Serialize data only, escaping controls and rejecting nonfinite numbers."""
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value) if math.isfinite(value) else "nil"
    if isinstance(value, str):
        text = value.replace("\\", "\\\\").replace('"', '\\"')
        text = "".join((f"\\{ord(c):03d}") if ord(c) < 32 or ord(c) == 127 else c for c in text)
        return '"' + text + '"'
    if isinstance(value, dict):
        return "{" + ",".join("[" + lua(str(k)) + "]=" + lua(v) for k, v in value.items()) + "}"
    if isinstance(value, (list, tuple)):
        return "{" + ",".join(lua(v) for v in value) + "}"
    raise TypeError(f"Unsupported snapshot value: {type(value).__name__}")


def publish_snapshot(cache, snapshot):
    """Keep history for tools while avoiding unused copies in each Conky Lua VM."""
    snapshot = finite_values(snapshot)
    atomic(cache / "dashboard.json", json.dumps(snapshot, ensure_ascii=False, allow_nan=False))
    presentation = {key: value for key, value in snapshot.items() if key != "history"}
    atomic(cache / "dashboard.lua", "return " + lua(presentation) + "\n")


def finite_values(value):
    """Represent a faulty numeric sensor as unavailable in both JSON and Lua."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: finite_values(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite_values(item) for item in value]
    return value
