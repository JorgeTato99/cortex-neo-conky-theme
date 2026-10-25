# Paletas, fuentes y detalle

Diez paletas completas siguen las categorías de acento observadas en Ubuntu 26. Cada una define nueve roles, con colores claros adaptados al fondo oscuro del tema. No cambia el acento ni la fuente del escritorio.

Estas imágenes son renders reales de Conky/Xvfb con datos sintéticos explícitos: **1920 × 1080, escalado 100%, 96 DPI**. Se verificaron contenido, límites, alineación y ausencia de solapamientos. Cada WebP conserva dimensiones y todos los píxeles del PNG original.

| Palette / Paleta | Font / Fuente | Language / Idioma | Detail / Detalle | Preview |
|---|---|---|---|---|
| `blue` | `ubuntu` | `en` | `full` | [blue](../../../assets/previews/blue.webp) |
| `teal` | `dejavu` | `es` | `essential` | [teal](../../../assets/previews/teal.webp) |
| `green` | `liberation` | `en` | `full` | [green](../../../assets/previews/green.webp) |
| `yellow` | `ubuntu` | `es` | `essential` | [yellow](../../../assets/previews/yellow.webp) |
| `orange` | `dejavu` | `en` | `full` | [orange](../../../assets/previews/orange.webp) |
| `red` | `liberation` | `es` | `essential` | [red](../../../assets/previews/red.webp) |
| `pink` | `ubuntu` | `en` | `full` | [pink](../../../assets/previews/pink.webp) |
| `purple` | `dejavu` | `es` | `essential` | [purple](../../../assets/previews/purple.webp) |
| `slate` | `liberation` | `en` | `full` | [slate](../../../assets/previews/slate.webp) |
| `brown` | `ubuntu` | `es` | `essential` | [brown](../../../assets/previews/brown.webp) |

```bash
cortex-neo configure --palette purple --font dejavu --language es --detail-level essential
cortex-neo configure --palette blue --font ubuntu --language en --detail-level full
```

Los nueve roles son text, primary, secondary, muted, border, accent, warning, graph y background. `theme.json` permite sobrescribirlos con seis dígitos hexadecimales; opacidad de 0 a 1. Los alias neon/contrast/amber se mantienen para migración.

Fuentes: Ubuntu Sans Mono, DejaVu Sans Mono y Liberation Mono. Si falta una familia, fontconfig comprueba la sustitución y se usa DejaVu o monospace. Los iconos mantienen FontAwesome.

El detalle esencial conserva nombre/modelo, versión, mediciones, gráficas y tops; oculta topología/especificaciones y builds secundarios. Atribuciones y advertencias de contabilidad permanecen. La densidad y el perfil siguen siendo independientes.

[Ubuntu accent source](https://github.com/ubuntu/yaru/blob/master/common/accent-colors.scss.in) · [GNOME upstream accent categories](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/enum.AccentColor.html)

Ubuntu añade brown a los nueve acentos de la API upstream de GNOME. La comprobación local `gsettings range org.gnome.desktop.interface accent-color` y la captura de configuración entregada confirman diez opciones; no confundimos nombres antiguos de variantes Yaru con los IDs actuales.
