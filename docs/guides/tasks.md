# Medir una tarea de desarrollo

Desde la carpeta de tu proyecto:

```bash
cortex-neo run --label backend-tests -- npm test
cortex-neo run --label rust-tests --timeout 900 -- cargo test
cortex-neo tasks
cortex-neo tasks --format json
```

`run` ejecuta los argumentos como programa, sin una shell intermediaria. Conserva
la salida normal del comando y su código de salida; el resumen de CÓRTEX aparece
en stderr. Para una operación de shell, invoca explícitamente la shell deseada.
No se modifica la carpeta de trabajo ni se añaden instaladores o comandos extra.

El registro privado conserva etiqueta, duración, resultado, CPU observada y pico
RSS del árbol de procesos. No guarda el comando, sus argumentos, la carpeta,
variables de entorno, stdout ni stderr. El muestreo opt-in es de 0,2 segundos y
se limita a los procesos de esa tarea; se siguen como máximo 4096 identidades
PID+nacimiento. Sin observaciones los recursos quedan nulos, no en cero.

Los recursos son observados, no una medición exhaustiva: pueden perderse picos
y descendientes muy breves o desacoplados. RSS incluye páginas compartidas.
Una tarea de Docker puede hacer trabajo en un daemon ajeno a ese árbol y ese
trabajo no queda atribuido íntegramente al cliente. Compara ejecuciones con la
misma etiqueta y condiciones; diferencias aisladas no demuestran regresión.

Sin `--timeout`, el comando conserva su duración natural. Un timeout admite
0,1 segundos a siete días y devuelve 124; Ctrl+C devuelve 130. La cancelación
señala únicamente el grupo creado y las identidades propias verificadas, intenta
terminación y después fuerza el cierre si es necesario. El registro indica si
quedaron descendientes conocidos. No es un sandbox ni un límite de CPU/RAM.
Si faltan permisos o un descendiente se desacopla, el cierre puede quedar
incompleto; se informa y no se elevan privilegios automáticamente.

Se conservan diez registros propios en `~/.local/state/cortex-neo/tasks/`, con
publicación atómica y permisos privados. Un fallo de lanzamiento también queda
registrado, con 127 para programa ausente y 126 para permisos insuficientes.
