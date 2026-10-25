# Configuración

La instalación conserva las preferencias personales. Edita los archivos de
`~/.config/cortex-neo/`; las métricas y configuraciones generadas en la caché no
son fuentes editables. Las rutas XDG absolutas correspondientes se respetan.

## Preferencias de pantalla

```json
{
  "monitor": "primary",
  "scale_multiplier": 1.0,
  "layout": "auto"
}
```

`monitor` acepta el monitor primario o un índice desde cero. El multiplicador
admite 0.5–1.0; `layout` admite auto, landscape y portrait. Consulta
[pantallas y escalado](../guides/displays-and-scaling.md) para distinguir la
resolución física, la escala de GNOME y la escala interna del tema.

## Paleta, opacidad y tarjetas

```bash
cortex-neo configure --palette contrast --opacity 0.95
cortex-neo configure --hide weather calendar --anchor left
cortex-neo configure --palette neon --opacity 0.745098 --hide --anchor right
```

Las paletas disponibles son `neon`, `contrast` y `amber`. `--hide` sustituye la
lista de tarjetas ocultas; sin nombres vuelve a mostrar las disponibles. Los
identificadores son `cpu`, `ram`, `gpu`, `storage`, `network`, `software`,
`weather` y `calendar`. La cabecera `system` permanece visible. Una tarjeta que
no tiene datos sigue oculta aunque no esté en esa lista.

El anclaje admite `left` y `right`. El supervisor detecta cambios en unos diez
segundos. `settings.json` guarda selección/anclaje y `theme.json` paleta/opacidad;
ambos viven en `~/.config/cortex-neo/` y se conservan al actualizar. También se
pueden editar a mano; `config/theme.example.json` documenta el formato. Colores
personalizados admiten solo seis dígitos hexadecimales; claves y valores inválidos
usan el tema seguro incluido. `configure` rechaza opacidad fuera de 0–1 antes
de escribir. Los campos personales de configuración no se publican en Git.

## Perfiles y lectura

```bash
cortex-neo configure --profile compact --density comfortable
cortex-neo configure --profile full --density complete
cortex-neo configure --profile auto
```

`full` conserva la composición completa. `compact` muestra sistema, CPU, RAM,
GPU, discos y red/Docker cuando hay datos, con tres procesos destacados. En
horizontal usa tres columnas; en vertical, dos. `auto` elige compacto cuando el
área útil tiene menos de 1100 píxeles de ancho o 650 de alto. Son píxeles de
aplicación, después de considerar el escalado del escritorio.

La densidad `comfortable` usa un mínimo de nueve puntos, tres procesos y versiones
sin detalles de compilación. `complete` mantiene el detalle y un mínimo de siete
puntos. El inventario completo continúa disponible con `cortex-neo inventory`.
En pantallas excepcionalmente pequeñas puede hacer falta ocultar tarjetas o
cambiar el escalado del escritorio; un mínimo tipográfico no crea espacio físico.

## Ciudad manual

`location.json` empieza así:

```json
{
  "mode": "manual_city",
  "name": "",
  "region": "",
  "latitude": null,
  "longitude": null
}
```

Introduce a mano la ciudad, región y coordenadas públicas de su centro. No uses
una dirección personal precisa. Hasta tener una ciudad válida, no hay petición
meteorológica ni tarjeta de clima. El archivo se relee cada treinta segundos.
No hay GeoIP, GPS, GeoClue, escaneo Wi-Fi ni detección automática como fallback.
La política completa está en [privacidad](../reference/privacy.md).

## Herramientas, hardware y ausencias

No hay que rellenar el modelo del procesador, discos, GPU o versiones de software.
Se descubren en cada equipo. Una herramienta ausente o fallida no genera filas
con errores; sin lenguajes válidos no aparece la categoría Lenguajes. El inventario
completo se consulta con `cortex-neo inventory`.

Python resume el intérprete global activo y el del sistema; las instalaciones
adicionales se cuentan. Esto no representa el entorno virtual seleccionado en un
proyecto concreto. Las consultas no descargan toolchains automáticamente.

La lectura SMBIOS de marca/DDR/velocidad es opcional mediante `sudo -n dmidecode`.
Si no está autorizada, esos campos se omiten sin solicitar contraseña. La GPU
solo presenta sensores realmente disponibles: frecuencia Intel no es porcentaje
de uso, y un sensor ausente no equivale a cero.

Los tops de memoria agrupan RSS e incluyen memoria compartida; no son PSS ni
memoria privada. Los discos sin montar no muestran un porcentaje de uso ficticio.
El inventario cambia al detectar montajes y se vuelve a explorar periódicamente.

## Control y personalización del tema

```bash
cortex-neo start
cortex-neo stop
cortex-neo restart
cortex-neo status
cortex-neo doctor
cortex-neo inventory
cortex-neo capture
```

El inicio automático pertenece a la sesión gráfica. Docker, SSH, RustDesk y
Cloudflare tienen servicios independientes. Para editar el diseño, modifica
`theme/cards/` y `theme/*.lua` en tu clon; después reinstala desde él. Las versiones
instaladas son copias de despliegue y una actualización no conserva cambios hechos
allí directamente. Consulta [arquitectura](../reference/architecture.md).
