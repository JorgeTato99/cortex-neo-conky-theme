"""Install immutable releases and switch the user entry point transactionally.

Virtual environments remain at their original absolute paths. Preparing a new
release never mutates the environment of the currently running installation.
"""

import argparse
import contextlib
import hashlib
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from cortex_neo.diagnostics import MINIMUM_PYTHON  # noqa: E402
from cortex_neo.i18n import tr  # noqa: E402

PROJECT = "cortex-neo"
MARKER = "installation.json"
PACKAGES = [
    "conky-all",
    "python3-venv",
    "python3-gi",
    "gir1.2-gtk-3.0",
    "fontconfig",
    "fonts-font-awesome",
    "fonts-dejavu-core",
    "fonts-liberation",
    "x11-utils",
    "xwayland",
    "iproute2",
    "pciutils",
    "util-linux",
    "procps",
    "dbus-user-session",
]
PROFILES = {"ubuntu": {"24.04", "26.04"}, "debian": {"12", "13"}}
CONTENT = [
    "cortex_neo",
    "theme",
    "config",
    "systemd",
    "scripts",
    "tests",
    "docs",
    "assets",
    "README.md",
    "README.es.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "stylua.toml",
    ".editorconfig",
]


def xdg(env, key, default):
    value = Path(env.get(key, ""))
    return value if value.is_absolute() else default


@contextlib.contextmanager
def installation_lock(paths):
    """Serialize CLI installation/uninstallation without blocking indefinitely."""
    import fcntl

    paths.state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (paths.state / "installation.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError(
                tr("Another CORTEX NEO installation or removal is in progress.")
            ) from error
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


@dataclass
class Paths:
    home: Path
    target: Path
    releases: Path
    config: Path
    cache: Path
    state: Path
    units: Path
    applications: Path

    @classmethod
    def for_user(cls, home=None, env=None):
        home = home or Path.home()
        env = os.environ if env is None else env
        data = xdg(env, "XDG_DATA_HOME", home / ".local/share")
        config = xdg(env, "XDG_CONFIG_HOME", home / ".config")
        return cls(
            home,
            data / PROJECT,
            data / (PROJECT + "-releases"),
            config / PROJECT,
            xdg(env, "XDG_CACHE_HOME", home / ".cache") / PROJECT,
            xdg(env, "XDG_STATE_HOME", home / ".local/state") / PROJECT,
            config / "systemd/user",
            data / "applications",
        )


def run(argv, *, check=True):
    try:
        result = subprocess.run(argv, check=False, capture_output=not check)
    except OSError:
        if not check:
            return 127
        raise
    if check and result.returncode:
        raise RuntimeError(
            tr("Command failed ({p0}): {p1}").format(p0=result.returncode, p1=argv[0])
        )
    return result.returncode


def package_plan(info):
    name, version = info.get("ID"), info.get("VERSION_ID")
    if version not in PROFILES.get(name, set()):
        raise RuntimeError(
            f"Sin perfil de paquetes para {name} {version}. Preparar las dependencias "
            "manualmente y usar --skip-system-deps; consultar docs/reference/compatibility.md."
        )
    return PACKAGES + (["fonts-ubuntu"] if name == "ubuntu" else [])


def fingerprint(path):
    if path.is_symlink():
        return "link:" + os.readlink(path)
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    return None


