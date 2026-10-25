"""Identify source bytes; revisions are observed metadata, never guessed versions."""

import hashlib
import json
import re
import subprocess
from pathlib import Path

from .io import read, read_json
from .paths import ROOT


def _project_version(root):
    try:
        import tomllib

        parsed = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        value = parsed.get("project", {}).get("version")
        return (
            value
            if isinstance(value, str)
            and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?", value)
            else "unknown"
        )
    except (OSError, ValueError, ImportError, AttributeError):
        return "unknown"


def _git(root, *arguments):
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(root), *arguments],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _fingerprint(root):
    candidates = []
    types = {
        "cortex_neo": {".py"},
        "theme": {".lua", ".conky"},
        "scripts": {".py", ".sh"},
        "systemd": {".service"},
    }
    try:
        for name, extensions in types.items():
            candidates.extend(
                path
                for path in (root / name).rglob("*")
                if path.suffix in extensions and path.is_file() and not path.is_symlink()
            )
        candidates.extend(
            path
            for path in (root / "config").glob("*.example.json")
            if path.is_file() and not path.is_symlink()
        )
        for name in ("pyproject.toml", "requirements.txt", "cortex_neo/_revision.txt"):
            path = root / name
            if path.is_file() and not path.is_symlink():
                candidates.append(path)
        digest = hashlib.sha256()
        for path in sorted(candidates, key=lambda item: item.relative_to(root).as_posix()):
            if not path.resolve().is_relative_to(root):
                return None, 0
            digest.update(path.relative_to(root).as_posix().encode("utf-8") + b"\x00")
            digest.update(path.read_bytes() + b"\x00")
        return (digest.hexdigest() if candidates else None), len(candidates)
    except OSError:
        return None, 0


def version_info(root=ROOT, *, allow_git=True):
    root = Path(root).resolve()
    revision = read(root / "cortex_neo/_revision.txt")
    revision = revision.lower() if re.fullmatch(r"[0-9a-fA-F]{40}", revision) else None
    source = read_json(root / ".source-info.json", {})
    source = (
        source
        if isinstance(source, dict)
        and source.get("project") == "cortex-neo"
        and source.get("format") == 1
        else {}
    )
    dirty = source.get("dirty") if isinstance(source.get("dirty"), bool) else None
    if allow_git and (root / ".git").exists():
        observed = _git(root, "rev-parse", "--verify", "HEAD")
        if observed and re.fullmatch(r"[0-9a-fA-F]{40}", observed):
            revision = observed.lower()
            status = _git(root, "status", "--porcelain", "--untracked-files=normal")
            dirty = bool(status) if status is not None else None
    fingerprint, count = _fingerprint(root)
    marker = read_json(root / "installation.json", {})
    marker = (
        marker
        if isinstance(marker, dict)
        and marker.get("project") == "cortex-neo"
        and marker.get("format") == 1
        else {}
    )
    application = marker.get("application")
    application = application if isinstance(application, dict) else {}
    expected = application.get("source_fingerprint")
    expected = (
        expected.lower()
        if isinstance(expected, str) and re.fullmatch(r"[0-9a-fA-F]{64}", expected)
        else None
    )
    return {
        "version": _project_version(root),
        "revision": revision,
        "source_dirty": dirty,
        "source_fingerprint": fingerprint,
        "fingerprint_files": count,
        "matches_installed_source": fingerprint == expected
        if fingerprint is not None and expected is not None
        else None,
    }


def stamp_source(source, release):
    """Carry a clone's revision into the immutable deployment without its Git history."""
    metadata = version_info(source)
    if metadata["revision"] is not None:
        (release / "cortex_neo/_revision.txt").write_text(
            metadata["revision"] + "\n", encoding="utf-8"
        )
    (release / ".source-info.json").write_text(
        json.dumps({"project": "cortex-neo", "format": 1, "dirty": metadata["source_dirty"]}),
        encoding="utf-8",
    )
