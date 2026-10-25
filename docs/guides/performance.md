# Measure dashboard overhead

```bash
cortex-neo performance --seconds 15
```

This observes the two CORTEX user services and their descendants over 2–60 seconds. It does not inspect arguments, environments or unrelated processes, nor change resource limits or collection cadence.

- `cpu_core_percent`: 100 means one fully occupied logical CPU.
- `cpu_machine_percent`: core percentage divided by logical CPU count.
- `rss_bytes` / `peak_rss_bytes`: summed RSS, including shared pages that can be counted repeatedly; not private memory or PSS.
- `payload_bytes`: actual published file sizes at observation time.
- `available: false`: the running installation could not be observed; not zero cost. Brief processes/rebuilds may escape deltas.

Snapshots also expose `collector.sample_ms`, provider timings, interval and overrun. Sampling timing ends before serialization/publication; service CPU measurement includes those operations. Providers not run in a cycle are absent rather than reported as free.

Compare equal windows, display resolution/scaling and workloads. One difference is not a reproducible benchmark. Conky graphs own their short history; historical tool samples stay in JSON and are omitted from the Lua payload read by every card. This reduces data, without promising a specific CPU reduction.
