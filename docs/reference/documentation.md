# Maintaining translated documentation

The primary `README.md`, explicit `README.en.md` alias and `README.es.md` share one Markdown layout. Language changes translate the same content; they do not select different sections, screenshots or examples.

- Edit structure, badges, image references, tables and executable examples in `docs/readme/template.md.in`.
- Edit inline text in `docs/readme/en.json` and `docs/readme/es.json`. Catalog keys must match. Structural Markdown blocks and images belong in the template.
- Capture dimensions and desktop scaling come from `assets/screenshots/manifest.json`; never transcribe these values separately into each language.

```bash
python3 scripts/generate_readme.py
python3 scripts/generate_readme.py --check
python3 scripts/check_docs.py
```

Commit source catalogs/template and regenerated READMEs together. CI rejects manual divergence, missing translation keys and broken local links. To add another README language, translate a matching catalog and maintain its documentation paths. Adding a dashboard locale also requires the application catalogs and supported language settings; a README translation alone does not implement a runtime language.

The overview embeds the same two recent, real desktop captures in every language. The separate [palette gallery](appearance.md) keeps all ten variants and their provenance outside the main README. Update English/Spanish galleries together, using the same order and images. Store only losslessly compressed screenshots after checking dimensions and every decoded pixel against the original. Keep original PNGs and operational evidence in ignored `temp/`.
