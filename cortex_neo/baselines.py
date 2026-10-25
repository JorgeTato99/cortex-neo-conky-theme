"""Named, selected observations and explicit comparisons between two contexts."""

import json
import time
from pathlib import Path

from .context import context_report
from .paths import STATE
from .records import new_identifier, read_records, remove_record, save_record
from .samples import number

KIND = "cortex-neo-baseline"


def _name(value):
    if not isinstance(value, str):
        raise ValueError("Choose a reference name")
    value = " ".join(value.split())
    if (
        not 1 <= len(value) <= 64
        or not value[0].isalnum()
        or any(not (char.isalnum() or char in " _.-") for char in value)
    ):
        raise ValueError(
            "Reference names allow 1–64 letters, digits, spaces, dots, hyphens and underscores"
        )
    return value


def _canonical(data):
    if (
        not isinstance(data, dict)
        or data.get("kind") != "cortex-neo-context"
        or type(data.get("format_version")) is not int
        or data["format_version"] != 1
        or number(data.get("observed_at")) is None
    ):
        raise ValueError("Choose a version-one CÓRTEX context with a valid observation timestamp")
    gpu = data.get("gpu")
    gpu = gpu if isinstance(gpu, dict) else {}
    contexts = data.get("docker_contexts")
    contexts = contexts if isinstance(contexts, list) else []
    result = context_report(
        {
            "sampled_at": data["observed_at"],
            "os": data.get("os"),
            "hardware": data.get("hardware"),
            "ram": {"total": data.get("memory_total_bytes")},
            "gpu": {"model": gpu.get("model"), "driver": gpu.get("driver")},
            "software": data.get("software"),
            "software_ready": data.get("software_complete") is True,
            "software_observed_at": data.get("software_observed_at"),
            "docker": {key: {} for key in contexts if key in ("default", "desktop-linux")},
        }
    )
    sensors = gpu.get("observed_sensors")
    result["gpu"]["observed_sensors"] = (
        sorted(
            {
                key
                for key in sensors
                if isinstance(key, str)
                and key in ("load", "frequency", "temperature", "memory_load")
            }
        )
        if isinstance(sensors, list)
        else []
    )
    result["software_truncated"] = (
        result["software_truncated"] or data.get("software_truncated") is True
    )
    return result


def load_context_file(path):
    def invalid_constant(_):
        raise ValueError("Nonfinite JSON values are not supported")

    try:
        with Path(path).open("rb") as file:
            payload = file.read(1024 * 1024 + 1)
        if len(payload) > 1024 * 1024:
            raise ValueError("Context file exceeds 1 MiB")
        return _canonical(json.loads(payload, parse_constant=invalid_constant))
    except (OSError, RecursionError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("The context file is unreadable or invalid") from error


def save_baseline(name, context, *, state=STATE):
    name = _name(name)
    selected = _canonical(context)
    record = {
        "kind": KIND,
        "format_version": 1,
        "id": new_identifier(),
        "name": name,
        "name_key": name.casefold(),
        "created_at": time.time(),
        "context": selected,
    }
    save_record(state / "baselines", record, KIND, limit=20, unique_key="name_key", prune=False)
    return record


def _find(name, state):
    key = _name(name).casefold()
    found = [
        record
        for record in read_records(state / "baselines", KIND)
        if record.get("name_key") == key
    ]
    if len(found) != 1:
        raise ValueError("Reference not found or ambiguous")
    return found[0]


def list_baselines(*, state=STATE):
    result = []
    for record in read_records(state / "baselines", KIND):
        context = record.get("context")
        context = context if isinstance(context, dict) else {}
        result.append(
            {
                "id": record["id"],
                "name": record.get("name"),
                "observed_at": context.get("observed_at"),
            }
        )
    return result


def export_baseline(name, *, state=STATE):
    return _canonical(_find(name, state).get("context"))


def remove_baseline(name, *, state=STATE):
    record = _find(name, state)
    remove_record(state / "baselines", record["id"], KIND)


def compare_contexts(reference, current):
    reference, current = _canonical(reference), _canonical(current)
    differences = []
    fields = [
        ("os." + key, reference["os"][key], current["os"][key])
        for key in ("name", "kernel", "arch")
    ]
    fields += [
        ("hardware." + key, reference["hardware"][key], current["hardware"][key])
        for key in ("cpu_model", "cpu_topology")
    ]
    fields += [
        ("memory_total_bytes", reference["memory_total_bytes"], current["memory_total_bytes"]),
        ("gpu.model", reference["gpu"]["model"], current["gpu"]["model"]),
        ("gpu.driver", reference["gpu"]["driver"], current["gpu"]["driver"]),
        (
            "gpu.observed_sensors",
            reference["gpu"]["observed_sensors"],
            current["gpu"]["observed_sensors"],
        ),
        ("docker_contexts", reference["docker_contexts"], current["docker_contexts"]),
    ]
    for field, before, after in fields:
        if before != after:
            differences.append(
                {
                    "field": field,
                    "reference": before,
                    "current": after,
                    "evidence": "missing_observation"
                    if before in (None, "", []) or after in (None, "", [])
                    else "observed_difference",
                }
            )

    def versions(context):
        result = {}
        for item in context["software"]:
            result.setdefault(item["label"], set()).add(item["version"])
        return result

    before, after = versions(reference), versions(current)
    complete = all(
        context["software_complete"] and not context["software_truncated"]
        for context in (reference, current)
    )
    for label in sorted(before.keys() | after.keys()):
        left, right = sorted(before.get(label, [])), sorted(after.get(label, []))
        if left != right:
            differences.append(
                {
                    "field": "software." + label,
                    "reference": left,
                    "current": right,
                    "evidence": "observed_difference" if complete else "partial_inventory",
                }
            )
    return {
        "kind": "cortex-neo-comparison",
        "format_version": 1,
        "reference_observed_at": reference["observed_at"],
        "current_observed_at": current["observed_at"],
        "current_fresh": current["fresh"],
        "reference_software_observed_at": reference["software_observed_at"],
        "current_software_observed_at": current["software_observed_at"],
        "differences": differences,
        "note": "Diferencias observadas: los inventarios no son exhaustivos; ausencia no demuestra eliminación y coincidencia temporal no acredita causa ni igualdad de dependencias del proyecto.",
    }
