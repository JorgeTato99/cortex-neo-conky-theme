# Palettes, fonts and detail

Ten complete palettes follow the accent categories observed on Ubuntu 26. Each defines nine semantic roles, with brighter foregrounds adapted to this dark theme. Selecting one does not change desktop accents or fonts.

These are actual Conky/Xvfb renders with explicit synthetic fixture data: **1920 × 1080, 100% scaling, 96 DPI**. Content, bounds, alignment and absence of overlap were checked. Every lossless WebP preserves the original PNG dimensions and decoded pixels.

| Palette / Paleta | Font / Fuente | Language / Idioma | Detail / Detalle | Preview |
|---|---|---|---|---|
| `blue` | `ubuntu` | `en` | `full` | [blue](../../assets/previews/blue.webp) |
| `teal` | `dejavu` | `es` | `essential` | [teal](../../assets/previews/teal.webp) |
| `green` | `liberation` | `en` | `full` | [green](../../assets/previews/green.webp) |
| `yellow` | `ubuntu` | `es` | `essential` | [yellow](../../assets/previews/yellow.webp) |
| `orange` | `dejavu` | `en` | `full` | [orange](../../assets/previews/orange.webp) |
| `red` | `liberation` | `es` | `essential` | [red](../../assets/previews/red.webp) |
| `pink` | `ubuntu` | `en` | `full` | [pink](../../assets/previews/pink.webp) |
| `purple` | `dejavu` | `es` | `essential` | [purple](../../assets/previews/purple.webp) |
| `slate` | `liberation` | `en` | `full` | [slate](../../assets/previews/slate.webp) |
| `brown` | `ubuntu` | `es` | `essential` | [brown](../../assets/previews/brown.webp) |

```bash
cortex-neo configure --palette purple --font dejavu --language es --detail-level essential
cortex-neo configure --palette blue --font ubuntu --language en --detail-level full
```

The nine roles are text, primary, secondary, muted, border, accent, warning, graph and background. `theme.json` accepts six-digit hexadecimal overrides and opacity from 0 to 1. Legacy neon/contrast/amber aliases remain readable for migration.

Font profiles select Ubuntu Sans Mono, DejaVu Sans Mono or Liberation Mono. Fontconfig checks availability; missing families fall back to DejaVu, then monospace. Icons keep FontAwesome.

Essential detail keeps model/name, version, measurements, graphs and tops while hiding secondary topology/specifications and builds. Attribution and accounting notices remain. Density and layout profile are independent choices.

[Ubuntu accent source](https://github.com/ubuntu/yaru/blob/master/common/accent-colors.scss.in) · [GNOME upstream accent categories](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/enum.AccentColor.html)

Ubuntu adds brown to the nine upstream GNOME API accents. Local `gsettings range org.gnome.desktop.interface accent-color` and the supplied Settings image confirm ten choices; older Yaru variant names are not substituted for current IDs.
