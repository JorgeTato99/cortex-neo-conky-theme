# Architecture and maintenance

Python discovers capabilities and samples once per user; independent Conky windows draw cards through shared Lua callbacks. `cortex_neo/telemetry.py` owns collection, `supervisor.py` owns card processes, `layout.py` calculates geometry, and `render.py` generates staged configurations. `theme/cards/` is maintained source; generated `.conf` files are replaceable cache.

## Invariants

Missing optional facts are omitted or unavailable, never fabricated as zero. Intel frequency remains MHz. CPU top processes normalize per-core values to machine capacity for the card. Memory tops are grouped RSS including shared pages. Absent languages produce no empty heading. Weather requires a manually configured city and has no automatic fallback.

Code, personal config, cache and private state use separate XDG locations. Process arguments, environments and project source are outside normal telemetry. Exporters select fields, rather than copying snapshots and trying to erase secrets. Presentation flags are data, directly checked by Lua even if the sampler stalls; invalid flags retain hiding.

| Operation | Cadence |
|---|---|
| CPU/RAM/processes/GPU/network rates/filesystem usage | 2 seconds |
| Network route and Docker worker | 15 seconds |
| Disk inventory / manual city config | 30 seconds, also mount changes |
| OS metadata | 60 seconds |
| Installed versions | Startup and hourly |
| Weather | 15 minutes; 5-minute error retry |
| Geometry/preferences/capability signature | 10 seconds |
| Numeric minute aggregates | Sample every 2 seconds, publish per minute/normal stop |
| Font resolution | Cached per process/profile |
| PSS/USS, tasks, incidents, baselines and reports | Explicit request only |

Mount fingerprints read small `/proc/self/mountinfo` device records, excluding noisy Docker overlays. Mount changes refresh disks before usage sampling; periodic inventory finds newly attached unmounted devices. Slow weather/version/Docker queries are bounded/background work, without blocking the hot path. Rustup and Go queries disable automatic downloads.

Publication uses distinct temporary files and atomic replace. A user lock prevents duplicate collectors. Short history is bounded to 121 samples. Snapshots older than ten seconds visibly become stale. Expected optional failures avoid card tracebacks; unexpected errors enter the journal. Software timestamps remain independent from CPU timestamps.

Each complete generation is staged before owned windows are replaced; the supervisor validates actual Xft heights and retains three generations. It never kills unrelated Conky windows. Lua payload omits JSON history unused by native graphs. State retains bounded numeric aggregates and explicit private records; source fingerprints exclude private configuration, environments and OS packages.

## Style and localization

Use UTF-8/LF, four spaces, Python snake_case and Ruff, Lua StyLua, English comments/docstrings explaining non-obvious decisions. English is the primary documentation/source language; `docs/es/` and shared JSON catalogs maintain Spanish in the same branch. New text must preserve placeholders in both catalogs. See [localization](localization.md).

References: [Conky configuration](https://conky.cc/config_settings), [GDK work areas](https://docs.gtk.org/gdk3/method.Monitor.get_workarea.html), [XDG specification](https://specifications.freedesktop.org/basedir/latest/), [Rustup environment](https://rust-lang.github.io/rustup/environment-variables.html), [Go toolchains](https://go.dev/doc/toolchain).
