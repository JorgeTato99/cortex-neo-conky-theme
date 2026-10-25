# Contribuir a CORTEX NEO

El tema se desarrolla en Python y Lua. Mantener comentarios/docstrings en inglés,
documentación principal en inglés y páginas equivalentes en español y texto UTF-8 con LF. Usar cuatro espacios y las
configuraciones de Ruff y StyLua incluidas en el repositorio.

## Entorno de desarrollo

```bash
sudo apt install python3-venv liblua5.4-0
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Instalar [StyLua 2.6.0](https://github.com/JohnnyMorganz/StyLua/releases/tag/v2.6.0)
y dejar `stylua` en el `PATH`. La suite ejecuta los callbacks Lua mediante la
biblioteca compartida; no necesita GPU, escritorio, Docker ni credenciales reales.

```bash
bash scripts/check.sh
```

El workflow ejecuta la suite con Python 3.11–3.15 y en ARM64. Otros trabajos
instalan el proyecto desde cero en cuatro distribuciones y renderizan con Conky
real bajo Xvfb. Esa pantalla virtual no acredita GNOME Wayland ni drivers físicos;
las comprobaciones en equipos reales se documentan por separado.

## Dónde cambiar cada cosa

| Cambio | Archivos |
|---|---|
| Contenido o estilo de tarjetas | `theme/cards/`, `theme/*.lua`, `cortex_neo/render.py` |
| Escala, columnas y alineación | `cortex_neo/layout.py` |
| Sensores e inventario | `cortex_neo/system.py`, `gpu.py`, `telemetry.py` |
| Versiones de programas | `cortex_neo/versions.py` |
| Ciudad manual y caché meteorológica | `cortex_neo/weather.py` |
| Instalación y servicios | `scripts/install.sh`, `scripts/manage_installation.py`, `systemd/` |
| Diagnóstico y capacidades de Conky | `cortex_neo/diagnostics.py`, `cortex_neo/conky.py` |

Consultar [arquitectura](reference/architecture.md) antes de mezclar responsabilidades.
Después de editar fuentes, ejecutar de nuevo el instalador desde el clon para
aplicarlas a `~/.local/share/cortex-neo/` sin sobrescribir las preferencias.

## Reglas de comportamiento

- Ausencia de herramienta o sensor: omitir el dato, sin inventar valores cero.
- No descargar toolchains durante consultas de versión ni bloquear métricas con red.
- Mantener la ciudad exclusivamente manual; no introducir fuentes de geolocalización.
- Limitar recorridos, consultas e históricos; respetar la cadencia de cada fuente.
- Conservar los avisos de copyright y la licencia MIT al reutilizar el código.

Una propuesta debe explicar el problema, el resultado observable y la validación
realizada. Para cambios visuales, incluir capturas y resolución/escala del monitor.
Revisar el contenido de las capturas antes de publicarlas.

Los informes de compatibilidad tienen una plantilla propia. Separar resolución
física, escala del escritorio y escala interna del tema; indicar qué se midió y
qué quedó sin comprobar. `cortex-neo version` identifica las fuentes y `report`
prepara campos seleccionados. No adjuntar snapshots, entornos o registros privados.
La [guía inglesa](../en/usage.md) reúne los comandos públicos; mantenerla junto
a la documentación española cuando cambie una interfaz.

Los contratos de instalación sustituyen solo los comandos externos; ejercitan
las operaciones reales de archivos en un hogar temporal. El fallo de preparación
debe conservar la instalación activa; el de activación debe restaurarla con su
entorno. El driver `check_distribution.sh` solo admite contenedores desechables.
Consulta [pruebas](validation/testing.md) para reproducir cada capa.

Mantén los catálogos en/es con las mismas claves y placeholders. Actualiza ambas páginas en el mismo cambio y registra lo notable en [Unreleased](../../CHANGELOG.es.md).
