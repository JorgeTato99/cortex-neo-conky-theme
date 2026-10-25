# Presentar y compartir con menos exposición

```bash
cortex-neo presentation --on
cortex-neo presentation
cortex-neo presentation --off
cortex-neo presentation --on --minutes 30
cortex-neo report
cortex-neo report --format json
```

El modo presentación oculta hostname, tops de procesos/aplicaciones, rutas de
montaje, interfaz de red y detalles de compilación. La tarjeta meteorológica
desaparece; CPU, RAM, gráficas, hardware y versiones siguen visibles. La cabecera
muestra **Presentación**. Espera ese indicador antes de empezar una grabación.
La CLI espera un ciclo de dibujo al activar o desactivar el modo.

El indicador se guarda solo en el runtime privado del usuario, fuera de las
preferencias persistentes. Reiniciar CÓRTEX no lo desactiva. Sin `--minutes`
continúa hasta desactivarlo o hasta que el sistema retire ese runtime; con linger
puede sobrevivir a un cierre de sesión. Así no reaparecen datos por un plazo
inesperado. Un vencimiento automático de 1–480 minutos requiere opción explícita.

Los lectores comprueban el indicador directamente, incluso si el recolector
se detuvo. Un indicador corrupto o ilegible conserva el ocultamiento hasta
corregirlo o quitarlo. No hay scripts ejecutables dentro del indicador.

El modo afecta al dashboard. No protege otras ventanas, terminales, archivos,
grabaciones anteriores ni registros privados ya conservados. El recolector
sigue trabajando y el proveedor del clima mantiene su cadencia habitual.
Hardware y versiones también pueden identificar un entorno: no es anonimización
completa del equipo.

`report` imprime una vista previa local con campos seleccionados: contexto,
dimensiones lógicas, escala interna y estados de diagnóstico. No incluye raw
snapshots, hostname, rutas, procesos, proyectos, ciudad, detalles de error ni
variables de entorno. No toma capturas ni envía o publica el informe. Puedes
revisarlo y después redirigirlo a un archivo que elijas. Para un entorno sin
sesión gráfica existe `report --dependencies-only`.
