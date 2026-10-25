"""Docker projects stay within their engine and never expose inspection secrets."""

import json
import socket
import tempfile
import threading
import unittest
from pathlib import Path

from cortex_neo.docker import DockerMonitor, collect_docker, socket_json


class DockerTests(unittest.TestCase):
    def test_real_socket_get_status_and_response_size_limit(self):
        for status, length, error in (
            (200, 2, None),
            (500, 2, OSError),
            (200, 2**20 + 1, ValueError),
        ):
            with (
                self.subTest(status=status, length=length),
                tempfile.TemporaryDirectory() as directory,
            ):
                path = str(Path(directory) / "docker.sock")
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
                    server.bind(path)
                    server.listen(1)
                    server.settimeout(2)
                    received = []

                    def serve(server=server, received=received, status=status, length=length):
                        connection, _ = server.accept()
                        with connection:
                            received.append(connection.recv(8192))
                            connection.sendall(
                                f"HTTP/1.1 {status} Result\r\nContent-Length: {length}\r\nConnection: close\r\n\r\n".encode()
                                + b"{}"
                            )

                    worker = threading.Thread(target=serve, daemon=True)
                    worker.start()
                    try:
                        if error:
                            with self.assertRaises(error):
                                socket_json(path, "/info")
                        else:
                            self.assertEqual(socket_json(path, "/info"), {})
                    finally:
                        worker.join(3)
                    self.assertFalse(worker.is_alive())
                    self.assertTrue(received[0].startswith(b"GET /info HTTP/1.1\r\n"))

    def test_compose_contexts_ports_and_private_fields(self):
        def request(endpoint, target):
            if target == "/info":
                return {"ContainersRunning": 1, "ServerVersion": "29.0"}
            return [
                {
                    "Id": "a" * 64,
                    "Names": ["/frontend"],
                    "State": "running",
                    "Labels": {
                        "com.docker.compose.project": "demo",
                        "com.docker.compose.service": "web",
                        "secret": "PRIVATE-LABEL",
                    },
                    "Env": ["PRIVATE-ENV"],
                    "Command": "PRIVATE-COMMAND",
                    "Ports": [{"PrivatePort": 80, "PublicPort": 8080, "Type": "tcp"}],
                }
            ]

        result = collect_docker(
            {"default": "engine", "desktop-linux": "desktop"}, request=request, now=100
        )
        self.assertEqual(set(result), {"default", "desktop-linux"})
        for context in ("default", "desktop-linux"):
            group = result[context]["projects"][0]
            self.assertEqual(group["name"], "demo")
            self.assertEqual(group["services"][0]["service"], "web")
            self.assertEqual(group["services"][0]["ports"], ["8080:80/tcp"])
        self.assertNotIn("PRIVATE", json.dumps(result))

    def test_endpoint_failure_unlabelled_and_large_results(self):
        def request(endpoint, target):
            if endpoint == "offline":
                raise OSError("offline")
            if target == "/info":
                return {"ContainersRunning": 0}
            return [{"Names": ["solo"], "State": "exited", "Ports": [{"PrivatePort": -1}]}] * 101

        result = collect_docker(
            {"default": "offline", "desktop-linux": "live"}, request=request, now=100
        )
        self.assertEqual(result["default"]["status"], "unavailable")
        self.assertNotIn("running", result["default"])
        desktop = result["desktop-linux"]
        self.assertEqual(desktop["running"], 0)
        self.assertTrue(desktop["truncated"])
        self.assertEqual(len(desktop["projects"][0]["services"]), 100)
        self.assertFalse(desktop["projects"][0]["compose"])

    def test_slow_query_never_blocks_the_sampling_thread(self):
        started, release = threading.Event(), threading.Event()

        def query(endpoints):
            started.set()
            release.wait(2)
            return {"default": {"running": 1}}

        monitor = DockerMonitor(query=query)
        try:
            self.assertTrue(monitor.refresh({"default": "socket"}))
            self.assertTrue(started.wait(1))
            self.assertEqual(monitor.snapshot(), {})
            self.assertFalse(monitor.refresh({"default": "socket"}))
        finally:
            release.set()
            monitor.thread.join(3)
        self.assertEqual(monitor.snapshot()["default"]["running"], 1)
