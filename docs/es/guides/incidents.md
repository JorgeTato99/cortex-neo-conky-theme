# Conservar un incidente

```bash
cortex-neo incident --label "lentitud durante pruebas"
cortex-neo incident --label "solo retrospectiva" --after 0
cortex-neo incidents
cortex-neo incident-export --id ID_DEL_INCIDENTE
```

La captura es voluntaria. Conserva hasta cuatro minutos previos y un minuto
posterior; `--before` admite 0–240 s y `--after` 0–60 s. La CLI espera la ventana
posterior y se puede interrumpir con Ctrl+C para guardar lo disponible. El
dashboard sigue funcionando: la herramienta lee su caché, sin otro recolector.

Cada muestra incluye métricas y tops resumidos. No hay argumentos, entornos ni
contenido de archivos. Los nombres de procesos y la etiqueta permanecen en el
registro privado de `~/.local/state/cortex-neo/incidents/`; los archivos se crean
con permisos privados. Se conservan diez incidentes, de hasta doscientas muestras,
y solo se eliminan registros propios con identificador y marcador válidos.
Las escrituras concurrentes se serializan; un archivo incompleto no se publica.

La ventana previa depende del tiempo que lleve activo el recolector. No se
inventan muestras ni ceros para huecos. `gaps` señala saltos superiores a 4,5 s;
`no_data` e `interrupted` distinguen esos resultados de una captura completa.
El tiempo de espera usa reloj monotónico para evitar esperas indefinidas por
ajustes del reloj del sistema.

`incident-export` imprime únicamente tiempos y métricas seleccionadas. Omite
etiquetas, nombres/PID de procesos e identidades de discos. No envía nada: revisa
la salida antes de compartirla. Coincidencias temporales no demuestran causas.
CPU global usa el total del equipo; el top CPU conserva porcentaje por núcleo y
la memoria de procesos es RSS, que incluye páginas compartidas.
