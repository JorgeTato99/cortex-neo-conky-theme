# Instalación

Se necesita Linux con escritorio, Python del sistema 3.11 o posterior y systemd
de usuario. Los perfiles de paquetes automáticos cubren Ubuntu 24.04/26.04 y
Debian 12/13. Consulta el alcance real en [compatibilidad](../reference/compatibility.md).

Descarga y descomprime el [ZIP del código](https://github.com/JorgeTato99/cortex-neo-conky-theme/archive/refs/heads/main.zip),
o clónalo si ya tienes Git.
Desde su carpeta ejecuta un único instalador:

```bash
bash scripts/install.sh
```

Ejecuta como tu usuario del escritorio. **No uses `sudo bash scripts/install.sh`.**
El instalador solicita elevación únicamente para `apt-get update` y la instalación
de dependencias. No necesita `sudo` sin contraseña de forma permanente.

Instala Conky con Lua/X11, GTK, fuentes, herramientas de consulta del sistema y
XWayland desde los repositorios de la distribución. No instala Docker, editores,
compiladores ni drivers de GPU. La lectura de datos SMBIOS privilegiados es
opcional; no crea reglas de sudo para conseguirlos.

Se usa `/usr/bin/python3` y un entorno virtual con acceso a los bindings GTK del
sistema. No se sustituye el Python del SO ni se usa el intérprete de pyenv/uv de
los proyectos. Cada versión del tema tiene su propio entorno; una descarga fallida
no modifica el de la instalación que está funcionando.

## Opciones

```bash
bash scripts/install.sh --dry-run
bash scripts/install.sh --skip-system-deps
bash scripts/install.sh --no-start
bash scripts/install.sh --location-file=/ruta/ciudad-manual.json
```

`--dry-run` solo muestra el plan: no ejecuta apt ni crea archivos. Con
`--skip-system-deps` declaras que ya preparaste las dependencias; el diagnóstico
sigue verificándolas. En otras distribuciones este modo es experimental.

`--no-start` instala y habilita para la próxima sesión gráfica, sin necesitar
un gestor de usuario activo. Si ya hay una instalación funcionando, se rechaza
esta opción para evitar sustituir su código sin detenerla de forma ordenada.
Sin esa opción se comprueban los dos servicios al arrancar.

El archivo de ciudad se copia solo si todavía no existe configuración personal.
El instalador no detecta ni consulta ubicación. Al arrancar el tema, este solo
consulta el pronóstico si ya existe una ciudad manual válida.

## Comprobación

```bash
~/.local/bin/cortex-neo doctor
```

Sin escritorio activo usa `doctor --dependencies-only`. Un resultado `warning`
identifica una función opcional o fuente de sustitución; `error` indica un
requisito que debe corregirse. El código de salida es distinto de cero si hay
errores. Las ventanas del tema pertenecen a la sesión gráfica, no al greeter.

Para migrar el antiguo servicio de este proyecto, añade `--migrate-legacy`.
El instalador nunca termina otras instancias Conky por nombre de proceso.