def remove_file(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        raise RuntimeError(f"Se esperaba un archivo, no una carpeta: {path}")


def remove_release(path, releases):
    """Never follow links or delete directories outside the owned release root."""
    if path.is_symlink() or path.resolve().parent != releases.resolve():
        raise RuntimeError(tr("Unmanaged release path: {p0}").format(p0=path))
    metadata = json.loads((path / MARKER).read_text())
    if metadata.get("project") != PROJECT:
        raise RuntimeError(tr("Release does not belong to CORTEX NEO: {p0}").format(p0=path))
    shutil.rmtree(path)


def owned_target(paths):
    target = paths.target
    if target.is_symlink():
        resolved = target.resolve()
        if resolved.parent != paths.releases.resolve():
            raise RuntimeError(tr("Installation link points outside managed releases."))
        metadata = json.loads((resolved / MARKER).read_text())
        if metadata.get("project") != PROJECT:
            raise RuntimeError(tr("Existing installation does not belong to CORTEX NEO."))
    elif target.exists() and not (
        target.is_dir()
        and (target / "cortex_neo/__main__.py").is_file()
        and (target / "theme/formatter.lua").is_file()
    ):
        raise RuntimeError(tr("Installation path contains unrelated data."))


def controls(paths):
    return [
        paths.home / ".local/bin/cortex-neo",
        paths.home / ".local/bin/conky-neon",
        paths.applications / "cortex-neo.desktop",
        paths.units / "cortex-neo.service",
        paths.units / "cortex-neo-metrics.service",
        paths.units / "graphical-session.target.wants/cortex-neo.service",
    ]


def snapshot_controls(paths, backup):
    snapshots = []
    paths_to_save = controls(paths)
    if legacy_shortcut(paths):
        paths_to_save.append(paths.applications / "conky.desktop")
    for index, path in enumerate(paths_to_save):
        if path.exists() and not path.is_file() and not path.is_symlink():
            raise RuntimeError(tr("Will not replace a user directory: {p0}").format(p0=path))
        saved = backup / f"control-{index}"
        existed = path.exists() or path.is_symlink()
        if existed:
            shutil.copy2(path, saved, follow_symlinks=False)
        snapshots.append((path, saved, existed))
    return snapshots


def restore_controls(snapshots):
    for path, saved, existed in snapshots:
        remove_file(path)
        if existed:
            shutil.copy2(saved, path, follow_symlinks=False)


def quote_unit(value):
    return unit_path(value).replace("\\", "\\\\").replace('"', '\\"')


def unit_path(value):
    text = str(value)
    if any(character in text for character in ("\n", "\r", "\x00")):
        raise RuntimeError(tr("Path cannot contain newlines or null characters."))
    return text.replace("%", "%%")


def legacy_shortcut(paths):
    path = paths.applications / "conky.desktop"
    return path.is_file() and any(
        name in path.read_text(errors="replace")
        for name in ("Name=Conky CÓRTEX NEO", "Name=Conky CORTEX NEO")
    )


def write_controls(paths, release):
    launcher, alias, desktop, *rest = controls(paths)
    for path in controls(paths):
        path.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text(
        "#!/bin/sh\nexec "
        + shlex.quote(str(paths.target / "venv/bin/python"))
        + ' -I -m cortex_neo "$@"\n'
    )
    launcher.chmod(0o755)
    remove_file(alias)
    alias.symlink_to("cortex-neo")
    for name in ("cortex-neo.service", "cortex-neo-metrics.service"):
        template = (release / "systemd" / name).read_text()
        template = (
            "\n".join(
                "WorkingDirectory=" + unit_path(paths.target)
                if line.startswith("WorkingDirectory=")
                else line.replace("%h/.local/share/cortex-neo", quote_unit(paths.target))
                for line in template.splitlines()
            )
            + "\n"
        )
        (paths.units / name).write_text(template)
    enabled = rest[-1]
    remove_file(enabled)
    enabled.symlink_to("../cortex-neo.service")
    executable = str(launcher).replace("\\", "\\\\").replace('"', '\\"')
    executable = executable.replace("$", "\\$").replace("`", "\\`").replace("%", "%%")
    desktop.write_text(
        tr('[Desktop Entry]\nType=Application\nName=CORTEX NEO\nExec="')
        + executable
        + '" start\nIcon=utilities-system-monitor\n'
        "Terminal=false\nCategories=System;Monitor;\n"
    )
    if legacy_shortcut(paths):
        remove_file(paths.applications / "conky.desktop")


def prepare_release(source, release, command=run):
    release.mkdir(mode=0o700)
    (release / MARKER).write_text(json.dumps({"project": PROJECT, "format": 1}))
    for name in CONTENT:
        item = source / name
        if item.is_dir():
            shutil.copytree(
                item, release / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
            )
        elif item.is_file():
            shutil.copy2(item, release / name)
    from cortex_neo.version import stamp_source

    stamp_source(source, release)
    command(["/usr/bin/python3", "-m", "venv", "--system-site-packages", str(release / "venv")])
    python = str(release / "venv/bin/python")
    command(
        [
            python,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--only-binary=:all:",
            "-r",
            str(release / "requirements.txt"),
        ]
    )
    command(
        [
            python,
            "-c",
            "import pathlib,site,sys; pathlib.Path(site.getsitepackages()[0], 'cortex_neo.pth')"
            ".write_text(sys.argv[1]+'\\n')",
            str(release),
        ]
    )
    command([python, "-I", "-m", "cortex_neo", "doctor", "--dependencies-only"])


def install(paths, options, *, source=SOURCE, command=run, prepare=prepare_release):
    owned_target(paths)
    available = command(["systemctl", "--user", "show-environment"], check=False) == 0
    active_units = [
        unit
        for unit in ("cortex-neo.service", "cortex-neo-metrics.service")
        if available
        and command(["systemctl", "--user", "is-active", "--quiet", unit], check=False) == 0
    ]
    active = bool(active_units)
    if not options.no_start and not available:
        raise RuntimeError(tr("No user systemd manager. Log in or use --no-start."))
    if options.no_start and active:
        raise RuntimeError(tr("The theme is active: omit --no-start to update safely."))
    if options.location_file and not options.location_file.is_file():
        raise RuntimeError(tr("The specified manual location file does not exist."))
    identifier = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]
    paths.releases.mkdir(parents=True, exist_ok=True)
    release = paths.releases / identifier
    try:
        prepare(source, release, command)
    except Exception:
        if release.exists():
            remove_release(release, paths.releases)
        raise
    backup = paths.state / "backups" / identifier
    backup.mkdir(parents=True, mode=0o700)
    paths.state.chmod(0o700)
    snapshots = snapshot_controls(paths, backup)
    if paths.config.exists():
        shutil.copytree(paths.config, backup / "config", symlinks=True)
    previous = None
    was_link = paths.target.is_symlink()
    legacy_active = False
    created = []
    switched = False
    moved_legacy = False
    next_link = None
    try:
        if active:
            command(
                ["systemctl", "--user", "stop", "cortex-neo.service", "cortex-neo-metrics.service"]
            )
        if options.migrate_legacy and available:
            legacy_active = (
                command(
                    ["systemctl", "--user", "is-active", "--quiet", "conky-neon.service"],
                    check=False,
                )
                == 0
            )
            command(
                ["systemctl", "--user", "stop", "conky-neon.service", "conky-neon-metrics.service"]
            )
        if was_link:
            previous = paths.target.resolve()
        elif paths.target.exists():
            previous = paths.releases / ("legacy-" + identifier)
            paths.target.rename(previous)
            moved_legacy = True
            (previous / MARKER).write_text(json.dumps({"project": PROJECT, "format": 1}))
        next_link = paths.target.with_name("cortex-neo.next-" + identifier)
        next_link.symlink_to(release)
        os.replace(next_link, paths.target)
        switched = True
        for directory in (paths.config, paths.cache):
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            directory.chmod(0o700)
        for name in ("settings", "location"):
            path = paths.config / (name + ".json")
            if not path.exists() and not path.is_symlink():
                template = (
                    options.location_file
                    if name == "location" and options.location_file
                    else (release / "config" / (name + ".example.json"))
                )
                shutil.copy2(template, path)
                path.chmod(0o600)
                created.append(path)
        write_controls(paths, release)
        if available:
            command(["systemctl", "--user", "daemon-reload"])
        if not options.no_start:
            command(["systemctl", "--user", "restart", "cortex-neo.service"])
            command(
                [
                    "systemctl",
                    "--user",
                    "is-active",
                    "--quiet",
                    "cortex-neo.service",
                    "cortex-neo-metrics.service",
                ]
            )
        if options.migrate_legacy and available:
            command(["systemctl", "--user", "disable", "conky-neon.service"], check=False)
        metadata = {
            "project": PROJECT,
            "format": 1,
            "previous": str(previous) if previous else None,
            "backup": str(backup),
            "controls": {str(path): fingerprint(path) for path in controls(paths)},
        }
        from cortex_neo.version import version_info

        metadata["application"] = version_info(release, allow_git=False)
        (release / MARKER).write_text(json.dumps(metadata, indent=2))
    except Exception:
        if available and switched:
            command(
                ["systemctl", "--user", "stop", "cortex-neo.service", "cortex-neo-metrics.service"],
                check=False,
            )
        if switched:
            remove_file(paths.target)
        if previous and (switched or moved_legacy):
            if was_link:
                paths.target.symlink_to(previous)
            else:
                previous.rename(paths.target)
        if next_link is not None and next_link.is_symlink():
            next_link.unlink()
        restore_controls(snapshots)
        for path in created:
            remove_file(path)
        if available:
            command(["systemctl", "--user", "daemon-reload"], check=False)
            if active:
                command(["systemctl", "--user", "start", *active_units], check=False)
            if legacy_active:
                command(["systemctl", "--user", "start", "conky-neon.service"], check=False)
        remove_release(release, paths.releases)
        raise
    print(
        tr("Installed: {p0}\nConfiguration: {p1}\nBackup: {p2}").format(
            p0=paths.target, p1=paths.config, p2=backup
        )
    )
    if options.no_start:
        print(tr("Startup enabled for the next graphical session. The theme was not started now."))


