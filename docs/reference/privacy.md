# Data, location and captures

The local sampler observes hardware models/capacity/sensors, hostname, processes, mount paths, network interface, installed versions and configured local Docker endpoints. Optional SMBIOS access uses noninteractive authorized `sudo -n dmidecode`; denial omits facts without prompting.

Snapshots under `~/.cache/cortex-neo/` are private operational data, not public attachments. Preferences and city live in `~/.config/cortex-neo/`. Minute history under XDG state stores only numeric aggregates with default 24-hour retention. Explicit incidents can include process names and private labels; their export selects numeric fields. Task records store labels/resources, excluding argv, environment, cwd and output. Baseline names are private and omitted from exports.

Presentation hides selected dashboard fields through a runtime flag, without deleting data or stopping collection. Support reports allowlist fields and omit raw diagnostics. Every export is printed for review; none is sent automatically.

## Manual location only

The checked-in location example has empty city/coordinates. Manually choose a city and public city-center coordinates. Avoid exact home coordinates. **Never add GeoIP, GPS, GeoClue, SSID/BSSID scanning or any automatic location provider/fallback.** Without valid manual settings there is no weather request or weather card.

Open-Meteo receives the configured coordinates and ordinary request network information. Preventing automatic location collection is not a promise of network anonymity from the weather provider. Weather attribution remains visible.

## Screenshots and public files

The normal GNOME screenshot portal can require session permission even with sudo. Captures go under `~/.local/state/cortex-neo/`; review hostnames, processes, city, versions and other windows before sharing. Published examples and palette galleries use authorized native desktop captures. Headless CI artifacts use synthetic fixtures and are separate from those images. Source examples contain no personal settings, SSH/LUKS keys, tokens, remote endpoints or administrative backups.

`temp/` is excluded from Git. Local research, old repository recovery bundles and deployment evidence stay there. Runtime snapshots/history are also ignored. See [sharing](../guides/sharing.md), [incidents](../guides/incidents.md), [tasks](../guides/tasks.md) and [history](../guides/history.md) for retention and scope.
