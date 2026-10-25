# Capture an incident

```bash
cortex-neo incident --label "slow tests"
cortex-neo incident --label "retrospective only" --after 0
cortex-neo incidents
cortex-neo incident-export --id INCIDENT_ID
```

Capture is explicit and uses the existing sampler cache. `--before` accepts 0–240 seconds; `--after` accepts 0–60. The CLI waits for the after-window; Ctrl+C saves available observations. No second hardware collector runs.

Private records include compact metrics/process tops and your label, but never arguments, environments or file contents. They live under `~/.local/state/cortex-neo/incidents/`, with private permissions, atomic writes and concurrent-operation locking. Retention is ten owned records, each at most two hundred samples; cleanup requires valid ownership markers/identifiers.

Available prehistory depends on sampler uptime. Missing intervals are not invented as zeros. `gaps` marks intervals over 4.5 seconds; `no_data` and `interrupted` remain distinct outcomes. Waiting uses a monotonic clock.

Export selects times and numeric metrics, omitting labels, process names/PIDs and disk identities. Nothing is sent. Global CPU uses machine capacity; process CPU is per-core and RSS includes shared pages. Temporal correlation does not establish cause. Review exports before sharing.
