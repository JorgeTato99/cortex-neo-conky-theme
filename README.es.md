<div align="center">

# CORTEX NEO

**Tu escritorio Linux, en tiempo real.**

[English](README.md) · Código actual: **0.1.0** · [Guía de comandos](docs/es/README.md)

Tarjetas Conky con estética neón, telemetría compartida y adaptación al espacio disponible.

[![CI](https://github.com/JorgeTato99/cortex-neo-conky-theme/actions/workflows/ci.yml/badge.svg)](https://github.com/JorgeTato99/cortex-neo-conky-theme/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-55aeff.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-6de4ef.svg)](pyproject.toml)

</div>

CORTEX NEO convierte información del sistema en un panel modular de escritorio.
Python descubre y recopila los datos; Lua y Conky presentan tarjetas independientes
con gráficas históricas, sin un gran fondo que cubra todo el escritorio.

## Así se ve

### Ryzen 7 5700X · RTX 4060 Ti

2560 × 1440 píxeles · escalado de GNOME: **166,67 %**.

![CORTEX NEO en la Ryzen a 2560 × 1440 y escalado del 166,67 %](assets/screenshots/ryzen-5700x-rtx4060ti.webp)

### Dell Latitude 5420 · Intel Iris Xe

1920 × 1080 píxeles · escalado de GNOME: **125 %**.

![CORTEX NEO en la Dell a 1920 × 1080 y escalado del 125 %](assets/screenshots/dell-latitude-5420.webp)

Son capturas de instalaciones reales. Los valores y las versiones representan
el momento de la captura; no son datos incluidos en la configuración del tema.
Las imágenes usan WebP sin pérdida y conservan todos los píxeles de la captura.
[Equipos, escala y condiciones de las capturas](docs/es/validation/screenshots.md).

## Qué muestra

- **Sistema:** distribución y versión, kernel, compilación, arquitectura y reloj.
- **CPU:** modelo, núcleos/hilos, temperatura, histórico y cinco procesos destacados.
- **RAM:** capacidad, DDR, módulos y velocidad cuando están disponibles; histórico
  y cinco aplicaciones agrupadas por consumo RSS.
- **GPU:** modelo, driver y sensores disponibles. NVIDIA puede ofrecer uso/VRAM;
  Intel puede ofrecer frecuencia en MHz sin inventar un porcentaje de uso.
- **Almacenamiento:** uso del filesystem principal, discos montados y sin montar,
  y rutas que permiten distinguir unidades del mismo modelo.
- **Red y Docker:** tráfico e históricos, y contenedores de Engine/Desktop por separado.
- **Versiones/builds:** aplicaciones y toolchains realmente instalados; las
  categorías vacías desaparecen y los inventarios largos se paginan.
- **Clima y calendario:** pronóstico de siete días con ciudad configurada a mano,
  y calendario del mes con el día actual destacado.

Las métricas se muestrean cada **2 segundos**. Un cambio de montaje refresca el
inventario de almacenamiento; sin cambios, el inventario completo se consulta
cada 30 segundos. Las consultas de versiones y clima tienen cadencias mayores.

## Instalación rápida

La ejecución requiere **Linux con sesión gráfica y systemd de usuario**. Las
instalaciones verificadas usan Ubuntu Desktop, GNOME Wayland y Conky sobre XWayland.

Descarga y extrae el [código ZIP](https://github.com/JorgeTato99/cortex-neo-conky-theme/archive/refs/heads/main.zip).
Desde esa carpeta, en Ubuntu 24.04/26.04 o Debian 12/13:

```bash
bash scripts/install.sh
```

Un único instalador prepara Conky, GTK, fuentes y herramientas del sistema,
crea el entorno Python y habilita los servicios de la sesión gráfica. Ejecuta
como tu usuario; solo apt solicita sudo. Conserva las preferencias y prepara
cada actualización antes de sustituir la versión activa. No instala Docker,
lenguajes ni drivers: muestra los que encuentre en el equipo.

La tarjeta meteorológica permanece oculta hasta configurar una ciudad manual.
Consulta [instalación y opciones](docs/es/getting-started/installation.md) para
descargar el código, simular el plan o instalar sin arrancar todavía el panel.
La [documentación](docs/es/README.md) reúne configuración, mantenimiento y diagnóstico.

## Control y actualización

```bash
~/.local/bin/cortex-neo start
~/.local/bin/cortex-neo stop
~/.local/bin/cortex-neo restart
~/.local/bin/cortex-neo inventory
~/.local/bin/cortex-neo capture
~/.local/bin/cortex-neo version
```

Para actualizar, descarga y extrae una copia nueva del código y ejecuta desde
ella el mismo instalador:

```bash
bash scripts/install.sh
```

La reinstalación aplica el código nuevo y reinicia únicamente los servicios del
tema. Los archivos personales de `~/.config/cortex-neo/` se conservan. Consulta
[actualización y desinstalación](docs/es/getting-started/updates-and-uninstall.md).
El [recorrido desde ZIP y la identidad instalada](docs/es/getting-started/version-and-zip.md)
permiten actualizar sin un clon ni sobrescribir el entorno activo.

## Herramientas para trabajar y diagnosticar

| Necesidad | Comando / guía |
|---|---|
| Paletas, contraste, tarjetas y perfiles | `configure` · [Configuración](docs/es/getting-started/configuration.md) |
| Medir el coste del dashboard | `performance` · [Rendimiento](docs/es/guides/performance.md) |
| Entender RAM, swap, presión y memoria compartida | `memory` · [Memoria](docs/es/guides/memory.md) |
| Ver servicios por motor y proyecto Compose | `containers` · [Docker](docs/es/guides/docker-projects.md) |
| Conservar un episodio de lentitud | `incident` · [Incidentes](docs/es/guides/incidents.md) |
| Consultar agregados de varias horas | `history` · [Historial](docs/es/guides/history.md) |
| Medir una suite o compilación explícita | `run` / `tasks` · [Tareas](docs/es/guides/tasks.md) |
| Dar contexto seleccionado a un agente | `context` · [Ficha](docs/es/guides/agent-context.md) |
| Comparar herramientas, kernel y drivers | `baseline-save` / `compare` · [Referencias](docs/es/guides/baselines.md) |
| Ocultar campos al grabar o preparar soporte | `presentation` / `report` · [Compartir](docs/es/guides/sharing.md) |

Son controles locales y optativos. Las consultas usan datos observados y
explican ausencias, cadencias y límites; no deducen causas de una lentitud ni
administran automáticamente procesos, contenedores o equipos remotos.

## Adaptación y equipos comprobados

La disposición usa el área útil del monitor, excluye dock y barra superior, y
escala juntas fuentes, gráficas, iconos y márgenes. CPU/RAM y GPU/discos comparten
alturas; el calendario completa el borde inferior de su columna. También existe
una disposición para pantallas verticales, validada mediante cálculo de geometría.

| Equipo | CPU / RAM | GPU | Pantalla | Sistema comprobado |
|---|---|---|---|---|
| Ryzen de escritorio | Ryzen 7 5700X, 64 GB DDR4 | RTX 4060 Ti 8 GB | 2560 × 1440, escalado 166,67 % | Ubuntu 26.04.1 LTS, GNOME Wayland |
| Dell Latitude 5420 | Core i5-1135G7, 16 GB DDR4 | Intel Iris Xe | 1920 × 1080, escalado 125 % | Ubuntu 26.04.1 LTS, GNOME Wayland |

El soporte de sensores depende del kernel, driver y permisos. El backend DRM
incluye detección AMD, pero aún no se ha validado en un equipo AMD real.
[Compatibilidad comprobada y experimental](docs/es/reference/compatibility.md).
[Resultados y límites de la validación](docs/es/validation/testing.md).

## Privacidad y configuración

La ubicación del clima es una **excepción manual**: no se obtiene de GeoIP, GPS,
GeoClue ni identificadores Wi-Fi. Solo se envían al proveedor las coordenadas de
ciudad que configures. Open-Meteo recibe la petición meteorológica y su conexión
de red ordinaria; esto no equivale a ocultar tu IP ante ese proveedor.

Preferencias, cachés, capturas y respaldos de cada equipo se guardan fuera del
código mediante rutas XDG. El repositorio incluye ejemplos vacíos de ubicación.
[Datos, ubicación y capturas](docs/es/reference/privacy.md).

## Estructura

```text
cortex_neo/             Recolección, inventario, geometría y supervisión
theme/cards/            Una plantilla por tarjeta
theme/*.lua             Presentación, calendario y bloques opcionales
config/                 Ejemplos editables, sin ubicación personal
systemd/                Servicios de usuario
scripts/                Instalación y comprobaciones
tests/                  Casos de ausencia, error y portabilidad
docs/                   Uso, arquitectura, privacidad y validación
assets/screenshots/     Capturas documentales de los dos equipos
.github/                Integración continua y plantillas
```

Para modificar el tema o contribuir: [CONTRIBUTING.md](CONTRIBUTING.md).
Las decisiones de diseño se explican en [la arquitectura](docs/es/reference/architecture.md).

## Autoría y licencia

Creado por **[Jorge Hernández Montero · JorgeTato99](https://github.com/JorgeTato99)**.

El código de CORTEX NEO se distribuye bajo la [licencia MIT](LICENSE). Puedes
usarlo, modificarlo y redistribuirlo conservando el aviso de copyright y la licencia.
Los componentes y recursos de terceros conservan sus propias licencias;
consulta [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Personalización de v0.1.0

```bash
cortex-neo configure --language es --palette blue --font ubuntu
cortex-neo configure --detail-level essential
```

Paletas completas: blue, teal, green, yellow, orange, red, pink, purple, slate y brown. Fuentes: ubuntu, dejavu y liberation, con comprobación y fallback. `essential` oculta información secundaria; `full` la restaura, independientemente de perfil y densidad. La documentación principal ahora es inglesa y el español permanece completo en [docs/es](docs/es/README.md). [Changelog español](CHANGELOG.es.md).
