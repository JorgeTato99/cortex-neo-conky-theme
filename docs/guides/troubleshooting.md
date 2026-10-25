# Troubleshooting

```bash
cortex-neo doctor
cortex-neo version --format json
cortex-neo status
journalctl --user -u cortex-neo -u cortex-neo-metrics --since "10 minutes ago"
```

Run as the desktop user. The theme requires a live graphical session, X11/XWayland, Lua-enabled Conky, GTK bindings and a user systemd bus. Sudo does not create the correct graphical session environment. Use `doctor --dependencies-only` for headless dependency diagnosis.

If cards are absent, check both units and journal errors before launching generic Conky, which shows its unrelated default black panel. Restart only this project's service with `cortex-neo restart`; avoid killing all Conky processes by name. A sample older than ten seconds displays stale status rather than fake zeros.

A missing sensor, compiler or Docker endpoint is an optional capability. Inspect `inventory` and `containers`; do not install unrelated tools merely to fill rows. Font substitution is checked with fontconfig. Try `--font dejavu`, compact profile or comfortable density for readability, and report logical work area plus physical resolution/desktop scaling.

If an update fails, the installer restores the previous runtime. Do not remove its active environment. See [lifecycle](../getting-started/updates-and-uninstall.md). If reporting a problem, use the issue form and review `report` output; avoid attaching raw cache, personal settings or unreviewed screenshots.
