# Real desktop screenshots

The main screenshots were refreshed on **October 25, 2026**, with both desktops clear and **CORTEX NEO 0.1.0**, revision `cee0e54`. The normal GNOME portal captured the complete desktops. These replace the historical examples and earlier fixture renders.

| Machine | Resolution | GNOME scaling | GDK work area | Theme scale | Capture time |
|---|---|---|---|---|---|
| [Ryzen 7 5700X · RTX 4060 Ti](../../assets/screenshots/ryzen-5700x-rtx4060ti.webp) | 2560 × 1440 | 166.67 % | `[67, 32, 1469, 832]` | 1.0 | 2026-10-25 17:33:01 UTC−06:00 |
| [Dell Latitude 5420 · Intel Iris Xe](../../assets/screenshots/dell-latitude-5420.webp) | 1920 × 1080 | 125 % | `[67, 32, 1469, 832]` | 1.0 | 2026-10-25 17:33:00 UTC−06:00 |

Both installations run Ubuntu 26.04.1 LTS with GNOME Wayland and Conky through XWayland. Resolution records the active physical mode and published file pixels; the percentage is GNOME desktop scaling queried from Mutter. GDK work areas use logical pixels and exclude the dock/top bar. Internal theme scale is independent. Both captured interfaces use English; changing README language changes neither the images nor content order.

## Lossless compression

Original PNGs were encoded as WebP with `lossless=True`, `quality=100`, `method=6` and `exact=True`. **Every image** was checked for identical dimensions and decoded RGBA bytes. No resizing, cropping or recoloring was applied. Only WebP files enter Git; original PNGs remain in ignored `temp/`.

| Machine | Original PNG | Published WebP | Reduction |
|---|---|---|---|
| Ryzen | 4.23 MB | 2.80 MB | 33.79 % |
| Dell | 1.99 MB | 1.32 MB | 33.60 % |

MB uses decimal units. Manifests retain dimensions, scaling, timestamps, version, sizes and pixel-comparison outcomes without copying private snapshots.

## Palette gallery

The other nine palettes were captured on the same Ryzen without changing resolution, scaling, font, language or detail level. Blue reuses the main example instead of duplicating its image. The [gallery](../reference/appearance.md) shows all ten native captures in the same order in both languages.

Captures can show hostnames, process names and the manually configured city. Desktops were reviewed before publication. Third-party icons and wallpaper retain their rights; see [notices](../../THIRD_PARTY_NOTICES.md).
