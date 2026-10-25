# Referencias y comparación explícita

```bash
cortex-neo baseline-save --name frontend-validado
cortex-neo baselines
cortex-neo compare --name frontend-validado
cortex-neo baseline-export --name frontend-validado > ~/frontend-context.json
cortex-neo compare --input ~/otro-equipo-context.json
cortex-neo baseline-remove --name frontend-validado
```

Una referencia conserva la ficha seleccionada de contexto: sistema/kernel,
arquitectura, CPU/RAM, modelo/driver GPU, sensores observados, contextos Docker
y versiones detectadas. No contiene hostname, procesos, ubicación ni rutas de
proyectos. El nombre que elijas sí puede ser privado; no forma parte de la
ficha exportada. El driver puede ser una versión o el nombre del módulo según
lo que exponga su proveedor.

No se sobrescriben nombres, ni siquiera cambiando mayúsculas. Hay espacio para
veinte referencias; al alcanzar el límite hay que exportar o quitar una
explícitamente. No se purgan automáticamente referencias anteriores. Los
registros privados viven en `~/.local/state/cortex-neo/baselines/`.

Para comparar dos equipos, exporta `cortex-neo context --format json` en uno,
copia tú el archivo al otro y usa `compare --input`. No hay descubrimiento,
sincronización ni conexiones nuevas. También se puede guardar una ficha
importada mediante `baseline-save --name NOMBRE --input ARCHIVO`.

Se admiten fichas versión uno, JSON de hasta 1 MiB y solo campos seleccionados.
Se comparan observaciones, no instalaciones completas. Un inventario parcial
produce `partial_inventory`; una versión ausente no demuestra eliminación.
La fecha del inventario de software se conserva separada de la muestra de CPU.
Las fichas antiguas que no la incluyen indican edad desconocida.

Una coincidencia temporal o igualdad de versiones globales no demuestra causa
de un fallo ni igualdad de dependencias/entornos activos de cada proyecto.
