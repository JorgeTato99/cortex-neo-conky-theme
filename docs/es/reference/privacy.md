# Datos, ubicación y capturas

## Qué se lee

El tema consulta métricas del equipo: modelos de hardware, capacidad y sensores,
nombre del host, procesos, rutas de montaje, interfaz de red, versiones instaladas
y el estado de endpoints Docker locales. La marca/modelo de RAM puede requerir
`sudo -n dmidecode`; si no está permitido, se omite sin pedir contraseña.

El recolector guarda snapshots e históricos en `~/.cache/cortex-neo/`. No son
archivos destinados a Git ni deben adjuntarse enteros a un reporte público.
Las preferencias de ubicación y pantalla viven en `~/.config/cortex-neo/`.

Los agregados numéricos por minuto se guardan en la ruta de estado XDG, con
retención predeterminada de 24 horas. No incluyen procesos ni identidades del
equipo. Las capturas de incidentes son explícitas y sí pueden conservar nombres
de procesos y etiquetas privadas; su exportación selecciona solo métricas.
Consulta [historial](../guides/history.md) e [incidentes](../guides/incidents.md)
para las ventanas, cadencias y límites de retención.

La medición de [tareas](../guides/tasks.md) es explícita. Sus registros guardan
etiqueta y métricas, pero no argumentos, entorno, carpeta ni salida del comando.
Las etiquetas y nombres de proyectos que introduzcas siguen siendo datos locales
que conviene revisar antes de compartir.

El [modo presentación](../guides/sharing.md) oculta campos del dashboard mediante
un indicador temporal. No detiene el recolector ni elimina registros privados.
Los informes de soporte seleccionan campos y omiten diagnósticos sin filtrar;
se imprimen para revisión, sin enviarse automáticamente.

## Ubicación exclusivamente manual

`config/location.example.json` empieza sin ciudad ni coordenadas. Copiarlo o
editar `~/.config/cortex-neo/location.json` con `mode: "manual_city"` y coordenadas
públicas del centro de una ciudad. No configurar una dirección doméstica precisa.

**No añadir GeoIP, GPS, GeoClue, SSID/BSSID, escaneos de redes ni otro mecanismo
automático como fuente o fallback de ubicación.** Sin configuración manual válida,
no hay consulta meteorológica ni tarjeta de clima.

Open-Meteo recibe las coordenadas configuradas y la conexión de red ordinaria de
esa petición. La protección consiste en no inferir ni recopilar automáticamente
la ubicación del equipo; no se promete anonimato de red ante el proveedor.

## Publicar capturas

El portal de GNOME puede solicitar autorización de la sesión aunque el usuario
tenga `sudo`. Las capturas se guardan en `~/.local/state/cortex-neo/`.

Una captura puede mostrar hostname, procesos, ubicación de ciudad, versiones y
contenido de otras ventanas. Las imágenes de `assets/screenshots/` fueron tomadas
con ambos escritorios despejados y autorizadas para documentar este repositorio.

Los ejemplos versionados no incluyen la configuración personal, claves SSH/LUKS,
tokens, endpoints remotos ni respaldos administrativos de los equipos.

Los ejemplos y la galería publicados usan capturas nativas autorizadas. Los artefactos de render de CI usan fixtures sintéticos y se mantienen separados de esas imágenes.
