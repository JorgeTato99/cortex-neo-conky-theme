# Named observations and comparisons

```bash
cortex-neo baseline-save --name frontend-working
cortex-neo baselines
cortex-neo compare --name frontend-working
cortex-neo baseline-export --name frontend-working > ~/reference.json
cortex-neo compare --input ~/other-host.json
cortex-neo baseline-remove --name frontend-working
```

A baseline stores selected OS/kernel/architecture, CPU/RAM, GPU model/driver and observed sensors, Docker contexts and tool versions. It excludes hostname, processes, location and project paths. Your chosen name remains private and is omitted from export. GPU driver may be a module name or version, depending on provider.

Names are never overwritten, including case-only changes. Twenty private baselines fit under `~/.local/state/cortex-neo/baselines/`; at the limit, explicitly export/remove one. There is no automatic pruning.

To compare machines, manually transfer `cortex-neo context --format json` output, then use `compare --input`. There is no network discovery/synchronization. `baseline-save --name NAME --input FILE` stores an imported context.

Only selected version-one contexts up to 1 MiB are accepted. Inventories describe observations, not exhaustive installations; partial queries yield `partial_inventory`, and missing versions do not prove removal. Software inventory age is separate from live CPU age; older contexts without that timestamp report unknown age.

Equal global versions do not establish equal project dependency environments. Temporal coincidence does not establish causality.
