# Hourly history

```bash
cortex-neo history
cortex-neo history --hours 6 --format json
cortex-neo configure --history-hours 24
cortex-neo configure --history-hours 0
```

Per-minute aggregates store count, minimum, maximum and mean for CPU, RAM, GPU/VRAM, available memory, swap, pressure and traffic. Percentages remain percentages, memory is bytes, traffic is bytes/second. There are no process names, arguments, hostnames, locations or disk identities.

Default retention is 24 hours; choose 1–168, or zero to disable new observations. Zero does not erase existing records. Retention applies on samples, including the current minute; a stopped program has no extra cleanup service. Settings refresh takes roughly thirty seconds.

Private state lives in `~/.local/state/cortex-neo/history/minutes.json`. Publication occurs on minute transitions, around sixty seconds, and normal shutdown. Sudden power loss can lose the current in-memory minute. Write failures keep bounded in-memory aggregates and expose `write_failed`, with delayed retries.

Each metric has its own observation count; no samples yields null mean. Missing minutes are gaps, not idle intervals. Duplicate/regressive timestamps are ignored, with clock-regression accounting. Text shows the latest twenty observed minutes in local time; JSON returns the selected retained window and extrema. Requesting older hours cannot recover unrecorded samples. Desktop graphs keep their short native history independently.
