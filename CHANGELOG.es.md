<!-- markdownlint-disable MD013 MD024 -->
# Changelog

Todos los cambios notables se documentan aquí. El formato sigue [Keep a Changelog 1.1.0](https://keepachangelog.com/es-ES/1.1.0/) y [Versionado Semántico 2.0.0](https://semver.org/lang/es/spec/v2.0.0.html).

[English](CHANGELOG.md)

## 📖 Guía de uso

### Cómo documentar cambios

Añade cambios relevantes para usuarios en **[Unreleased]** mientras trabajas. Agrupa entradas relacionadas, explica qué cambió y por qué, enlaza evidencia y escribe para personas. Evita listar commits o cambios internos sin impacto. Marca incompatibilidades y explica su migración.

| Categoría estándar | Significado |
|---|---|
| ✨ Added | Nueva funcionalidad |
| 🔄 Changed | Cambios en comportamiento existente |
| ⚠️ Deprecated | Disponible pero prevista para eliminación |
| 🗑️ Removed | Funcionalidad eliminada |
| 🐛 Fixed | Corrección de comportamiento incorrecto |
| 🔒 Security | Correcciones de vulnerabilidades |

Documentation y Testing pueden explicar soporte o evidencia relevante. Omite categorías vacías de las versiones reales.

### Cuándo publicar

Mueve las entradas a `[X.Y.Z] - YYYY-MM-DD - Título descriptivo` con fecha ISO. Durante desarrollo inicial, `0.Y.0` incorpora funciones importantes o incompatibilidades deliberadas; `0.y.Z` corrige errores o mejoras pequeñas compatibles. Explica las incompatibilidades incluso antes de 1.0.0. Una interfaz estable, núcleo completo, documentación mantenida y verificación suficiente permiten llegar a 1.0.0. A partir de entonces MAJOR rompe compatibilidad, MINOR agrega funciones compatibles y PATCH corrige comportamiento compatible.

Ejemplo: una capacidad completa nueva puede ir en 0.2.0; corregir valores obsoletos, en 0.1.1. El formato por sí solo no justifica una versión.

## [Unreleased]

### 📚 Documentation

- Generar los README inglés y español desde una estructura común, con comprobaciones de CI contra divergencias de traducción/estructura.
- Renovar los dos ejemplos nativos y añadir una galería separada de diez paletas con capturas actuales de GNOME, resolución/escalado documentados y compresión WebP sin pérdida verificada.

## [0.1.0] - 2026-10-25 - Lanzamiento internacional

### 🎯 Resumen

**Tipo de release:** primera versión del repositorio renombrado. El historial anterior queda preservado localmente; esta nueva secuencia conserva sus funciones terminadas.

### ✨ Added

- Diez paletas completas inspiradas en los acentos de Ubuntu 26: texto, colores principales/secundarios, metadatos, bordes, advertencias, gráficas y fondo.
- Inglés predeterminado, español completo en catálogos de interfaz/controles y documentación paralela en una sola rama.
- Tres perfiles monoespaciados configurables con comprobación y sustitución segura.
- Detalle esencial/completo independiente del perfil: conserva datos principales, gráficas y procesos; permite ocultar especificaciones y builds.
- Tarjetas adaptables independientes para SO, CPU, RAM, GPU, discos montados/sin montar, red/Docker, software, calendario y clima de ciudad manual.
- Herramientas locales acotadas: coste del tema, presión de memoria, Compose, incidentes antes/después, agregados por minuto, comandos medidos, contexto seleccionado, referencias y comparación.
- Presentación temporal e informes con campos permitidos para compartir tras revisión local.
- Instalación transaccional única, entornos inmutables, revisión/huella de fuentes, actualización/desinstalación segura y preservación de preferencias.

### 🔄 Changed

- Marca **CORTEX NEO** y repositorio **cortex-neo-conky-theme**. CLI, servicios y rutas XDG `cortex-neo` estables para actualizar.
- Documentación principal inglesa; español en `docs/es/` y `README.es.md`. Nombres antiguos de paleta conservados para migración.

### 🐛 Fixed

- Los metadatos disponibles del SO se conservan en modo completo aunque falte el hostname.

### 📚 Documentation

- Guías bilingües de instalación, apariencia, ciclo de vida, diagnóstico, arquitectura, privacidad, compatibilidad y contribución.
- Procedencia de capturas, resolución/escalado y compresión sin pérdida explícitos.

### 🧪 Testing

- Python 3.11–3.15, callbacks Lua reales, lógica ARM64 nativa, cuatro distribuciones limpias con instalación/render y despliegues Ryzen/Dell.
- Regresiones de paletas, fuentes, detalle esencial, placeholders, preservación y capacidades opcionales acotadas.
- Evidencia sintética y física diferenciada; no se afirma compatibilidad universal de controladores/compositores.

[Unreleased]: https://github.com/JorgeTato99/cortex-neo-conky-theme/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/JorgeTato99/cortex-neo-conky-theme/releases/tag/v0.1.0

<!-- ============================================================ -->
<!-- PLANTILLA PARA NUEVAS VERSIONES — copiar al preparar release   -->
<!-- ============================================================ -->
<!--
## [X.Y.Z] - YYYY-MM-DD - 📌 TÍTULO DESCRIPTIVO

### 🎯 Resumen
**Tipo de release:** Función / Corrección / Mejora
Propósito y notas de migración.

### ✨ Added
#### Nombre de la función
Descripción y documentación; explica comportamiento observable.

### 🐛 Fixed
#### Comportamiento corregido
**Problema:** síntoma, causa e impacto.
**Solución:** comportamiento resultante.

### 🔄 Changed
- Describe cambios y marca incompatibilidades.

### 📚 Documentation
| Documento | Cambio |
|---|---|
| docs/es/README.md | Describe el cambio para usuarios |

### 🧪 Testing
**Verificación:** comandos, escenarios y resultados.

**Archivos modificados:**
| Ruta | Líneas | Descripción |
|---|---|---|
| ruta/fuente | +X/-Y | Describe el cambio |
-->
