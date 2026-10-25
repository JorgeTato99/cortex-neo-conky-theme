# Compatibilidad

## Política de Python

El mínimo estándar es **Python 3.11**. La suite de Python/Lua se ejecuta con
3.11, 3.12, 3.13, 3.14 y 3.15. Cada equipo utiliza un solo intérprete: el Python
de su distribución, dentro de un entorno virtual que ve los bindings GTK del SO.
No se instala la versión más reciente a costa de sustituir el intérprete del
sistema. Probar la lógica en 3.15 no acredita GTK de todas las distribuciones
para un Python instalado por separado.

Python 3.10 terminó su soporte upstream el 1 de octubre de 2026. La versión
anterior del proyecto tenía ese mínimo; el instalador nuevo lo rechaza antes
de modificar archivos o paquetes. Esto excluye la instalación estándar de
Ubuntu 22.04 con su Python predeterminado, aunque el proveedor pueda ofrecer
mantenimiento propio del paquete.

## Capas de evidencia

| Entorno | Alcance de la comprobación |
|---|---|
| Ubuntu 26.04.1, GNOME Wayland, Intel y NVIDIA x86_64 | Dos escritorios físicos; las capturas documentan su resultado. |
| Ubuntu 24.04/26.04 y Debian 12/13 | Contratos de instalación/reinstalación/desinstalación y Conky real bajo Xvfb en contenedores limpios. |
| Python 3.11–3.15 | Pruebas de lógica, archivos y callbacks Lua en CI; no equivalen a cinco escritorios reales. |
| Linux ARM64 | Suite Python/Lua en runner nativo de GitHub; no acredita sensores ni composición gráfica de una placa concreta. |
| AMD | Sensores DRM probados con fixtures; todavía sin certificación sobre hardware AMD real. |
| Otros escritorios o distribuciones | Experimental con dependencias manuales; sin promesa de compatibilidad gráfica. |

El instalador admite únicamente los perfiles de paquetes enumerados. Las
pruebas no ejecutan un producto cartesiano de cada versión de Python, SO, GPU
y escritorio; se cubren por capas independientes.

Conky debe incluir **X11 y Lua**, y la sesión Wayland debe disponer de XWayland.
Se seleccionan opciones compatibles con versiones antiguas y modernas del
motor. Las funciones opcionales no convierten herramientas ausentes en errores
en el panel: sin Docker, toolchains, sensores o ciudad no se inventan datos.

## Fuentes de la política

- [Estado de Python](https://devguide.python.org/versions/), consultado el 24-10-2026.
- [Instalación de PyGObject](https://pygobject.gnome.org/getting_started.html).
- [Opciones de Conky](https://conky.cc/config_settings).
- [Runners GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job).
