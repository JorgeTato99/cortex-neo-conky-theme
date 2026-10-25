"""Read installed toolchains without starting installers or sourcing shell profiles."""

import json
import logging
import re
import shutil
from pathlib import Path

from .io import command, read_json, safe

LOG = logging.getLogger(__name__)


def executable(name, *candidates):
    for path in candidates:
        if Path(path).is_file():
            return str(path)
    return shutil.which(name)


def first_line(value):
    return (value or "").splitlines()[0] if value else ""


def match(pattern, value, group=1):
    result = re.search(pattern, value or "")
    return result.group(group) if result else ""


def packages():
    """Keep successful records even when dpkg reports missing sibling packages."""
    output = command(
        [
            "dpkg-query",
            "-W",
            "-f=${Package}\t${Version}\t${db:Status-Abbrev}\n",
            "code",
            "brave-browser",
            "docker-ce",
            "docker-desktop",
        ],
        accepted=(0, 1),
    )
    result = {}
    for line in (output or "").splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[2].startswith("ii"):
            result[parts[0]] = parts[1]
    return result


def applications():
    installed = packages()
    result = []

    def add(label, version, detail=""):
        if version:
            result.append(dict(label=label, version=version, detail=detail, group="Aplicaciones"))

    product = read_json("/usr/share/code/resources/app/product.json", {})
    if not isinstance(product, dict):
        product = {}
    code_path = executable("code", Path("/usr/share/code/bin/code"))
    product_version = product.get("version") if isinstance(product.get("version"), str) else None
    code = (
        (product_version or installed.get("code")) if code_path or installed.get("code") else None
    )
    commit = product.get("commit", "")
    commit = commit if isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{7,40}", commit) else ""
    if not code and (path := code_path):
        lines = (command([path, "--version"], timeout=4) or "").splitlines()
        code = match(r"^(\d+\.\d+\.\d+)", "\n".join(lines))
        commit = lines[1] if len(lines) > 1 and re.fullmatch(r"[0-9a-f]{7,40}", lines[1]) else ""
    add("VS Code", code, commit)
    engine = installed.get("docker-ce", "")
    if engine:
        add("Docker Engine", engine.split(":")[-1].split("-")[0], engine)
    elif path := executable("docker"):
        server = command(
            [path, "--context", "default", "version", "--format", "{{.Server.Version}}"]
        )
        add("Docker Engine", match(r"^(\d+\.\d+\.\d+)", server))
    desktop = installed.get("docker-desktop", "")
    if desktop:
        version, _, build = desktop.partition("-")
        add("Docker Desktop", version, "build " + build if build else "")
    brave = installed.get("brave-browser", "")
    if not brave and (path := executable("brave-browser")):
        brave = match(r"(?:Brave Browser|Brave)\s+(\d[\w.-]+)", command([path, "--version"]))
    add("Brave", brave)
    if path := executable("cloudflared"):
        output = command([path, "--version"])
        build = match(r"\(built ([^)]+)\)", output)
        add(
            "Cloudflare Tunnel",
            match(r"cloudflared version (\S+)", output),
            "build " + build if build else "",
        )
    return result


def node_versions():
    paths = {p.resolve() for p in (Path.home() / ".nvm/versions/node").glob("*/bin/node")}
    if path := executable("node"):
        paths.add(Path(path).resolve())
    result = []
    for path in sorted(paths):
        output = command([str(path), "-p", "JSON.stringify(process.versions)"])
        try:
            value = json.loads(output or "{}")
        except ValueError:
            continue
        if isinstance(value, dict) and value.get("node"):
            result.append(
                dict(
                    label="Node.js",
                    version=value["node"],
                    detail="V8 " + value.get("v8", ""),
                    group="Lenguajes",
                )
            )
    return result


