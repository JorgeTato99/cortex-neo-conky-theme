# Capturas de instalaciones reales

Imágenes renovadas el **24 de octubre de 2026 a las 20:07 (UTC−06:00)**, con
los escritorios despejados y la versión 1.1.0 del dashboard instalada.
Son capturas completas obtenidas mediante el portal normal de GNOME; no se
generaron como mockups ni se incorporaron datos ficticios al tema.

| Archivo | Equipo | Resolución de captura | Escalado de GNOME | Área útil GDK | Escala del tema |
|---|---|---|---:|---|---:|
| [Ryzen](../../../assets/screenshots/ryzen-5700x-rtx4060ti.webp) | Ryzen 7 5700X, 64 GB DDR4, NVIDIA RTX 4060 Ti 8 GB | 2560 × 1440 | 166,67 % | `(67, 32, 1469, 832)` | 1.0 |
| [Dell](../../../assets/screenshots/dell-latitude-5420.webp) | Latitude 5420, Core i5-1135G7, 16 GB DDR4, Intel Iris Xe | 1920 × 1080 | 125 % | `(67, 32, 1469, 832)` | 1.0 |

Los dos equipos ejecutan Ubuntu 26.04.1 LTS con GNOME Wayland y Conky sobre
XWayland. La resolución indica los píxeles físicos del modo activo y del archivo
publicado; el escalado de GNOME indica el tamaño elegido para la interfaz. Ambos
valores se consultaron en Mutter antes de capturar, sin cambiar la pantalla.

En la Ryzen, el factor que devuelve Mutter es `1.6666666269302368`, redondeado
a 166,67 % en la tabla; en la Dell es `1.25`. Ambos producen un escritorio lógico
de aproximadamente 1536 × 864. GDK informa el área útil como `(x, y, ancho, alto)`
en píxeles lógicos, descontando el dock y la barra superior. La escala del tema
es un multiplicador interno independiente del escalado del escritorio. Por eso
estas capturas tienen distinta resolución física y la misma disposición lógica.

## Compresión sin pérdida

Las capturas PNG originales se convirtieron a **WebP sin pérdida**, manteniendo
resolución, colores y nitidez del texto. Se verificó la igualdad de todos los
píxeles decodificados, además de las dimensiones; no se redimensionaron ni se
redujo la paleta de colores.

| Equipo | PNG original | WebP publicado | Reducción |
|---|---:|---:|---:|
| Ryzen | 4,23 MB | 2,79 MB | 33,98 % |
| Dell | 1,99 MB | 1,32 MB | 33,71 % |

Tamaños expresados en MB decimales (1 MB = 1 000 000 bytes). Conversión con
Pillow 12.3.0, `lossless=True`, `quality=100`, `method=6` y `exact=True`.
El repositorio conserva solo las versiones comprimidas de estas capturas.

## Información visible

La gráfica principal de almacenamiento muestra `/`; los discos adicionales se
enumeran debajo. Los HDD de la Ryzen permanecen sin montar. La frecuencia Intel
se expresa en MHz y no equivale al porcentaje de uso que ofrece NVIDIA.

La ciudad mostrada se configuró manualmente para estas instalaciones. Los modelos,
programas y versiones se descubren por equipo. Los valores visibles representan
una instantánea y no una recomendación de versiones actuales de esos programas.

Consultar [validación](testing.md) y [recursos de terceros](../../../THIRD_PARTY_NOTICES.md).
