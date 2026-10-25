"""Explicit incident captures with bounded windows, retention and safe exports."""

import time
import uuid
from itertools import pairwise

from .io import read_json, safe
from .paths import CACHE, STATE
from .records import load_record, read_records, save_record
from .samples import METRICS, compact_point


def capture_incident(
    label="",
    *,
    before=240,
    after=60,
    cache=CACHE,
    state=STATE,
    max_records=10,
    clock=time.time,
    monotonic=time.monotonic,
    sleep=time.sleep,
):
    if not 0 <= before <= 240 or not 0 <= after <= 60 or not 1 <= max_records <= 50:
        raise ValueError("Windows: 0–240 seconds before, 0–60 after; retention: 1–50 records")
    started, deadline = clock(), monotonic() + after
    points = {}
    interrupted = False
    try:
        while True:
            snapshot = read_json(cache / "dashboard.json", {})
            history = snapshot.get("history", []) if isinstance(snapshot, dict) else []
            now = clock()
            for raw in history[-121:] if isinstance(history, list) else []:
                point = compact_point(raw)
                if point and started - before <= point["time"] <= min(now, started + after + 5):
                    points[point["time"]] = point
            remaining = deadline - monotonic()
            if remaining <= 0:
                break
            sleep(min(2, remaining))
    except KeyboardInterrupt:
        interrupted = True
    samples = sorted(points.values(), key=lambda point: point["time"])[-200:]
    identifier = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(started)) + "-" + uuid.uuid4().hex[:12]
    record = {
        "kind": "cortex-neo-incident",
        "format_version": 1,
        "id": identifier,
        "label": safe(label)[:80],
        "started_at": started,
        "finished_at": clock(),
        "requested_before_seconds": before,
        "requested_after_seconds": after,
        "status": "interrupted" if interrupted else ("complete" if samples else "no_data"),
        "points": samples,
        "gaps": [
            {"from": left["time"], "to": right["time"]}
            for left, right in pairwise(samples)
            if right["time"] - left["time"] > 4.5
        ],
        "coverage": {
            "first_sample": samples[0]["time"] if samples else None,
            "last_sample": samples[-1]["time"] if samples else None,
            "has_samples_since_marker": any(point["time"] >= started for point in samples),
        },
        "accounting": "global CPU is machine percent; cpu_top is one-core percent; process RSS includes shared pages",
    }
    folder = state / "incidents"
    save_record(folder, record, "cortex-neo-incident", limit=max_records)
    return record


def load_incident(identifier, *, state=STATE):
    return load_record(state / "incidents", identifier, "cortex-neo-incident")


def list_incidents(*, state=STATE):
    result = []
    for record in read_records(state / "incidents", "cortex-neo-incident"):
        result.append({key: record.get(key) for key in ("id", "label", "started_at", "status")})
    return result


def public_incident(record):
    """Export metric names only; labels, process names and disk identities stay local."""
    points = record.get("points", [])
    selected = []
    for raw in points[:200] if isinstance(points, list) else []:
        point = compact_point(raw)
        if point:
            selected.append({key: point[key] for key in ("time", *METRICS)})
    return {
        "kind": "cortex-neo-incident-public",
        "format_version": 1,
        "points": selected,
        "note": "Temporal correlation does not establish a cause; private labels and process/disk names omitted",
    }
