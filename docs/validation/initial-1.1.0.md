# Validación de CÓRTEX NEO 1.1.0

Fecha de las comprobaciones: **24 de octubre de 2026**. Las preferencias de cada
máquina y sus snapshots permanecen fuera del repositorio. La ciudad de las
capturas fue configurada manualmente; el ejemplo público empieza vacío.

## Equipos reales

La tabla siguiente conserva las condiciones de la validación inicial. Las
[capturas renovadas](screenshots.md) documentan los modos actuales: Ryzen a
2560 × 1440 con escalado de GNOME del 166,67 % y Dell a 1920 × 1080 con 125 %.

| Equipo | Hardware | Escritorio y captura | Escala del tema |
|---|---|---|---:|
| Ryzen de escritorio | Ryzen 7 5700X, 64 GB DDR4, RTX 4060 Ti 8 GB | Ubuntu 26.04.1 LTS, GNOME Wayland, 1920 × 1080 | 1.0 |
| Dell Latitude 5420 | Core i5-1135G7, 16 GB DDR4, Intel Iris Xe | Ubuntu 26.04.1 LTS, GNOME Wayland, 1366 × 768 | 0.884615 |

Las [capturas](screenshots.md) proceden de ambos escritorios despejados. Se
comprobaron las nueve ventanas reales mediante `scripts/check_desktop.py`:

- Dentro del área útil y sin solapamientos.
- CPU/RAM y GPU/almacenamiento con la misma altura y posición vertical por fila.
- Calendario alineado con el borde inferior del conjunto.
- Servicios de interfaz y métricas activos, sin reinicios automáticos.
- Datos recientes y ausencia de errores Lua o trazas en sus invocaciones del journal.

GDK usa píxeles lógicos y XWayland puede utilizar otra escala. El comprobador
aplica el factor correspondiente antes de comparar alturas y límites; no equipara
las dimensiones de la captura directamente con las de `xwininfo`.

## Escala y alineación

Se redujo temporalmente `scale_multiplier` y se restauró la configuración
original en ambos equipos, sin cambiar la resolución ni reiniciar el supervisor:

| Equipo | Escala reducida | Escala restaurada |
|---|---:|---:|
| Ryzen | 0.900000 | 1.000000 |
| Dell | 0.796154 | 0.884615 |

Los bordes inferiores calendario/red/versiones fueron 1688/1688/1688 en la
Ryzen y 751/750/751 en la Dell, en coordenadas XWayland. El píxel de diferencia
en la Dell procede del redondeo de escala.

La matriz de geometría también cubre 1280 × 720, 2560 × 1440, 3840 × 2160,
3440 × 1440 y una pantalla vertical de 1080 × 1920. Es una comprobación de
cálculo; no acredita capturas reales en siete monitores ni legibilidad física
a cualquier densidad.

## Suite automatizada

**30 pruebas** ejecutan Python y los callbacks Lua reales con snapshots aislados:

- Herramientas ausentes, errores, timeouts y versiones malformadas.
- Inventarios parciales de dpkg y fallos aislados de proveedores de versiones.
- Restos de metadatos que no deben simular una aplicación instalada.
- Categorías vacías, herramientas opcionales y paginación de inventarios largos.
- Consultas de Rustup/Go sin descarga automática de toolchains.
- Ausencia de GPU/sensores y frecuencia Intel sin porcentaje ficticio de utilización.
- Datos antiguos y métricas numéricas inválidas.
- Ciudad manual ausente/inválida, cambio de ciudad, caché y fallos meteorológicos.
- Agrupación de memoria antes de seleccionar las cinco aplicaciones destacadas.
- Escalado de fuentes, gráficas, alineación y límites de la disposición.
- Detección de montajes/desmontajes antes del refresco periódico, sin un escaneo
  completo en cada tick ni reacciones a overlays de contenedores.
- Identificación de SSD del mismo modelo mediante su punto de montaje.

La CI usa Python 3.10 y 3.14 sobre Ubuntu. Comprueba estilo con Ruff 0.17.2 y
StyLua 2.6.0, sintaxis Bash y la suite. No prueba una sesión gráfica ni drivers
reales; estos se verificaron por separado en los equipos de la tabla.

## Almacenamiento y coste de consulta

La Ryzen descubre dos SSD montados: el sistema en `/` y desarrollo en `/srv/dev`.
Los dos HDD siguen sin montar. La tarjeta distingue esas situaciones y conserva
la gráfica principal del filesystem `/`, sin presentar un porcentaje agregado
engañoso de varios discos.

Cada dos segundos se lee una firma pequeña de montajes de dispositivos del
kernel y se consulta el uso de sus filesystems. `lsblk` se ejecuta al cambiar
esa firma o cada 30 segundos para descubrir también unidades nuevas sin montar.
Los cambios de overlay/tmpfs de Docker no invalidan por sí solos esa firma.

Se verificó además un bind mount temporal del SSD de desarrollo, sin desmontar
el volumen utilizado por los proyectos. El recolector detectó su aparición en
1.405 segundos y su retirada en 2.006 segundos, manteniendo el mismo PID. La ruta
temporal se retiró al terminar: no se necesitó reiniciar el tema ni el servidor.

## Reproducción y límites

```bash
bash scripts/check.sh
~/.local/bin/cortex-neo doctor
~/.local/share/cortex-neo/venv/bin/python -I scripts/check_desktop.py
```

El último comando se ejecuta desde la carpeta del código instalado y requiere
una sesión gráfica. Las capturas usan el portal normal de GNOME y pueden pedir
consentimiento de la sesión aunque exista acceso administrativo.

No se reiniciaron los equipos para esta publicación. Se verificó el inicio
habilitado para la sesión gráfica, pero no se declara un nuevo arranque completo.
AMD y otros escritorios tienen detección o rutas previstas, pero no se presentan
como comprobados físicamente. Los datos RSS incluyen memoria compartida; no
representan memoria privada/PSS.
