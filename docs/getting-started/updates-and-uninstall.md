# Actualización, recuperación y desinstalación

## Actualizar

Descarga y extrae una nueva copia del código en una carpeta distinta y ejecuta
el mismo comando de instalación desde ella. No es necesario tener un clon Git:

```bash
bash scripts/install.sh
```

Si usas Git, selecciona el estado deseado con tu flujo habitual antes de
instalar. Comprueba después `cortex-neo version`; consulta
[identidad y actualización desde ZIP](version-and-zip.md).

En un equipo cuyas dependencias ya están preparadas puedes usar
`bash scripts/install.sh --skip-system-deps`.

Primero se copia la versión a una carpeta nueva y se construye allí su entorno
virtual. Las rutas de los entornos no se renombran: los ejecutables instalados
por pip conservan sus rutas válidas. Solo después de verificar las dependencias
se detienen los servicios del tema y se cambia el enlace de la versión activa.

La configuración existente no se sobrescribe. Antes de activar se respaldan
las preferencias y los accesos/unidades previos. Si falla la activación se
recuperan la versión anterior, su entorno y los controles anteriores. Se intenta
arrancar de nuevo el servicio que estaba activo. Un fallo de energía o del propio
gestor de servicios puede requerir recuperación manual; el respaldo no sustituye
una copia externa de tus datos.

## Rutas administradas

| Contenido | Ruta predeterminada |
|---|---|
| Enlace a la versión activa | `~/.local/share/cortex-neo` |
| Código y entorno de cada versión | `~/.local/share/cortex-neo-releases/<id>/` |
| Preferencias y ciudad | `~/.config/cortex-neo/` |
| Métricas e históricos | `~/.cache/cortex-neo/` |
| Respaldos y capturas | `~/.local/state/cortex-neo/` |

Se respetan las variables XDG absolutas correspondientes. Los comandos del
usuario permanecen en `~/.local/bin/`. Al actualizar una instalación anterior
basada en una carpeta, esta se conserva como versión `legacy-<id>`.

Los respaldos de controles y configuración están en `backups/<id>` dentro de la
ruta de estado. La versión activa incluye `installation.json`, que registra la
versión previa y el respaldo. No se borran automáticamente versiones anteriores
durante las actualizaciones.

## Desinstalar

```bash
cortex-neo uninstall
```

También se puede usar `bash scripts/install.sh --uninstall` desde el código.
Se detienen únicamente los dos servicios del tema y se eliminan los accesos y
versiones administrados. Los accesos modificados por el usuario se conservan y
se indican en la salida. **Configuración, caché y respaldos se conservan**.

No se desinstalan Conky, las fuentes ni otros paquetes compartidos del SO.
Una instalación antigua sin marcador debe actualizarse primero para poder usar
esta desinstalación. No hay una opción de purga automática de datos personales.
