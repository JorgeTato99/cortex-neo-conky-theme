"""Read-only Unix-socket Docker queries, bounded results and asynchronous refresh."""

import http.client
import json
import logging
import socket
import threading
import time

from .io import safe

LOG = logging.getLogger(__name__)
MAX_BODY = 1024 * 1024
MAX_CONTAINERS = 100
CONTAINERS_PATH = "/containers/json?all=1&limit=101"


def socket_json(endpoint, target):
    if target not in ("/info", CONTAINERS_PATH):
        raise ValueError("Only the two read-only inventory resources are allowed")
    deadline = time.monotonic() + 2
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(1)
        connection.connect(endpoint)
        connection.sendall(
            f"GET {target} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n".encode("ascii")
        )
        response = http.client.HTTPResponse(connection)
        try:
            response.begin()
            if response.status != 200:
                raise OSError("Docker inventory endpoint failed")
            length = response.getheader("Content-Length")
            if length is not None and int(length) > MAX_BODY:
                raise ValueError("Docker response exceeds the size limit")
            body = bytearray()
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("Docker query deadline exceeded")
                connection.settimeout(min(1, remaining))
                chunk = response.read1(min(8192, MAX_BODY + 1 - len(body)))
                if not chunk:
                    break
                body.extend(chunk)
                if len(body) > MAX_BODY:
                    raise ValueError("Docker response exceeds the size limit")
            return json.loads(body)
        finally:
            response.close()


def _text(value, limit=64):
    return safe(value)[:limit] if isinstance(value, str) else ""


def _container(raw):
    labels = raw.get("Labels")
    labels = labels if isinstance(labels, dict) else {}
    project = _text(labels.get("com.docker.compose.project"))
    service = _text(labels.get("com.docker.compose.service"))
    names = raw.get("Names")
    names = names if isinstance(names, list) else []
    ports = []
    candidates = raw.get("Ports")
    for port in candidates[:16] if isinstance(candidates, list) else []:
        if not isinstance(port, dict):
            continue
        private, public = port.get("PrivatePort"), port.get("PublicPort")
        kind = port.get("Type", "tcp")
        if (
            isinstance(private, bool)
            or not isinstance(private, int)
            or not 1 <= private <= 65535
            or kind not in ("tcp", "udp", "sctp")
        ):
            continue
        prefix = (
            f"{public}:"
            if isinstance(public, int) and not isinstance(public, bool) and 1 <= public <= 65535
            else ""
        )
        ports.append(f"{prefix}{private}/{kind}")
    return project, {
        "id": _text(raw.get("Id"), 12),
        "name": _text(names[0]).lstrip("/") if names else "sin nombre",
        "service": service,
        "state": _text(raw.get("State"), 24) or "unknown",
        "ports": ports,
    }


def collect_docker(endpoints, *, request=socket_json, now=None):
    result = {}
    for context, endpoint in endpoints.items():
        if context not in ("default", "desktop-linux"):
            continue
        try:
            info = request(endpoint, "/info")
            rows = request(endpoint, CONTAINERS_PATH)
            if not isinstance(info, dict) or not isinstance(rows, list):
                raise ValueError("Invalid Docker inventory response")
            groups = {}
            for raw in rows[:MAX_CONTAINERS]:
                if not isinstance(raw, dict):
                    continue
                project, row = _container(raw)
                group = groups.setdefault(
                    project,
                    {
                        "name": project or "Sin proyecto Compose",
                        "compose": bool(project),
                        "services": [],
                    },
                )
                group["services"].append(row)
            running = info.get("ContainersRunning")
            result[context] = {
                "status": "ok",
                "sampled_at": time.time() if now is None else now,
                "running": running
                if isinstance(running, int) and not isinstance(running, bool) and running >= 0
                else None,
                "version": _text(info.get("ServerVersion")),
                "projects": sorted(groups.values(), key=lambda group: group["name"]),
                "project_count": sum(group["compose"] for group in groups.values()),
                "truncated": len(rows) > MAX_CONTAINERS,
            }
        except (OSError, ValueError, http.client.HTTPException):
            result[context] = {
                "status": "unavailable",
                "sampled_at": time.time() if now is None else now,
            }
    return result


class DockerMonitor:
    """One worker publishes a complete result; slow daemons never stall live CPU/RAM."""

    def __init__(self, query=collect_docker):
        self.query = query
        self.thread = None
        self.value = {}

    def refresh(self, endpoints):
        if self.thread is not None and self.thread.is_alive():
            return False

        def worker():
            try:
                self.value = self.query(dict(endpoints))
            except Exception:
                LOG.exception("Docker inventory failed")
                self.value = {}

        self.thread = threading.Thread(target=worker, name="docker-inventory", daemon=True)
        self.thread.start()
        return True

    def snapshot(self):
        return dict(self.value)
