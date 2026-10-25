# Displays and scaling

Three distinct measurements matter: physical display resolution, desktop scaling (GNOME percentage or GDK factor), and the internal theme scale. A 4K display at 200% does not provide a 3840-pixel logical work area. Always record both resolution and desktop scaling when sharing a screenshot.

The theme queries the selected monitor's GDK work area, excluding panels and docks, then fits an independent-card composition with matching margins. It supports landscape and portrait layouts, mixed card availability, four-to-six-week calendars and full/compact profiles. CPU/RAM rows and GPU/storage rows share heights. The calendar fills its column to the common bottom edge.

```json
{"monitor":"primary","layout":"auto","scale_multiplier":1.0}
```

`monitor` also accepts a zero-based index. `scale_multiplier` accepts 0.5–1. Automatic profile selection uses logical work-area thresholds. Every ten seconds the supervisor checks display/capability/preferences signatures and regenerates only when those change. Actual Xft window heights are checked after mapping, with bounded font fitting for integer rounding.

Compact mode and comfortable density improve readability on small screens; hiding optional cards can help. Minimum font sizes do not create physical space on exceptionally small work areas. Conky uses XWayland under Wayland; desktop support still requires native verification.

Changing resolution can restart a remote capture stream independently of the dashboard. The project does not change monitor modes, GNOME login state or RustDesk settings. See [screenshots](../validation/screenshots.md) for measured desktop examples.
