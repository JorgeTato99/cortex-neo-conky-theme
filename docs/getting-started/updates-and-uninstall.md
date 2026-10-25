# Updates and removal

Download a new source ZIP into a separate directory, or update your own checkout, then run the installer again as the same desktop user:

```bash
bash scripts/install.sh
cortex-neo version
cortex-neo doctor
```

The installer builds an immutable release and its environment before switching the stable `~/.local/share/cortex-neo` link. Activation failure restores the previous release and saved controls/configuration. An installation lock rejects concurrent update/removal. It refuses unrelated directories and unmanaged releases.

Personal settings, manual weather location, history and private records are preserved. Edited launchers are not silently deleted. Releases and backups are under XDG data/state directories; inspect their ownership before manual cleanup. Never remove the active virtual environment or edit an installed release as if it were your source checkout.

```bash
cortex-neo uninstall
# Or, from an extracted source directory:
bash scripts/install.sh --uninstall
```

Removal disables the project's user units and removes only owned installation controls. Configuration, cache, state and backups remain, so reinstalling can recover your choices. It does not uninstall distribution packages shared with other applications, delete projects or stop Docker/RustDesk.

The repository was renamed for v0.1.0. Runtime command names, service names and XDG paths stay `cortex-neo`; existing personal data need not move. See [version identification](version-and-zip.md).
