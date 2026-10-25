"""Optional GPU providers: NVIDIA NVML and kernel DRM sensors.

Intel clock frequency is not utilization. Each metric retains its own name and
unit, and an unsupported sensor is omitted rather than converted to zero.
"""

import math
import time
from pathlib import Path

from .io import command, read, safe
from .system import fields

try:
    import pynvml as nvml
except ImportError:
    nvml = None


def sensor(path, divisor=1):
    try:
        value = float(read(path)) / divisor
        return value if math.isfinite(value) and value >= 0 else None
    except (TypeError, ValueError):
        return None


class GPU:
    """Reuse one NVML handle; missing libraries/drivers never stop CPU sampling."""

    def __init__(self, model="", drm_root=Path("/sys/class/drm")):
        self.device = None
        self.initialized = False
        self.retry = 0
        cards = [p for p in drm_root.glob("card[0-9]*") if "-" not in p.name]
        cards.sort(key=lambda p: read(p / "device/vendor") != "0x10de")
        self.card = cards[0] if cards else None
        self.vendor = read(self.card / "device/vendor") if self.card else ""
        self.metadata = {"model": model} if model else {}
        if self.card:
            driver = (self.card / "device/driver").resolve().name
            if driver and driver != "driver":
                self.metadata["driver"] = driver
            if not self.metadata.get("model"):
                maker = {"0x8086": "Intel", "0x1002": "AMD", "0x10de": "NVIDIA"}.get(self.vendor)
                if maker:
                    self.metadata["model"] = "GPU " + maker

    def generic(self):
        result = dict(self.metadata)
        if not self.card:
            return result
        for key, paths in {
            "load": ["device/gpu_busy_percent"],
            "frequency": ["gt_cur_freq_mhz", "gt/gt0/rps_cur_freq_mhz"],
            "frequency_max": ["gt_max_freq_mhz", "gt/gt0/rps_max_freq_mhz"],
            "used": ["device/mem_info_vram_used"],
            "total": ["device/mem_info_vram_total"],
        }.items():
            for path in paths:
                if (value := sensor(self.card / path)) is not None:
                    result[key] = value
                    break
        for path in (self.card / "device/hwmon").glob("hwmon*/temp1_input"):
            if (value := sensor(path, 1000)) is not None:
                result["temperature"] = value
                break
        if result.get("total") and result.get("used") is not None:
            result["memory_load"] = result["used"] * 100 / result["total"]
        return result

    def sample(self):
        result = self.generic()
        if nvml is None or self.vendor != "0x10de" or time.monotonic() < self.retry:
            return result
        try:
            if self.device is None:
                nvml.nvmlInit()
                self.initialized = True
                self.device = nvml.nvmlDeviceGetHandleByIndex(0)
                bus = safe(nvml.nvmlDeviceGetPciInfo(self.device).busId)
                domain, slot = bus.split(":", 1)
                details = fields(
                    command(["lspci", "-D", "-vmm", "-s", f"{int(domain, 16):04x}:{slot.lower()}"])
                    or ""
                )
                self.metadata.update(
                    model=safe(nvml.nvmlDeviceGetName(self.device)),
                    maker=safe(details.get("SVendor")),
                    driver=safe(nvml.nvmlSystemGetDriverVersion()),
                )
            result.update(self.metadata)
            memory = nvml.nvmlDeviceGetMemoryInfo(self.device)
            result.update(
                used=memory.used,
                total=memory.total,
                memory_load=memory.used * 100 / memory.total if memory.total else None,
            )
            for name, reader in {
                "load": lambda: nvml.nvmlDeviceGetUtilizationRates(self.device).gpu,
                "temperature": lambda: nvml.nvmlDeviceGetTemperature(
                    self.device, nvml.NVML_TEMPERATURE_GPU
                ),
            }.items():
                try:
                    result[name] = reader()
                except nvml.NVMLError:
                    pass
        except (nvml.NVMLError, OSError, TypeError, ValueError):
            if self.initialized:
                try:
                    nvml.nvmlShutdown()
                except nvml.NVMLError:
                    pass
            self.initialized = False
            self.device = None
            self.retry = time.monotonic() + 30
        return result