def uninstall(paths, command=run):
    owned_target(paths)
    if not paths.target.is_symlink():
        raise RuntimeError(tr("Update an old installation with the installer before removing it."))
    metadata = json.loads((paths.target / MARKER).read_text())
    available = command(["systemctl", "--user", "show-environment"], check=False) == 0
    if available:
        command(["systemctl", "--user", "stop", "cortex-neo.service", "cortex-neo-metrics.service"])
    for path in controls(paths):
        if fingerprint(path) == metadata.get("controls", {}).get(str(path)):
            remove_file(path)
        elif path.exists() or path.is_symlink():
            print(f"Conservado por cambios del usuario: {path}")
    remove_file(paths.target)
    for release in paths.releases.iterdir():
        if release.is_dir() and not release.is_symlink() and (release / MARKER).is_file():
            remove_release(release, paths.releases)
    if available:
        command(["systemctl", "--user", "daemon-reload"])
    print(
        tr("Removed. Configuration, cache and backups preserved at {p0}, {p1}, {p2}.").format(
            p0=paths.config, p1=paths.cache, p2=paths.state
        )
    )


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=tr("Install, update or uninstall CORTEX NEO."))
    parser.add_argument(
        "--skip-system-deps",
        action="store_true",
        help="Dependencias del SO preparadas manualmente.",
    )
    parser.add_argument(
        "--no-start",
        action="store_true",
        help=tr("Install for the next session without starting services."),
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Mostrar el plan sin modificar archivos ni paquetes."
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help=tr("Remove only the installation; preserve personal data."),
    )
    parser.add_argument(
        "--migrate-legacy",
        action="store_true",
        help=tr("Explicitly stop the old conky-neon."),
    )
    parser.add_argument("--location-file", type=Path, help=tr("Manually configured location file."))
    return parser.parse_args(argv)


def main(argv=None):
    options = arguments(argv)
    if sys.version_info[:2] < MINIMUM_PYTHON:
        print("Se requiere Python del sistema 3.11 o posterior.", file=sys.stderr)
        return 78
    paths = Paths.for_user()
    try:
        packages = (
            []
            if options.skip_system_deps or options.uninstall
            else package_plan(platform.freedesktop_os_release())
        )
        if options.dry_run:
            print(
                json.dumps(
                    {
                        "action": "uninstall" if options.uninstall else "install/update",
                        "target": str(paths.target),
                        "packages": packages,
                        "start": not options.no_start,
                        "preserve_configuration": True,
                    },
                    indent=2,
                )
            )
            return 0
        if os.geteuid() == 0:
            raise RuntimeError(
                tr("Run as the desktop user, without sudo. Only apt requests elevation.")
            )
        with installation_lock(paths):
            if options.uninstall:
                uninstall(paths)
                return 0
            if packages:
                run(["sudo", "apt-get", "update"])
                run(["sudo", "apt-get", "install", "--yes", "--no-install-recommends", *packages])
            install(paths, options)
    except (OSError, RuntimeError, ValueError) as error:
        print(tr("Installation incomplete: {p0}").format(p0=error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
