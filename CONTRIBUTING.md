# Contributing to CORTEX NEO

[Español](docs/es/contributing.md)

Use English code comments/docstrings, primary English documentation and matching Spanish pages. Keep UTF-8/LF, four-space indentation, Ruff and the checked-in StyLua configuration.

```bash
sudo apt install python3-venv liblua5.4-0
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
bash scripts/check.sh
```

Install [StyLua 2.6.0](https://github.com/JohnnyMorganz/StyLua/releases/tag/v2.6.0) on PATH. Unit tests run real Lua callbacks without a desktop, Docker, GPU or credentials. Distribution integration tests install/render in disposable containers; physical session evidence remains separate.

| Change | Source |
|---|---|
| Card content/style | theme/cards, theme Lua, render.py |
| Geometry/alignment | layout.py |
| Hardware and sampling | system.py, gpu.py, telemetry.py |
| Tool inventory | versions.py |
| Weather/manual city | weather.py |
| Appearance and languages | preferences.py, palettes.py, fonts.py, i18n.py, locales |
| Installation/services | scripts and systemd |

Read [architecture](docs/reference/architecture.md) before moving responsibilities. Reinstall from your clone to apply source edits without overwriting personal preferences. Test observable behavior, failure boundaries and preservation, rather than mirroring implementation details.

Missing tools/sensors stay omitted/unavailable. Version probes must not download toolchains. Bound work and histories, preserve source cadences, and keep location exclusively manual. Retain MIT attribution.

Explain the concrete problem/result and verification. Visual changes need screenshots with physical resolution and desktop scaling, reviewed for private content. Translate matching docs/catalogs in the same change; preserve placeholders. Add notable changes to [Unreleased](CHANGELOG.md). Use the compatibility form for actual checked environments and state limits. Review `version`/`report` output before sharing; never attach raw snapshots, environments or private records.

README changes use one shared template and inline language catalogs. Run `python3 scripts/generate_readme.py`, then `--check`; see [documentation maintenance](docs/reference/documentation.md). Update both gallery languages with the same images and order.
