# CÓRTEX NEO

**Your Linux desktop, in real time.**

[Español](README.md) · [Command guide](docs/en/usage.md) · [Compatibility](docs/reference/compatibility.md)

CÓRTEX NEO is an open-source desktop dashboard built with Python, Lua and Conky.
Independent neon cards show CPU, memory, GPU, disks, networking, Docker,
installed tools, a calendar and optional manually configured weather.
The current source version is **1.2.0**.

## Install

Download and extract the [source ZIP](https://github.com/JorgeTato99/cortex-neo/archive/refs/heads/main.zip).
Open a terminal in the extracted directory and run:

```bash
bash scripts/install.sh
```

The installer prepares Conky, fonts and Linux dependencies, creates an immutable
Python environment and enables the user services. Run it as your desktop user;
only system packages need sudo. Existing personal settings are preserved.
Ubuntu 24.04/26.04 and Debian 12/13 have tested installation profiles.
Python 3.11+, a graphical Linux session and user systemd are required.

If the launcher is not on your current PATH, use `~/.local/bin/cortex-neo`.

```bash
~/.local/bin/cortex-neo version
~/.local/bin/cortex-neo doctor
```

## Make it yours

```bash
cortex-neo configure --palette neon --opacity 0.9
cortex-neo configure --profile compact --density comfortable
cortex-neo configure --profile full --density complete
```

Palettes, opacity, card selection and anchoring are persistent XDG preferences.
The full profile keeps the complete composition; compact focuses on hardware and
network/Docker. Comfortable density prioritizes readable text and less detail.
Missing tools and sensors are omitted or shown as unavailable, never invented.

## Understand your machine

- Measure CÓRTEX itself with `performance`.
- Inspect available memory, swap and pressure with `memory`; PSS/USS is opt-in.
- Group containers by engine and Compose project with `containers`.
- Capture a local before/after timeline with `incident`.
- Query bounded numerical minute aggregates with `history`.
- Measure an explicit test/build command with `run`, preserving its output and exit code.
- Export selected capabilities for an agent with `context`.
- Save named observations and compare environments with `baseline-save` and `compare`.
- Hide personal labels while screen sharing with `presentation`.
- Preview a selected support report with `report`.

See the [English command guide](docs/en/usage.md) for examples, retention,
measurement limits and the difference between observations and inferred causes.

## Update from a ZIP

Download and extract the new source into a separate directory. Run the same
installer from that directory, then check `cortex-neo version`. You do not need
to turn a ZIP download into a Git checkout. Preparation happens before replacing
the active deployment; failed activation attempts restore the previous runtime.
See [version and ZIP updates](docs/getting-started/version-and-zip.md).

## Real desktops and validation

The [Spanish README](README.md#así-se-ve) contains lossless screenshots from the
Ryzen 7 5700X/RTX 4060 Ti and Dell Latitude 5420 installations, with physical
resolution and GNOME scaling documented. Images represent their capture time.
Both physical machines use Ubuntu Desktop and GNOME Wayland with Conky on XWayland.

CI checks Python 3.11–3.15, ARM64 contracts and clean installation/rendering in
Ubuntu 24.04/26.04 and Debian 12/13. Xvfb rendering and synthetic GPU fixtures do
not certify physical drivers or complete desktop sessions. AMD graphics still
need physical validation. See [testing](docs/validation/testing.md).

## Privacy

System collection is local. Weather stays disabled until you manually configure
a city; there is no GeoIP, GPS or Wi-Fi location discovery. Optional weather
requests send that city's coordinates and an ordinary network connection to
Open-Meteo. Presentation mode masks the dashboard, not other apps or existing
private records. Reports are previews: nothing is automatically sent or published.

## Contribute

Read [CONTRIBUTING.md](CONTRIBUTING.md). A compatibility report should include
the application revision, distribution/session, physical resolution, desktop
scaling and what was actually checked. Use the repository's compatibility issue
form and review reports/screenshots before sharing them. A report is evidence,
not automatic certification of a platform.

## License and attribution

Created by [Jorge Hernández Montero · JorgeTato99](https://github.com/JorgeTato99).
MIT licensed: retain the copyright notice and license when reusing the code.
See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
