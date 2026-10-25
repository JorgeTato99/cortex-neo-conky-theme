# Palettes, fonts and detail

All ten variants use **real screenshots of the same Ryzen desktop**, taken through the normal GNOME portal. Only the palette changed: font `ubuntu`, language `en` and detail `full` stayed the same. Original preference files were restored afterward.

**2560 × 1440 · GNOME scaling 166.67% · internal theme scale 1.0.** Captured on October 25, 2026, version 0.1.0. Values and clock reflect each moment; graphs restart their short window when cards regenerate. No synthetic readings or image recoloring were used.

| Palette | Primary color | Original image |
|---|---|---|
| `blue` | `#55AEFF` | [Open](../../assets/screenshots/ryzen-5700x-rtx4060ti.webp) |
| `teal` | `#56D6CE` | [Open](../../assets/palettes/teal.webp) |
| `green` | `#96D56C` | [Open](../../assets/palettes/green.webp) |
| `yellow` | `#F3CC61` | [Open](../../assets/palettes/yellow.webp) |
| `orange` | `#FFAB75` | [Open](../../assets/palettes/orange.webp) |
| `red` | `#FF8097` | [Open](../../assets/palettes/red.webp) |
| `pink` | `#E896E8` | [Open](../../assets/palettes/pink.webp) |
| `purple` | `#B3A1FF` | [Open](../../assets/palettes/purple.webp) |
| `slate` | `#A7C8B2` | [Open](../../assets/palettes/slate.webp) |
| `brown` | `#DDBA8D` | [Open](../../assets/palettes/brown.webp) |

## Blue · `blue`

![CORTEX NEO · Blue](../../assets/screenshots/ryzen-5700x-rtx4060ti.webp)

## Teal · `teal`

![CORTEX NEO · Teal](../../assets/palettes/teal.webp)

## Green · `green`

![CORTEX NEO · Green](../../assets/palettes/green.webp)

## Yellow · `yellow`

![CORTEX NEO · Yellow](../../assets/palettes/yellow.webp)

## Orange · `orange`

![CORTEX NEO · Orange](../../assets/palettes/orange.webp)

## Red · `red`

![CORTEX NEO · Red](../../assets/palettes/red.webp)

## Pink · `pink`

![CORTEX NEO · Pink](../../assets/palettes/pink.webp)

## Purple · `purple`

![CORTEX NEO · Purple](../../assets/palettes/purple.webp)

## Slate · `slate`

![CORTEX NEO · Slate](../../assets/palettes/slate.webp)

## Brown · `brown`

![CORTEX NEO · Brown](../../assets/palettes/brown.webp)

## Configuration

```bash
cortex-neo configure --palette purple --font ubuntu --detail-level full
cortex-neo configure --palette blue
```

Every palette defines nine roles: text, primary, secondary, muted, border, accent, warning, graph and background. `theme.json` accepts six-digit hexadecimal overrides and opacity from 0 to 1. Legacy neon/contrast/amber aliases remain for migration.

Font profiles select Ubuntu Sans Mono, DejaVu Sans Mono or Liberation Mono; fontconfig checks availability and substitutes missing families. Icons retain FontAwesome.

The `essential` detail level hides secondary specifications/builds while keeping models, versions, measurements, graphs, tops and accounting/attribution notices. Profile and density remain independent choices.

[Provenance and compression](../validation/screenshots.md) · [Configuration](../getting-started/configuration.md)
