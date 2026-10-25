# Evidencia comunitaria de compatibilidad

La matriz de [pruebas](testing.md) distingue contratos, renderizado aislado y
sesiones físicas. Un informe de otra persona no amplía automáticamente el
soporte declarado: necesita condiciones, versión y evidencia reproducible.

## Cómo informar

Usa la plantilla «Compatibility report» del repositorio. Incluye distribución,
sesión/escritorio, versión de CORTEX y Conky, resolución física y escalado del
escritorio. La escala interna del tema es un dato distinto. Pega un informe de
soporte revisado y describe qué comprobaste contra otra herramienta.

No publiques snapshots completos, variables de entorno, claves ni registros
privados. Una captura es opcional y puede mostrar datos de otras ventanas;
el modo presentación protege solo los campos reconocidos del dashboard.

## Niveles de evidencia

- **Instalación:** dependencias e importaciones funcionan.
- **Presentación:** tarjetas visibles, sin solapamiento ni recorte en condiciones documentadas.
- **Métricas:** unidades y valores contrastados con una fuente independiente.
- **Recuperación:** comportamiento después de un cambio o fallo descrito.

Cada informe debe indicar lo no comprobado. Fixtures de GPU no son validación
física; Xvfb no equivale a GNOME/KDE ni a sus portales/controladores.

## Registro de informes incorporados

| Fecha / versión o commit | Equipo y entorno | Resolución / escalado | Nivel y evidencia | Limitaciones |
|---|---|---|---|---|
| Sin entradas comunitarias incorporadas en este documento | — | — | — | La evidencia de los dos equipos iniciales está en [capturas](screenshots.md) |

Al incorporar una entrada, enlazar el issue y las condiciones, sin números de
serie ni identificadores personales. Fechar cambios de versión/controlador y
evitar presentar informes antiguos como garantía de compatibilidad actual.
