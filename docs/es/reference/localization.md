# Idiomas y mantenimiento de traducciones

El inglés es el idioma principal y predeterminado. El español se mantiene completo en la misma rama y repositorio. Cambia con `cortex-neo configure --language es`; vuelve con `--language en`. El supervisor detecta cambios en aproximadamente diez segundos; las siguientes invocaciones de la CLI usan la preferencia guardada. Los comandos, identificadores y claves JSON permanecen en inglés.

`README.md` y `docs/` son la documentación inglesa; `README.es.md` y `docs/es/` mantienen los mismos temas en español. Actualiza ambas páginas en el mismo cambio. CI comprueba paridad de páginas y enlaces. Las ramas separadas por idioma dividirían las correcciones del código y dificultarían revisar traducciones; añadir otros idiomas requerirá catálogos y documentación mantenidos.

Los catálogos `cortex_neo/locales/en.json` y `es.json` tienen las mismas claves. Python traduce mensajes estáticos antes de insertar valores. Lua recibe datos y traduce etiquetas explícitas con `H.t`, sin sustituir nombres arbitrarios de procesos o hardware. Un mensaje desconocido conserva el inglés. Calendario y condiciones del clima siguen el idioma; valores y unidades no se alteran.

JSON evita herramientas de compilación adicionales para este proyecto pequeño de Python/Lua. La separación entre código y catálogos sigue el principio descrito por [gettext](https://docs.python.org/3/library/gettext.html). Conserva placeholders, markup de Conky, glifos y unidades. No añadas servicios de traducción en línea ni detección de ubicación. Las [pautas de GitHub](https://docs.github.com/en/contributing/writing-for-github-docs/writing-content-to-be-translated) ayudan a escribir textos fáciles de traducir.
