# Source versions and ZIP updates

```bash
cortex-neo version
cortex-neo version --format json
cortex-neo --version
```

The report separates semantic version, observed commit revision, source dirty state, source fingerprint and comparison with the installed marker. Unknown metadata stays unknown. A fingerprint identifies maintained runtime bytes, including language catalogs; it does not identify your venv, OS packages or personal configuration.

Git source archives expand `_revision.txt` through `export-subst`. Local checkouts can query their own HEAD read-only. The installer stamps copied sources before switching releases, preserving revision information without copying a Git directory. Downloading a ZIP does not require initializing Git.

The new repository starts at **0.1.0**. It preserves functionality from the previous independently versioned repository; the lower number is a new public release sequence, not removal of those capabilities.

Extract each update separately and run `bash scripts/install.sh` from it. Then compare `version --format json` and `doctor`. Do not overwrite the currently active release in place. See [updates and removal](updates-and-uninstall.md).
