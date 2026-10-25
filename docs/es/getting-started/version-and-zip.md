# Identificar la instalación y actualizar desde ZIP

```bash
cortex-neo version
cortex-neo version --format json
```

La versión procede de `pyproject.toml`. La revisión se obtiene del checkout Git
o de los metadatos incluidos en el archivo de código; si no está disponible,
se indica como desconocida. No se deduce por el nombre de la carpeta.

La huella SHA-256 identifica fuentes mantenidas y ejemplos de configuración.
No incluye preferencias personales, venv, paquetes del sistema, capturas ni
históricos. `matches_installed_source` compara esas fuentes con el registro
creado al instalar; nulo significa que no existe una comparación acreditable.
Es identificación local de archivos, no firma del editor ni certificación de
dependencias externas. `source_dirty` puede ser desconocido fuera de un checkout.

## Primera instalación y actualización

1. Descarga el [ZIP del código](https://github.com/JorgeTato99/cortex-neo-conky-theme/archive/refs/heads/main.zip).
2. Extráelo en una carpeta nueva; no encima del entorno instalado.
3. Abre una terminal en esa carpeta y ejecuta:

```bash
bash scripts/install.sh
```

4. Comprueba la identidad y el diagnóstico:

```bash
~/.local/bin/cortex-neo version
~/.local/bin/cortex-neo doctor
```

No hace falta convertir el ZIP en un clon. Si trabajas con Git, selecciona el
estado que quieras mediante tu flujo habitual y ejecuta el instalador desde él.
La configuración XDG existente se conserva. Consulta [mantenimiento](updates-and-uninstall.md)
para respaldos, recuperación y desinstalación.

La rama `main` puede avanzar. Para reproducir exactamente una instalación,
guarda su revisión y usa un archivo del commit concreto. GitHub permite
[descargar archivos de commits](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives);
la identidad se comprueba sobre los contenidos, no sobre bytes de compresión que
pueden variar. [Git export-subst](https://git-scm.com/docs/gitattributes#_export_subst)
permite incluir la revisión en archivos preparados por Git.
