# Entender la memoria

```bash
cortex-neo memory
cortex-neo memory --pid 1234 --pid 5678
```

La tarjeta muestra usada/total y disponible. La caché y los buffers se conservan
como contadores separados en el snapshot y en el comando; no son cantidades que
se deban sumar a disponible para reconstruir el total. Linux puede recuperar
parte de esas páginas. Swap ocupada tampoco demuestra por sí sola presión actual.

PSI expresa tiempo de espera por memoria. Cero es una lectura válida; un guion
significa que no se pudo obtener el contador. Una media PSI positiva acredita
esperas observadas, no identifica automáticamente al proceso responsable ni
demuestra fuga. Se incluyen medias de 10/60/300 s y actividad de swap entre
muestras; la primera muestra no inventa una tasa.

Los tops usan RSS agrupada, que incluye páginas compartidas. Los procesos QEMU
se marcan `[VM]`: esa memoria pertenece al proceso del invitado desde el host.
No se identifica toda instancia QEMU como Docker Desktop. La VM y los
contenedores que viven dentro de ella no son sumandos independientes del host.

PSS distribuye páginas compartidas entre procesos; USS refleja páginas privadas.
Se consultan solo con PIDs explícitos y como máximo cinco por llamada. La lectura
puede ser más lenta o estar denegada; en esos casos se conserva el estado en vez
de presentar ceros. El muestreo de dos segundos no recorre smaps.

Fuentes: [PSI del kernel](https://docs.kernel.org/accounting/psi.html),
[RSS/PSS en proc](https://www.kernel.org/doc/html/latest/filesystems/proc.html) y
[la VM de Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/).
