# Languages and translation maintenance

English is the source/default language. Spanish is a complete maintained variant in the same repository and branch, selected with `cortex-neo configure --language es`. Use `--language en` to switch back. Dashboard regeneration detects settings changes; new CLI invocations use the saved language. Machine-readable keys, CLI actions and configuration IDs remain stable English identifiers.

Root `README.md` and `docs/` are English; `README.es.md` and `docs/es/` mirror Spanish topics. Change both language pages in the same pull request. CI checks page parity and local Markdown links. Avoid separate language branches: they split code changes and make translation drift harder to review. Additional languages can add catalogs and matching documentation once maintained.

`cortex_neo/locales/en.json` defines source messages; `es.json` has identical keys. Python translates static messages before formatting dynamic values. The renderer passes translations as data to Lua; `H.t` translates explicit static labels, not arbitrary device/process names. Unknown messages safely retain English. Calendar month/day labels and weather conditions follow the selected language; hardware values and physical units do not change.

A small mixed Python/Lua application benefits from data-only JSON catalogs without binary compilation tooling. This follows the catalog separation principle described by [Python gettext](https://docs.python.org/3/library/gettext.html), while keeping the format directly serializable for Lua. It is a project choice, not a claim that gettext is unsuitable.

Translation checks require identical keys and Python placeholders. Preserve Conky markup, FontAwesome glyphs, numeric units and formatting tokens. Do not add executable translation expressions, network translation services or location discovery. New phrases should be short, clear English as recommended by [GitHub's translation writing guidance](https://docs.github.com/en/contributing/writing-for-github-docs/writing-content-to-be-translated).
