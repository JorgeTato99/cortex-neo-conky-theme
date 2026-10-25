"""Actionable local checks; diagnostics never contact location or web services."""

import json
import shutil
import subprocess
import sys

from .conky import capabilities

MINIMUM_PYTHON = (3, 11)


def run(argv):
    try:
        return subprocess.run(argv, capture_output=True, text=True, timeout=8, check=False)
    except (OSError, subprocess.SubprocessError) as error:
        return subprocess.CompletedProcess(argv, 1, "", str(error))


def inspect(*, session=True, runner=run, locate=shutil.which, version=None):
    """Report actual imports/connections, not just module or binary presence."""
    checks = []

    def add(name, success, detail, remedy, *, optional=False):
        checks.append(
            dict(
                name=name,
                status="ok" if success else ("warning" if optional else "error"),
                detail=detail,
                remedy="" if success else remedy,
            )
        )

    version = tuple(version or sys.version_info[:3])
    add(
        "python",
        version[:2] >= MINIMUM_PYTHON,
        ".".join(map(str, version)),
        "Usar Python 3.11 o posterior proporcionado por una distribución compatible.",
    )
    conky = locate("conky")
    banner = runner([conky, "--version"]) if conky else None
    build = capabilities(banner.stdout + banner.stderr) if banner else capabilities("")
    add(
        "conky",
        bool(banner and banner.returncode == 0 and build["version"]),
        build["version"] or "No se pudo consultar Conky.",
        "Instalar conky-all mediante el instalador o el gestor de paquetes.",
    )
    for name, detail in (("x11", "backend X11/XWayland"), ("lua", "callbacks Lua")):
        add(
            "conky_" + name,
            build[name],
            detail,
            "Instalar una compilación de Conky con X11 y Lua; en Ubuntu/Debian: conky-all.",
        )
    for module in ("psutil", "gi"):
        script = "import " + module
        if module == "gi":
            script += "; gi.require_version('Gdk', '3.0'); from gi.repository import Gdk"
        result = runner([sys.executable, "-c", script])
        add(
            module,
            result.returncode == 0,
            "Importación real en el intérprete del tema.",
            "Reinstalar el entorno con bash scripts/install.sh; GTK requiere el Python del sistema.",
        )
    for name, family, optional in (
        ("icons", "FontAwesome", False),
        ("monospace", "Ubuntu Sans Mono", True),
    ):
        result = runner(["fc-match", "-f", "%{family}", family])
        actual = result.stdout.strip()
        matched = ("awesome" in actual.lower()) if name == "icons" else family in actual
        add(
            name,
            result.returncode == 0 and matched,
            actual or "Fuente no disponible.",
            "Instalar fonts-font-awesome."
            if name == "icons"
            else "Se usa la fuente de sustitución de fontconfig; Ubuntu Sans Mono conserva el aspecto original.",
            optional=optional,
        )
    add(
        "xwininfo",
        bool(locate("xwininfo")),
        "Medición de las ventanas reales.",
        "Instalar x11-utils.",
    )
    if session:
        from .display import import_session_environment

        import_session_environment()
        bus = runner(["systemctl", "--user", "show-environment"])
        add(
            "user_bus",
            bus.returncode == 0,
            "Conexión al gestor systemd del usuario.",
            "Ejecutar desde la sesión del usuario de escritorio; no usar sudo para arrancar el tema.",
        )
        display = runner(
            [
                sys.executable,
                "-c",
                "import gi; gi.require_version('Gdk','3.0'); from gi.repository import Gdk; "
                "import os,sys; Gdk.set_allowed_backends('x11'); Gdk.init([]); "
                "d=Gdk.Display.open(os.environ.get('DISPLAY','')); "
                "sys.exit(0 if d is not None and d.get_n_monitors()>0 else 1)",
            ]
        )
        add(
            "display",
            display.returncode == 0,
            "Conexión real a X11/XWayland y monitor activo.",
            "Iniciar la sesión gráfica y comprobar XWayland; usar --dependencies-only sin escritorio.",
        )
        for service in ("cortex-neo", "cortex-neo-metrics"):
            active = runner(["systemctl", "--user", "is-active", service + ".service"])
            add(
                service,
                active.returncode == 0,
                "Estado del servicio de usuario.",
                "Ejecutar cortex-neo start y revisar journalctl --user -u " + service,
                optional=True,
            )
    result = {
        "ok": not any(c["status"] == "error" for c in checks),
        "checks": checks,
        "conky": build,
        "location_mode": "manual only; no location queries",
    }
    return result


def main(*, session=True):
    report = inspect(session=session)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1
