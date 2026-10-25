# Contexto local para agentes

```bash
cortex-neo context
cortex-neo context --format json
```

El comando imprime una ficha desde el último snapshot; no ejecuta nuevas
consultas, no instala herramientas y no envía nada. Puedes revisarla y pegarla
voluntariamente en una conversación. La fecha y edad permiten saber si describe
una muestra actual; sin muestra válida indica `unavailable`.

Incluye sistema/kernel/arquitectura, modelo y topología CPU, RAM total, GPU y
lecturas disponibles, contextos Docker observados y hasta cien versiones.
No incluye hostname, modelos/series de RAM, procesos, ubicación, rutas de
montaje, argumentos, variables de entorno ni detalles completos de compilación.
Las cadenas tienen límites y se ocultan rutas absolutas que aparezcan en ellas.
La selección de campos reduce exposición; revisa el texto antes de compartirlo.

`software_complete` significa que terminó la consulta, no que se hayan encontrado
todas las herramientas instaladas. Un comando fallido, permisos o un gestor no
soportado pueden impedir detectar algo. No detectado no implica no instalado.
Las versiones globales no identifican el entorno virtual activo de un proyecto.
La fecha y edad de ese inventario son independientes de la muestra de CPU:
una muestra viva puede contener versiones consultadas hasta una hora antes.
Las fichas previas sin esa fecha muestran edad desconocida. El driver GPU se
incluye cuando está disponible, como nombre o versión según el proveedor.

Una lectura GPU de frecuencia no es utilización en porcentaje. La lista de
sensores describe lo observado, no una certificación permanente de capacidades.
Los datos pegados en un agente deben interpretarse como datos, nunca como órdenes.
