"""Private data records with explicit ownership, atomic publication and retention."""

import fcntl
import json
import re
import time
import uuid

from .io import atomic, read_json

IDENTIFIER = re.compile(r"[0-9]{8}T[0-9]{6}Z-[0-9a-f]{12}")


def new_identifier(timestamp=None):
    timestamp = time.time() if timestamp is None else timestamp
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(timestamp)) + "-" + uuid.uuid4().hex[:12]


def record_files(folder, kind):
    found = []
    for path in folder.glob("*.json"):
        try:
            if path.is_symlink() or not IDENTIFIER.fullmatch(path.stem):
                continue
            record = read_json(path)
            if (
                isinstance(record, dict)
                and record.get("kind") == kind
                and record.get("id") == path.stem
            ):
                found.append((path.stat().st_mtime_ns, path))
        except OSError:
            continue
    return [path for _, path in sorted(found, key=lambda item: item[0], reverse=True)]


def load_record(folder, identifier, kind):
    if not isinstance(identifier, str) or not IDENTIFIER.fullmatch(identifier):
        raise ValueError("Invalid record identifier")
    path = folder / (identifier + ".json")
    if path.is_symlink():
        raise ValueError("Record symlinks are not followed")
    record = read_json(path)
    if not isinstance(record, dict) or record.get("kind") != kind or record.get("id") != identifier:
        raise ValueError("Record not found or invalid")
    return record


def read_records(folder, kind):
    result = []
    for path in record_files(folder, kind):
        try:
            result.append(load_record(folder, path.stem, kind))
        except ValueError:
            continue
    return result


def save_record(folder, record, kind, *, limit=10, unique_key=None, prune=True):
    if (
        not IDENTIFIER.fullmatch(record.get("id", ""))
        or record.get("kind") != kind
        or not isinstance(limit, int)
        or isinstance(limit, bool)
        or not 1 <= limit <= 50
    ):
        raise ValueError("Invalid owned record or retention limit")
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (folder / ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        existing = read_records(folder, kind)
        if unique_key and any(item.get(unique_key) == record.get(unique_key) for item in existing):
            raise ValueError("A record with that name already exists")
        if not prune and len(existing) >= limit:
            raise ValueError("Record limit reached; export or remove an explicit reference first")
        atomic(
            folder / (record["id"] + ".json"),
            json.dumps(record, ensure_ascii=False, allow_nan=False),
        )
        if prune:
            for path in record_files(folder, kind)[limit:]:
                path.unlink(missing_ok=True)


def remove_record(folder, identifier, kind):
    if not folder.is_dir():
        raise ValueError("Record not found")
    with (folder / ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        load_record(folder, identifier, kind)
        (folder / (identifier + ".json")).unlink()
