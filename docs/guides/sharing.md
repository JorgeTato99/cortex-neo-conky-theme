# Presentation mode and support reports

```bash
cortex-neo presentation --on
cortex-neo presentation --on --minutes 30
cortex-neo presentation
cortex-neo presentation --off
cortex-neo report
cortex-neo report --format json
```

Presentation mode hides host identity, process/application names, mount labels, network interface, build details and location/weather on this dashboard. Percentages and graphs remain. It uses a private runtime data flag, without rewriting persistent preferences or stopping collection. Each Lua card reads the flag directly every two seconds, so a stalled collector does not prevent hiding. Invalid/unreadable flags fail closed.

The optional lifetime is 1–480 minutes. Without it, turn the mode off explicitly; runtime cleanup/reboot also removes it. With user lingering, logout alone may not clear runtime state. Existing cache/incident/task records are not erased. Other applications, open windows and old screenshots remain outside this protection.

Support reports allowlist application revision/fingerprint, runtime Python/Conky capabilities, selected diagnostic statuses, theme preferences, work-area size and selected context. Raw diagnostic output, paths, hostnames, process names, project labels and city are omitted. No screenshot is automatically attached and nothing is sent.

Read output before sharing. Screenshots may still expose unrelated content. Native screenshot portals can request desktop permission even when the SSH account has sudo. See [privacy](../reference/privacy.md).
