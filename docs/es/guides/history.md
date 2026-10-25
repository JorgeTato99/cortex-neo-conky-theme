# Historial de varias horas

```bash
cortex-neo history
cortex-neo history --hours 6 --format json
cortex-neo configure --history-hours 24
cortex-neo configure --history-hours 0
```

Se guardan agregados numéricos por minuto: número de observaciones, mínimo,
máximo y promedio para CPU, RAM, GPU/VRAM, memoria disponible, swap, presión y
tráfico. No hay nombres de procesos, argumentos, hostnames, ubicaciones ni
identidades de discos en este historial. Las unidades de CPU/RAM/GPU/VRAM/PSI
son porcentajes; disponible/swap son bytes y tráfico es bytes por segundo.

La retención predeterminada es de 24 horas; admite 1–168 horas o cero para
desactivar nuevas observaciones. Se aplica al recibir muestras, redondeando al
minuto e incluyendo el minuto actual. Desactivar no borra los datos existentes.
Si el programa está detenido no hay un servicio adicional que borre archivos.
Un cambio de configuración se detecta en unos treinta segundos.

El archivo privado está en `~/.local/state/cortex-neo/history/minutes.json`.
Se publica al cambiar de minuto o tras unos sesenta segundos, y durante una
parada normal. Puede quedar hasta un minuto en memoria si se corta la energía.
Un error de escritura conserva agregados acotados en RAM y no detiene las
métricas; `write_failed` permite distinguirlo. Los reintentos tienen espera.

Las observaciones no disponibles no se convierten en cero. Cada magnitud tiene
su propio conteo; sin observaciones su promedio es nulo. Los minutos ausentes
son huecos, no intervalos de inactividad. Muestras repetidas o regresivas se
ignoran; el contador de regresiones ayuda a detectar ajustes del reloj.

La salida de texto resume los últimos veinte minutos observados con fecha local.
JSON incluye todos los minutos seleccionados y sus extremos. Pedir más horas
no recupera datos que nunca se conservaron. Las gráficas del escritorio mantienen
su ventana corta de dos segundos; la consulta histórica no aumenta su coste.
