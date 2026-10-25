# Capturas de instalaciones reales

Las capturas principales se renovaron el **25 de octubre de 2026**, con ambos escritorios despejados y **CORTEX NEO 0.1.0**, revisión `cee0e54`. Se obtuvieron mediante el portal normal de GNOME, conservando íntegro el escritorio. Sustituyen los ejemplos históricos y los renders con fixtures anteriores.

| Equipo | Resolución | Escalado GNOME | Área útil GDK | Escala del tema | Hora de captura |
|---|---|---|---|---|---|
| [Ryzen 7 5700X · RTX 4060 Ti](../../../assets/screenshots/ryzen-5700x-rtx4060ti.webp) | 2560 × 1440 | 166,67 % | `[67, 32, 1469, 832]` | 1.0 | 2026-10-25 17:33:01 UTC−06:00 |
| [Dell Latitude 5420 · Intel Iris Xe](../../../assets/screenshots/dell-latitude-5420.webp) | 1920 × 1080 | 125 % | `[67, 32, 1469, 832]` | 1.0 | 2026-10-25 17:33:00 UTC−06:00 |

Las dos instalaciones ejecutan Ubuntu 26.04.1 LTS con GNOME Wayland y Conky sobre XWayland. La resolución corresponde a los píxeles del modo activo y del archivo publicado; el porcentaje es el escalado elegido en GNOME, consultado en Mutter. El área útil GDK usa píxeles lógicos y excluye dock/barra superior. La escala interna del tema es independiente. La interfaz capturada está en inglés en ambos casos; cambiar el idioma del README no cambia las imágenes ni el orden del contenido.

## Compresión sin pérdida

Los PNG originales se convirtieron a WebP con `lossless=True`, `quality=100`, `method=6` y `exact=True`. Para **cada imagen** se compararon las dimensiones y todos los bytes RGBA decodificados. No se redimensionó, recortó ni recoloreó el contenido. Solo los WebP se incluyen en Git; los PNG originales permanecen en `temp/`, excluido de Git.

| Equipo | PNG original | WebP publicado | Reducción |
|---|---|---|---|
| Ryzen | 4.23 MB | 2.80 MB | 33.79 % |
| Dell | 1.99 MB | 1.32 MB | 33.60 % |

MB son unidades decimales. Los manifiestos conservan dimensiones, escalado, fechas, versión, tamaños y resultado de la comparación, sin copiar snapshots privados.

## Galería de paletas

Las otras nueve paletas se capturaron en el mismo Ryzen sin cambiar resolución, escalado, fuente, idioma o nivel de detalle. La imagen azul se reutiliza del ejemplo principal para evitar duplicarla. La [galería](../reference/appearance.md) muestra las diez capturas reales en el mismo orden para ambos idiomas.

Las capturas pueden mostrar hostname, procesos y la ciudad configurada a mano. Se revisaron los escritorios antes de publicar. Los iconos y fondos de terceros conservan sus derechos; consulta los [avisos](../../../THIRD_PARTY_NOTICES.md).
