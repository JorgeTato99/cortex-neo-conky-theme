"""Linux hardware discovery; optional SMBIOS/PCI tools may be absent."""

import glob
import json
import os
import platform
import re
import socket
from pathlib import Path

from .io import atomic, command, read, safe
from .paths import CACHE


def write(name, content):
    path = CACHE / name
    if read(path) != content.strip():
        atomic(path, content + "\n")


def fields(block):
    return {
        key.strip(): value.strip()
        for line in block.splitlines()
        if ":" in line
        for key, value in [line.split(":", 1)]
    }


def inventory():
    cpu = fields(read("/proc/cpuinfo").split("\n\n")[0])
    cpus = glob.glob("/sys/devices/system/cpu/cpu[0-9]*")
    cores = set()
    for path in cpus:
        package = read(Path(path) / "topology/physical_package_id")
        core = read(Path(path) / "topology/core_id")
        if package and core:
            cores.add((package, core))
    # Noninteractive SMBIOS is optional: denied privileges omit these fields.
    dmi = command(["sudo", "-n", "/usr/sbin/dmidecode", "--type", "17"], timeout=5)
    modules = []
    for block in re.split(r"^Memory Device\s*$", dmi or "", flags=re.MULTILINE)[1:]:
        module = fields(block)
        if re.match(r"^\d+ (?:MB|GB|TB)$", module.get("Size", "")):
            modules.append(module)
    models = []
    for module in modules:
        model = module.get("Part Number", "Unknown").strip()
        maker = module.get("Manufacturer", "Unknown").strip()
        # Some firmware reports an encoded JEDEC value rather than a brand name.
        if re.fullmatch(r"(?:0x)?[0-9a-fA-F]{8,}", maker):
            maker = ""
        if (
            maker.lower() not in ("unknown", "not specified", "")
            and maker.lower() not in model.lower()
        ):
            model = maker + " " + model
        if model.lower() not in ("unknown", "not specified", "") and model not in models:
            models.append(model)
    unavailable = ("", "Unknown", "Not Specified", "N/D", None)
    types = sorted({m.get("Type") for m in modules if m.get("Type") not in unavailable})
    speeds = sorted(
        {
            m.get("Configured Memory Speed") or m.get("Speed")
            for m in modules
            if (m.get("Configured Memory Speed") or m.get("Speed")) not in unavailable
        }
    )
    sizes = {m["Size"] for m in modules}
    capacity_mib = 0
    for module in modules:
        number, unit = module["Size"].split()
        capacity_mib += int(number) * {"MB": 1, "GB": 1024, "TB": 1024**2}[unit]
    module_text = (
        f"{len(modules)}x{next(iter(sizes))}" if len(sizes) == 1 else f"{len(modules)} modulos"
    )
    capacity = f"{capacity_mib / 1024:g} GB ({module_text})" if modules else ""
    gpu_model = ""
    for block in (command(["lspci", "-D", "-vmm"]) or "").split("\n\n"):
        device = fields(block)
        if any(
            kind in device.get("Class", "")
            for kind in ("VGA", "3D controller", "Display controller")
        ):
            gpu_model = safe(device.get("Vendor", "") + " " + device.get("Device", ""))
            break
    result = {
        "cpu_model": safe(cpu.get("model name", platform.processor() or "CPU")),
        "cpu_topology": f"{len(cores)} cores / {len(cpus)} threads"
        if cores
        else f"{os.cpu_count()} threads",
        "cpu_threads": os.cpu_count() or 1,
        "ram_model": safe(" / ".join(models)),
        "ram_capacity": capacity,
        "ram_type": safe(" / ".join(types)),
        "ram_speed": safe(" / ".join(speeds)),
        "gpu_model": gpu_model,
    }
    write("inventory.json", json.dumps(result, ensure_ascii=False, indent=2))
    return result


def disk_inventory():
    result = command(
        [
            "/usr/bin/lsblk",
            "--json",
            "--bytes",
            "--output",
            "NAME,TYPE,SIZE,MODEL,MOUNTPOINTS,TRAN,ROTA",
        ]
    )
    try:
        return json.loads(result)["blockdevices"] if result else []
    except (ValueError, KeyError):
        return []


def mount_signature():
    """Notice block-device mount changes without rescanning hardware every tick.

    Ignore overlay/tmpfs churn from containers. The source, mountpoint and
    filesystem root distinguish mounts, bind mounts and subvolumes.
    """
    signature = []
    for line in read("/proc/self/mountinfo").splitlines():
        fields = line.split()
        try:
            separator = fields.index("-")
            source = fields[separator + 2]
            if source.startswith("/dev/"):
                signature.append((source, fields[4], fields[3]))
        except (ValueError, IndexError):
            continue
    return tuple(sorted(signature))


def mounts(device):
    result = [mount for mount in device.get("mountpoints", []) if mount]
    for child in device.get("children", []):
        result.extend(mounts(child))
    return result


def docker_endpoints():
    endpoints = {}
    for context in ("default", "desktop-linux"):
        value = command(["/usr/bin/docker", "context", "inspect", context])
        try:
            host = json.loads(value)[0]["Endpoints"]["docker"]["Host"] if value else ""
            if host.startswith("unix://"):
                endpoints[context] = host[len("unix://") :]
        except (ValueError, KeyError, IndexError):
            pass
    return endpoints


def ready():
    target = os.environ.get("NOTIFY_SOCKET")
    if target:
        with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as connection:
            connection.connect("\0" + target[1:] if target.startswith("@") else target)
            connection.sendall(b"READY=1")