def python_versions():
    system = Path("/usr/bin/python3").resolve()
    selected = executable("python3", Path.home() / ".local/bin/python3")
    active = Path(selected).resolve() if selected else system
    paths = {system, active}
    paths.update(
        p.resolve() for p in (Path.home() / ".local/share/uv/python").glob("cpython-*/bin/python3")
    )
    result = []
    for path in sorted(paths, key=lambda p: (p != active, p != system, str(p))):
        output = command([str(path), "-VV"])
        version = match(r"Python (\S+)", output)
        if not version:
            continue
        role = "active" if path == active else "system" if path == system else "additional"
        labels = {
            "active": "Python (activa/SO)" if active == system else "Python (activa)",
            "system": "Python (SO)",
            "additional": "Python adicional",
        }
        result.append(
            dict(
                label=labels[role],
                version=version,
                detail=match(r"\[([^]]+)\]", output),
                group="Lenguajes",
                family="python",
                role=role,
            )
        )
    return result


def compiled_languages():
    result = []

    def add(label, version, detail=""):
        if version:
            result.append(dict(label=label, version=version, detail=detail, group="Lenguajes"))

    if path := executable("rustc", Path.home() / ".cargo/bin/rustc"):
        output = command([path, "-Vv"])
        info = dict(line.split(": ", 1) for line in (output or "").splitlines() if ": " in line)
        detail = " / ".join(
            v
            for v in (
                info.get("commit-hash"),
                "LLVM " + info["LLVM version"] if info.get("LLVM version") else "",
            )
            if v
        )
        add("Rust", info.get("release"), detail)
    if path := executable("gcc"):
        add(
            "C / C++ · GCC",
            command([path, "-dumpfullversion"]),
            first_line(command([path, "--version"])),
        )
    if path := executable("clang", Path.home() / ".local/bin/clang"):
        output = command([path, "--version"])
        add(
            "C / C++ · Clang",
            match(r"clang version (\S+)", output),
            match(r"\+([0-9a-f]{12,40})-", output) or first_line(output),
        )
    if path := executable("go", Path.home() / ".local/bin/go", Path("/usr/local/go/bin/go")):
        output = command([path, "version"])
        add("Go", match(r"go version go(\S+)", output), match(r"go version go\S+ (\S+)", output))
    return result


def other_languages():
    result = []
    typescript = set()
    for path in (Path.home() / ".nvm/versions/node").glob(
        "*/lib/node_modules/typescript/package.json"
    ):
        info = read_json(path, {})
        if isinstance(info, dict) and info.get("version"):
            typescript.add(info["version"])
    if not typescript and (path := executable("tsc")):
        if version := match(r"Version (\S+)", command([path, "--version"])):
            typescript.add(version)
    for version in sorted(typescript):
        result.append(dict(label="TypeScript", version=version, detail="", group="Lenguajes"))
    probes = [
        ("Perl", "perl", ["-e", 'printf "%vd", $^V'], r"^(\d+\.\d+(?:\.\d+)?)$"),
        ("Ruby", "ruby", ["--version"], r"ruby ([\w.]+)"),
        ("PHP", "php", ["--version"], r"PHP ([\w.]+)"),
        ("Java", "java", ["-version"], r'(?:openjdk|java) (?:version )?"?([\d.]+)'),
        (".NET", "dotnet", ["--version"], r"^(\d+\.\d+[\w.-]*)"),
        ("Dart", "dart", ["--version"], r"Dart SDK version: ([\w.]+)"),
    ]
    for label, binary, args, pattern in probes:
        if path := executable(binary):
            version = match(pattern, command([path, *args], stderr=True))
            if version:
                result.append(dict(label=label, version=version, detail="", group="Lenguajes"))
    return result


def shells():
    values = []
    for binary, pattern in [("bash", r"version ([\d.]+)"), ("zsh", r"zsh ([\d.]+)")]:
        if path := executable(binary):
            if version := match(pattern, command([path, "--version"])):
                values.append(binary + " " + version)
    return (
        [dict(label="Shells", version=" / ".join(values), detail="", group="Herramientas")]
        if values
        else []
    )


def installed_versions():
    """A broken optional probe cannot remove the other valid inventory entries."""
    result = []
    for probe in (
        applications,
        node_versions,
        python_versions,
        compiled_languages,
        other_languages,
        shells,
    ):
        try:
            for entry in probe():
                if not isinstance(entry.get("version"), str) or not entry["version"].strip():
                    continue
                result.append({key: safe(value) for key, value in entry.items()})
        except (OSError, ValueError, TypeError, IndexError, KeyError):
            LOG.warning("Optional inventory probe failed: %s", probe.__name__, exc_info=True)
    return result
