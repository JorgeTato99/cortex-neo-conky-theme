# Pruebas y límites

La suite combina lógica pura, callbacks Lua reales, transacciones de archivos,
datos sintéticos de hardware y pruebas de instalación/renderizado. La evidencia
histórica de los primeros equipos se conserva en [validación inicial](initial-1.1.0.md).

## Comprobaciones rápidas

```bash
bash scripts/check.sh
```

La suite unittest se complementa con pruebas de integración por distribución y
particiones parametrizadas de pantalla. El runner informa el conteo vigente.

Se comprueban Ruff, formato Python/Lua, sintaxis Bash, enlaces locales de Markdown
y la suite unittest. La CI usa Python 3.11–3.15. Un trabajo separado ejecuta la
suite en ARM64 nativo, sin afirmar que tenga los sensores de una placa física.

Las pruebas de instalación usan un hogar temporal real. Solo se reemplaza el
lanzamiento de procesos externos para inyectar fallos. Cubren instalación limpia,
reinstalación, fallo de preparación, fallo de activación, fallo del cambio atómico,
preservación del entorno anterior, migración, desinstalación, rutas XDG y rechazo
de enlaces ajenos. Estas pruebas no son evidencia de apt o systemd reales.

Los fixtures de AMD/Intel/NVIDIA y discos cifrados son datos sintéticos, sin
identificadores de equipos personales. Se incluyen sensores ausentes y permisos
denegados. La geometría se verifica para combinaciones de tarjetas opcionales,
calendarios de cuatro a seis semanas, escritorios desplazados, verticales y
escalados. Las dimensiones lógicas no acreditan por sí solas legibilidad física.

Los contratos de las herramientas locales cubren preferencias persistentes,
perfiles, exportación de contexto, memoria/PSI, Docker por contexto, captura de
incidentes y agregados históricos. Se comprueban ausencias, límites, errores de
escritura, identidad de procesos y exclusión de datos privados.
Se añaden referencias concurrentes sin sobrescritura, cancelación de tareas sin
afectar procesos ajenos, indicadores de presentación corruptos y lectura directa
desde Lua, e identidad de código con archivos desconocidos o modificados.

## Instalaciones desde cero

El driver siguiente solo funciona como root dentro de un contenedor desechable
con la variable explícita de prueba. No se debe ejecutar para preparar un host.

```bash
docker run --rm -e CORTEX_NEO_TEST_CONTAINER=1 \
  -v "$PWD:/source:ro" ubuntu:24.04 \
  bash -c 'cp -a /source /tmp/project && cd /tmp/project && bash scripts/check_distribution.sh'
```

Se ejecuta para Ubuntu 24.04, Ubuntu 26.04, Debian 12 y Debian 13. El driver crea
un usuario de prueba, instala dependencias mediante el instalador normal,
comprueba imports reales, ejecuta la suite, reinstala conservando una preferencia,
renderiza con Conky en Xvfb y desinstala conservando los datos personales.
También analiza las unidades generadas con `systemd-analyze --user verify`,
sin sustituir ese parser por un comando simulado.

Xvfb utiliza Openbox y un compositor dentro del contenedor. Se comprueban nueve
procesos Conky vivos, píxeles distintos del fondo, contenido en cada tarjeta y
ausencia de errores Lua/configuración. Se guarda una imagen de diagnóstico en
`artifacts/distribution-render.png`, que no se versiona y se adjunta a la ejecución
de GitHub Actions durante siete días. No se capturan pantallas
del usuario durante estas pruebas.

## Sesión gráfica real

```bash
cortex-neo doctor
python_del_entorno -I scripts/check_desktop.py
```

El último comando se ejecuta desde el código de la instalación y comprueba
ventanas, alineación, límites, servicios y datos recientes. Las
[capturas reales](screenshots.md) tienen su propia resolución y escalado documentados.

Los contenedores no arrancan una sesión GNOME Wayland completa ni verifican
drivers físicos o sus portales. Los contratos con comandos sustituidos tampoco
acreditan una recuperación real frente a corte de corriente. Se distinguen estas
capas en la [matriz de compatibilidad](../reference/compatibility.md).
