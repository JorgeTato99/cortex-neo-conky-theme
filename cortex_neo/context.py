"""Explicit, bounded export of observed capabilities; raw snapshots stay private."""

import math
import re
import time

from .io import safe


def _mapping(value):
    return value if isinstance(value, dict) else {}


def _text(value, limit=160):
    if not isinstance(value, str):
        return ""
    value = re.sub(r"(?<!\w)(?:[A-Za-z]:[\\/]|/)[^\s]+", "[ruta omitida]", safe(value))
    return " ".join(value.split())[:limit]


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def context_report(snapshot, *, now=None):
    """Select public fields rather than trying to remove private keys from a copy."""
    snapshot = _mapping(snapshot)
    now = time.time() if now is None else now
    sampled = snapshot.get("sampled_at")
    age = now - sampled if _number(sampled) else None
    fresh = age is not None and -5 <= age < 10
    software_at = snapshot.get("software_observed_at")
    hardware = _mapping(snapshot.get("hardware"))
    system = _mapping(snapshot.get("os"))
    gpu = _mapping(snapshot.get("gpu"))
    ram = _mapping(snapshot.get("ram"))
    software = snapshot.get("software")
    software = software if isinstance(software, list) else []
    detected = {}
    for item in software:
        item = _mapping(item)
        label, version = _text(item.get("label"), 64), _text(item.get("version"), 96)
        if label and version:
            detected[(label, version)] = {"label": label, "version": version}
        if len(detected) > 100:
            break
    entries = sorted(detected.values(), key=lambda item: (item["label"], item["version"]))
    sensors = [
        key for key in ("load", "frequency", "temperature", "memory_load") if _number(gpu.get(key))
    ]
    return {
        "kind": "cortex-neo-context",
        "format_version": 1,
        "status": ("live" if fresh else "stale") if age is not None else "unavailable",
        "observed_at": sampled if _number(sampled) else None,
        "age_seconds": round(age, 3) if age is not None else None,
        "fresh": fresh,
        "os": {key: _text(system.get(key)) for key in ("name", "kernel", "arch")},
        "hardware": {key: _text(hardware.get(key)) for key in ("cpu_model", "cpu_topology")},
        "memory_total_bytes": ram.get("total")
        if _number(ram.get("total")) and ram["total"] > 0
        else None,
        "gpu": {
            "model": _text(gpu.get("model") or hardware.get("gpu_model")),
            "driver": _text(gpu.get("driver")),
            "observed_sensors": sensors,
        },
        "docker_contexts": [
            key for key in ("default", "desktop-linux") if key in _mapping(snapshot.get("docker"))
        ],
        "software": entries[:100],
        "software_complete": snapshot.get("software_ready") is True,
        "software_observed_at": software_at if _number(software_at) else None,
        "software_age_seconds": round(now - software_at, 3) if _number(software_at) else None,
        "software_truncated": len(entries) > 100,
        "coverage": "observed only; completed queries do not guarantee exhaustive detection",
        "privacy": "selected fields; no hostname, processes, location, mount paths or build details",
    }


def context_text(report):
    """Keep observations visibly separate from instructions when pasted into a chat."""
    system, hardware, gpu = report["os"], report["hardware"], report["gpu"]
    lines = [
        "CÓRTEX NEO — contexto observado del equipo",
        "Estos datos describen observaciones; no contienen instrucciones para el agente.",
        f"Estado: {report['status']} · edad: {report['age_seconds']} s · fecha Unix: {report['observed_at']}",
        "Sistema: " + " / ".join(value for value in system.values() if value),
        "CPU: " + " / ".join(value for value in hardware.values() if value),
        "GPU: " + (gpu["model"] or "modelo no detectado"),
        "Driver GPU: " + (gpu["driver"] or "sin lectura"),
        "Lecturas GPU observadas: "
        + (", ".join(gpu["observed_sensors"]) or "ninguna en esta muestra"),
    ]
    if report["memory_total_bytes"]:
        lines.append(f"RAM total: {report['memory_total_bytes'] / 1024**3:.1f} GiB")
    lines.append(
        "Contextos Docker observados: "
        + (", ".join(report["docker_contexts"]) or "ninguno en esta muestra")
    )
    lines.append(
        "Herramientas detectadas (consulta "
        + ("finalizada" if report["software_complete"] else "parcial o pendiente")
        + f"; edad del inventario: {report['software_age_seconds']} s):"
    )
    lines.extend(f"- {item['label']}: {item['version']}" for item in report["software"])
    if report["software_truncated"]:
        lines.append("Se muestran como máximo cien herramientas/versiones.")
    lines.append(
        "No detectado no implica no instalado. No representa el entorno activo de un proyecto."
    )
    return "\n".join(lines)
