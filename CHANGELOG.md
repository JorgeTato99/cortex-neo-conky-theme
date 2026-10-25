<!-- markdownlint-disable MD013 MD024 -->
# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
and [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

[Español](CHANGELOG.es.md)

## 📖 Usage guide

### How to document changes

Add notable user-facing changes to **[Unreleased]** as you work. Group related entries, explain what changed and why, and link relevant issues or documentation. Write for people; avoid raw commit dumps and implementation-only noise. Mark breaking changes and provide a migration path.

| Standard category | Meaning |
|---|---|
| ✨ Added | New functionality |
| 🔄 Changed | Changes to existing behavior |
| ⚠️ Deprecated | Still available but scheduled for removal |
| 🗑️ Removed | Removed functionality |
| 🐛 Fixed | Corrections to incorrect behavior |
| 🔒 Security | Vulnerability fixes |

Documentation and Testing subsections may explain user-relevant support/evidence. Omit empty categories from actual releases.

### When to release

Move Unreleased entries under `[X.Y.Z] - YYYY-MM-DD - Descriptive title` using ISO dates. During initial development `0.Y.0` introduces substantial features or deliberate breaking changes; `0.y.Z` fixes bugs or compatible small improvements. State incompatibilities explicitly even before 1.0.0. A stable public interface, complete core behavior, maintained documentation and adequate verification support a future 1.0.0. After that, MAJOR breaks compatibility, MINOR adds compatible features and PATCH fixes compatible behavior.

Example: add a complete new dashboard capability in 0.2.0; correct a stale-value bug in 0.1.1. Do not increment merely to record formatting changes.

## [Unreleased]

### 📚 Documentation

- Generate English and Spanish READMEs from one shared layout, with CI checks against translation/structure drift.
- Refresh both native desktop examples and add a separate ten-palette gallery using current GNOME captures, documented resolution/scaling and verified lossless WebP compression.

## [0.1.0] - 2026-10-25 - International desktop launch

### 🎯 Summary

**Release type:** Initial release of the renamed repository. The previous project history is preserved locally; this new sequence retains its completed functionality.

### ✨ Added

- Ten complete Ubuntu 26 accent-inspired palettes, covering text, accents, muted metadata, borders, warning, graph and background roles.
- English as default, complete Spanish dashboard/control catalogs and parallel documentation in one maintained branch.
- Three configurable monospace profiles with availability checks and safe fallback.
- Independent essential/full detail levels, preserving primary values, graphs and process tops while optionally hiding specifications/build metadata.
- Independent adaptive cards for OS, CPU, RAM, GPU, mounted/unmounted storage, network/Docker, installed software, calendar and manually configured city weather.
- Bounded local diagnostics: own-service performance, memory pressure, Compose groups, before/after incidents, minute history, measured commands, selected agent context, named baselines and comparisons.
- Runtime presentation mode and allowlisted support reports for reviewed local sharing.
- Transactional single-entry installation, immutable environments, source revision/fingerprint reporting, safe upgrades/removal and personal-settings preservation.

### 🔄 Changed

- Brand standardized to **CORTEX NEO**; public repository named **cortex-neo-conky-theme**. Existing `cortex-neo` CLI, user services and XDG data paths remain stable for upgrades.
- English documentation is primary; Spanish is under `docs/es/` and `README.es.md`. Legacy palette names remain readable for migration.

### 🐛 Fixed

- Available OS metadata remains visible in full mode even when a hostname is absent.

### 📚 Documentation

- Bilingual installation, appearance, lifecycle, diagnostic tools, architecture, privacy, compatibility and contribution guides.
- Explicit screenshot provenance, resolution/scaling captions and lossless preview compression.

### 🧪 Testing

- Python 3.11–3.15, real Lua callbacks, native ARM64 logic, four clean distribution install/render jobs and native Ryzen/Dell deployment checks.
- Regression contracts for palette completeness, font fallback, essential metadata, localization placeholders, preservation and bounded optional capabilities.
- Synthetic display renders and physical machine evidence are labeled separately; no claim of universal compositor/driver coverage.

[Unreleased]: https://github.com/JorgeTato99/cortex-neo-conky-theme/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/JorgeTato99/cortex-neo-conky-theme/releases/tag/v0.1.0

<!-- ============================================================ -->
<!-- TEMPLATE FOR NEW RELEASES — copy when preparing a release      -->
<!-- ============================================================ -->
<!--
## [X.Y.Z] - YYYY-MM-DD - 📌 DESCRIPTIVE RELEASE TITLE

### 🎯 Summary
**Release type:** Feature / Fix / Improvement
Brief purpose and migration notes.

### ✨ Added
#### Feature name
Description and relevant documentation. Explain observable behavior.

### 🐛 Fixed
#### Corrected behavior
**Problem:** symptom, root cause and user impact.
**Solution:** resulting corrected behavior.

### 🔄 Changed
- Describe behavior changes and mark breaking changes.

### 📚 Documentation
| Document | Change |
|---|---|
| docs/README.md | Describe the user-facing change |

### 🧪 Testing
**Verification:** commands, scenarios and results.

**Modified files:**
| Path | Lines | Description |
|---|---|---|
| source/path | +X/-Y | Describe the change |
-->
