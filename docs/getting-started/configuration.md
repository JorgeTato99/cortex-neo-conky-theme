# Configuration

Personal settings live in `~/.config/cortex-neo/`, respecting absolute XDG overrides. Updates preserve them. Generated cache files are not editable sources.

```bash
cortex-neo configure --language en --palette blue --font ubuntu
cortex-neo configure --detail-level essential
cortex-neo configure --detail-level full
cortex-neo configure --opacity 0.85 --anchor right
```

`settings.json` controls language, font, detail, layout and visible cards. `theme.json` controls palette, opacity and optional colors. See the maintained [settings example](../../config/settings.example.json) and [theme example](../../config/theme.example.json). Manual edits are detected within approximately ten seconds; invalid values fall back safely. CLI validation rejects invalid choices before writing. Unknown personal fields survive updates.

## Appearance

Ten complete palettes: `blue`, `teal`, `green`, `yellow`, `orange`, `red`, `pink`, `purple`, `slate`, `brown`. Every variant defines text, primary, secondary, muted, border, accent, warning, graph and background colors. Six-digit hexadecimal overrides are supported. Foregrounds are adapted to this dark design rather than copying solid Ubuntu button backgrounds. Old `neon`, `contrast` and `amber` settings remain readable for migration.

Fonts: `ubuntu` (Ubuntu Sans Mono), `dejavu` (DejaVu Sans Mono), `liberation` (Liberation Mono). Availability is checked with fontconfig; unavailable fonts fall back to DejaVu Sans Mono, then monospace. FontAwesome icons keep their own family.

`detail_level` is independent of geometry and density. `essential` hides hardware topology/specification lines, GPU maker/driver, detailed OS build/host identity and software builds/additional-Python notes. Models, versions, percentages, graphs and process tops remain. `full` restores metadata where available. The complete inventory remains accessible through `inventory`.

## Layout and density

```bash
cortex-neo configure --profile compact --density comfortable
cortex-neo configure --profile full --density complete
cortex-neo configure --profile auto
cortex-neo configure --hide weather calendar --anchor left
cortex-neo configure --hide --anchor right
```

`--hide` replaces the hidden-card list; no names clears it. Optional IDs are cpu, ram, gpu, storage, network, software, weather, calendar. The system header stays visible. Missing capabilities can still hide optional cards.

`full` keeps the complete composition. `compact` shows hardware and network/Docker, with three top processes. `auto` selects compact below 1100 logical pixels wide or 650 high. `comfortable` prioritizes nine-point minimum fonts and three rows, omitting build detail; `complete` allows seven-point minimum fonts and five rows. Essential detail does not force compact layout.

Additional display settings: `monitor` is primary or a zero-based index; `scale_multiplier` is 0.5–1; `layout` is auto, landscape or portrait. See [display scaling](../guides/displays-and-scaling.md).

## Manual city and dynamic inventory

Copy [location.example.json](../../config/location.example.json) to the personal configuration directory and manually set city, region and public city-center coordinates. Avoid a precise home address. Until valid, no weather request is sent. No GeoIP, GPS, GeoClue or Wi-Fi fallback exists. The file is checked every thirty seconds.

Hardware models, tools and versions are discovered, not configured by hand. Missing languages produce no empty Languages heading. Python summarizes the active global and OS interpreters, with a count of additional installations; it does not claim to describe a project's venv. Queries disable automatic toolchain downloads.

RAM brand/type/speed requires optional authorized SMBIOS access; absent facts disappear. Intel GPU frequency remains MHz, never a fake utilization percentage. Memory tops are grouped RSS including shared pages. Unmounted disks have no invented used percentage; mount changes trigger inventory refresh.

Use `start`, `stop`, `restart`, `status`, `doctor`, `inventory` and `capture` for controls. Edit theme source in your clone and reinstall; installed releases are deployment copies. Docker, SSH, RustDesk and Cloudflare services are independent.

[Ten palette previews and font/detail examples](../reference/appearance.md).
