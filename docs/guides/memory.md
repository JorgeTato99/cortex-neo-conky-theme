# Understand memory

```bash
cortex-neo memory
cortex-neo memory --pid 1234 --pid 5678
```

The card shows used, total and available memory. Cache/buffer counters remain separate; do not add them to available to reconstruct total. Linux can reclaim some pages. Occupied swap alone does not prove current memory pressure.

PSI measures time stalled on memory. Zero is a valid observation; unavailable is not zero. Positive PSI indicates observed waits, without identifying a culprit or proving a leak. The command includes 10/60/300-second averages and swap activity deltas. The first sample does not invent a transfer rate.

Application tops group RSS and include shared pages. QEMU is labeled `[VM]`, reflecting host memory used by a guest process. A generic QEMU guest is not automatically Docker Desktop. The VM and containers inside it are not independent host totals.

PSS apportions shared pages; USS measures private pages. These slower reads require explicit PIDs, at most five per request. Denied or vanished processes keep distinct states. The two-second sampler never scans smaps.

Sources: [kernel PSI](https://docs.kernel.org/accounting/psi.html), [proc accounting](https://www.kernel.org/doc/html/latest/filesystems/proc.html), [Docker Desktop VM](https://docs.docker.com/desktop/setup/install/linux/).
