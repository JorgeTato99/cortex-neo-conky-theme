# Installation

Use a graphical Linux session, user systemd and the distribution's Python 3.11 or newer. Automatic package profiles cover Ubuntu 24.04/26.04 and Debian 12/13. See [compatibility](../reference/compatibility.md) for evidence limits.

Download and extract the [source ZIP](https://github.com/JorgeTato99/cortex-neo-conky-theme/archive/refs/heads/main.zip), or clone the repository. In that directory run:

```bash
bash scripts/install.sh
```

Run as your desktop user, **without sudo**. Only apt operations request elevation. Permanent passwordless sudo is unnecessary. The installer prepares Conky with Lua/X11, GTK bindings, fonts, XWayland and bounded system-query tools. It does not install Docker, editors, compilers or GPU drivers.

The runtime uses `/usr/bin/python3` in its own virtual environment with system GTK bindings. It never replaces the OS Python or borrows a project's uv/pyenv environment. Each immutable release has a separate environment; preparation precedes switching the active installation. Failed activation restores the previous release and controls.

```bash
bash scripts/install.sh --dry-run
bash scripts/install.sh --skip-system-deps
bash scripts/install.sh --no-start
bash scripts/install.sh --location-file=/path/manual-city.json
~/.local/bin/cortex-neo doctor
```

`--dry-run` changes nothing. `--skip-system-deps` requires dependencies already present and still runs diagnosis. On other distributions this is experimental. `--no-start` enables startup for the next graphical session; it rejects an already active installation rather than replace running code unsafely.

A location file is copied only when no personal location exists. No location discovery occurs. Weather requests require valid manual city coordinates. SMBIOS queries are optional and never create sudo rules.

Without a desktop, use `doctor --dependencies-only`. Warnings describe optional capabilities or font fallback; errors produce a nonzero exit status. Use `--migrate-legacy` only for an old conky-neon installation. Other Conky processes are never killed by process name.
