"""Cheap host memory signals and explicitly requested process footprints."""
from cortex_neo.i18n import tr
import math
import time
from pathlib import Path
import psutil
from .io import read, safe

def parse_pressure(text):
    result = {}
    for line in text.splitlines()[:8]:
        parts = line.split()
        if not parts or parts[0] not in ('some', 'full'):
            continue
        try:
            values = dict((part.split('=', 1) for part in parts[1:]))
            averages = {key: float(values[key]) for key in ('avg10', 'avg60', 'avg300')}
            total = int(values['total'])
            if total < 0 or not all((math.isfinite(n) and 0 <= n <= 100 for n in averages.values())):
                continue
            result[parts[0]] = {**averages, 'total_us': total}
        except (ValueError, KeyError):
            continue
    return result or None

class MemoryMonitor:
    """Read only small global counters on the hot path, never process smaps."""

    def __init__(self, pressure_root=Path('/proc/pressure'), swap_reader=psutil.swap_memory):
        self.root = Path(pressure_root)
        self.swap_reader = swap_reader
        self.previous = None

    def sample(self, memory, now=None):
        now = time.monotonic() if now is None else now
        swap = dict(total=None, used=None, in_bytes_per_second=None, out_bytes_per_second=None)
        try:
            current = self.swap_reader()
            swap.update(total=current.total, used=current.used)
            if self.previous and now > self.previous[0]:
                elapsed = now - self.previous[0]
                if current.sin >= self.previous[1] and current.sout >= self.previous[2]:
                    swap['in_bytes_per_second'] = (current.sin - self.previous[1]) / elapsed
                    swap['out_bytes_per_second'] = (current.sout - self.previous[2]) / elapsed
            self.previous = (now, current.sin, current.sout)
        except (OSError, AttributeError, psutil.Error):
            self.previous = None
        return dict(available=getattr(memory, 'available', None), cached=getattr(memory, 'cached', None), buffers=getattr(memory, 'buffers', None), swap=swap, pressure=parse_pressure(read(self.root / 'memory')))

def explain_memory(ram):
    pressure = ram.get('pressure') or {}
    average = (pressure.get('some') or {}).get('avg10')
    if average is None:
        return tr('Memory PSI unavailable; used percentage alone does not prove pressure.')
    if average == 0:
        return tr('No memory stalls observed in the ten-second PSI average.')
    return tr('Observed memory stalls: {p0:.2f}% of time in the ten-second PSI average.').format(p0=average)

def memory_details(pids, *, factory=psutil.Process):
    """A slower PSS/USS read is opt-in and bounded to five explicit identities."""
    if len(pids) > 5 or any((not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0 for pid in pids)):
        raise ValueError('Choose at most five positive PIDs')
    rows = []
    for pid in dict.fromkeys(pids):
        try:
            process = factory(pid)
            info = process.memory_full_info()
            item = {'pid': pid, 'name': safe(process.name())[:64], 'status': 'ok'}
            for field in ('rss', 'pss', 'uss'):
                value = getattr(info, field, None)
                if value is not None:
                    item[field + '_bytes'] = value
            rows.append(item)
        except psutil.AccessDenied:
            rows.append({'pid': pid, 'status': 'denied'})
        except psutil.NoSuchProcess:
            rows.append({'pid': pid, 'status': 'gone'})
        except (OSError, AttributeError):
            rows.append({'pid': pid, 'status': 'unavailable'})
    return rows
