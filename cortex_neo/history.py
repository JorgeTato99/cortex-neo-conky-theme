"""Bounded numerical minute aggregates; process names never enter long history."""

import json
import logging
import math
import time

from .io import atomic, read_json
from .paths import STATE
from .samples import METRICS, compact_point, number

LOG = logging.getLogger(__name__)


def _empty():
    return {"count": 0, "sum": 0, "minimum": None, "maximum": None}


class HistoryStore:
    def __init__(self, state=STATE, *, hours=24):
        if not isinstance(hours, int) or isinstance(hours, bool) or not 0 <= hours <= 168:
            raise ValueError("History retention must be 0–168 hours")
        self.path = state / "history/minutes.json"
        self.hours = hours
        self.minutes = {}
        self.last_time = None
        self.last_flushed = None
        self.flushed_minute = None
        self.retry_after = 0
        self.dirty = False
        self.write_failed = False
        self.clock_regressions = 0
        raw = read_json(self.path, {})
        if isinstance(raw, dict):
            regressions = raw.get("clock_regressions", 0)
            self.clock_regressions = (
                regressions if isinstance(regressions, int) and 0 <= regressions <= 1000000 else 0
            )
        rows = (
            raw.get("minutes", [])
            if isinstance(raw, dict) and raw.get("kind") == "cortex-neo-history"
            else []
        )
        for row in rows[-10081:] if isinstance(rows, list) else []:
            if not isinstance(row, dict):
                continue
            minute, sampled = row.get("minute"), row.get("last_sample")
            if (
                not isinstance(minute, int)
                or isinstance(minute, bool)
                or minute < 0
                or minute % 60
                or number(sampled) is None
                or not minute <= sampled < minute + 60
            ):
                continue
            metrics = {}
            incoming = row.get("metrics", {})
            incoming = incoming if isinstance(incoming, dict) else {}
            for key in METRICS:
                item = incoming.get(key, {})
                item = item if isinstance(item, dict) else {}
                count = item.get("count")
                valid = (
                    isinstance(count, int) and not isinstance(count, bool) and 0 < count <= 1000000
                )
                valid = valid and all(
                    number(item.get(field)) is not None for field in ("sum", "minimum", "maximum")
                )
                metrics[key] = (
                    {field: item[field] for field in ("count", "sum", "minimum", "maximum")}
                    if valid
                    else _empty()
                )
            self.minutes[minute] = {"minute": minute, "last_sample": sampled, "metrics": metrics}
            self.last_time = max(self.last_time if self.last_time is not None else sampled, sampled)

    def record(self, raw):
        if not self.hours:
            return False
        point = compact_point(raw)
        if point is None:
            return False
        now = point["time"]
        if self.last_time is not None and now <= self.last_time:
            self.clock_regressions += int(now < self.last_time)
            return False
        minute = int(now // 60) * 60
        bucket = self.minutes.setdefault(
            minute,
            {"minute": minute, "last_sample": now, "metrics": {key: _empty() for key in METRICS}},
        )
        for key in METRICS:
            value = point[key]
            item = bucket["metrics"][key]
            if value is None or not math.isfinite(item["sum"] + value):
                continue
            item["count"] += 1
            item["sum"] += value
            item["minimum"] = value if item["minimum"] is None else min(item["minimum"], value)
            item["maximum"] = value if item["maximum"] is None else max(item["maximum"], value)
        bucket["last_sample"] = self.last_time = now
        cutoff = int((now - self.hours * 3600) // 60) * 60
        self.minutes = {key: value for key, value in self.minutes.items() if key >= cutoff}
        self.dirty = True
        self.flush()
        return True

    def flush(self, *, force=False):
        if not self.hours or not self.dirty:
            return False
        if not force and self.last_time < self.retry_after:
            return False
        minute = int(self.last_time // 60) * 60
        if (
            not force
            and self.last_flushed is not None
            and self.last_time - self.last_flushed < 60
            and minute == self.flushed_minute
        ):
            return False
        payload = {
            "kind": "cortex-neo-history",
            "format_version": 1,
            "minutes": [self.minutes[key] for key in sorted(self.minutes)],
            "clock_regressions": self.clock_regressions,
        }
        try:
            atomic(self.path, json.dumps(payload, allow_nan=False, separators=(",", ":")))
        except OSError:
            self.write_failed = True
            self.retry_after = self.last_time + 60
            LOG.warning("History publication unavailable; retaining bounded aggregates in memory")
            return False
        self.last_flushed, self.flushed_minute = self.last_time, minute
        self.dirty = self.write_failed = False
        return True

    def query(self, *, now=None, hours=None):
        now = time.time() if now is None else now
        hours = (self.hours or 24) if hours is None else hours
        if not isinstance(hours, int) or isinstance(hours, bool) or not 1 <= hours <= 168:
            raise ValueError("Choose a history window of 1–168 hours")
        effective = min(hours, self.hours) if self.hours else hours
        cutoff = int((now - effective * 3600) // 60) * 60
        rows = []
        for minute, bucket in sorted(self.minutes.items()):
            if not cutoff <= minute <= now:
                continue
            metrics = {}
            for key, item in bucket["metrics"].items():
                metrics[key] = {
                    "count": item["count"],
                    "minimum": item["minimum"],
                    "maximum": item["maximum"],
                    "average": item["sum"] / item["count"] if item["count"] else None,
                }
            rows.append({"minute": minute, "metrics": metrics})
        return {
            "kind": "cortex-neo-history-query",
            "recording_enabled": bool(self.hours),
            "retention_hours": self.hours,
            "requested_hours": hours,
            "latest_sample": self.last_time,
            "clock_regressions": self.clock_regressions,
            "write_failed": self.write_failed,
            "minutes": rows,
            "note": "Only observed values contribute; missing minutes are gaps; persistence can lag by one minute",
        }
